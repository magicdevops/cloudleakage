#!/usr/bin/env python3
"""
AWS Cost Optimization Tool - Main Flask Application
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import logging
from datetime import datetime
from cryptography.fernet import Fernet
from account_manager import (
    test_aws_credentials, test_iam_role, generate_account_id, perform_account_sync
)
from simple_database import (
    init_database, CloudAccountService, CostDataService
)
from ec2_service import EC2Service
from terraform_analyzer import analyze_state_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Initialize encryption key for credential storage
    encryption_key = os.environ.get('ENCRYPTION_KEY')
    if not encryption_key:
        # Use a fixed key for development to maintain persistence
        # In production, set ENCRYPTION_KEY environment variable
        encryption_key = "oz2fA05GT7jHw-kReDcvXCHc9weUCOM2sBe7bIOQqps="
        logger.warning("Using default encryption key. Set ENCRYPTION_KEY environment variable in production.")
    
    app.config['ENCRYPTION_KEY'] = encryption_key
    app.config['CIPHER_SUITE'] = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
    
    # Initialize database
    database_path = os.environ.get('DATABASE_PATH', 'cloudleakage.db')
    db_manager = init_database(database_path)
    
    # Initialize services
    account_service = CloudAccountService(db_manager, app.config['CIPHER_SUITE'])
    cost_service = CostDataService(db_manager)
    ec2_service = EC2Service(db_manager, app.config['CIPHER_SUITE'])
    
    # Store services in app config for access in routes
    app.config['ACCOUNT_SERVICE'] = account_service
    app.config['COST_SERVICE'] = cost_service
    app.config['EC2_SERVICE'] = ec2_service
    app.config['DB_MANAGER'] = db_manager
    
    # Main dashboard route
    @app.route('/')
    @app.route('/dashboard')
    def dashboard():
        """Main dashboard with cost metrics and recommendations"""
        try:
            # Sample data for demonstration
            dashboard_data = {
                'current_month_cost': 2847.32,
                'last_month_cost': 3156.78,
                'cost_change': -9.8,
                'total_resources': 127,
                'active_alarms': 3,
                'recommendations_count': 8,
                'cost_trend': [2100, 2300, 2500, 2700, 2847],
                'top_services': [
                    {'name': 'EC2', 'cost': 1247.89, 'percentage': 43.8},
                    {'name': 'RDS', 'cost': 623.45, 'percentage': 21.9},
                    {'name': 'S3', 'cost': 345.67, 'percentage': 12.1},
                    {'name': 'Lambda', 'cost': 234.56, 'percentage': 8.2},
                    {'name': 'Others', 'cost': 395.75, 'percentage': 13.9}
                ],
                'recommendations': [
                    {
                        'title': 'Resize Underutilized EC2 Instances',
                        'description': '3 instances running at <20% CPU utilization',
                        'potential_savings': 234.50,
                        'priority': 'high'
                    },
                    {
                        'title': 'Delete Unused EBS Volumes',
                        'description': '5 unattached volumes consuming storage',
                        'potential_savings': 156.30,
                        'priority': 'medium'
                    },
                    {
                        'title': 'Optimize S3 Storage Classes',
                        'description': 'Move infrequently accessed data to IA',
                        'potential_savings': 89.20,
                        'priority': 'low'
                    }
                ]
            }
            return render_template('cloudspend-dashboard.html', data=dashboard_data)
        except Exception as e:
            logger.error(f"Error loading dashboard: {str(e)}")
            return render_template('cloudspend-dashboard.html', data={})

    # Business Units
    @app.route('/business-units')
    def business_units():
        """Business units management page"""
        return render_template('business_units/index.html')

    # Budgets
    @app.route('/budgets')
    def budgets():
        """Budget management page"""
        return render_template('base.html', title='Budgets')

    # Reports
    @app.route('/reports')
    def reports():
        """Reports page"""
        return render_template('base.html', title='Reports')

    # Integration routes
    @app.route('/integration')
    @app.route('/integration/accounts')
    def integration_accounts():
        """Account integration management"""
        return render_template('integration/accounts.html')

    @app.route('/integration/wizard')
    def integration_wizard():
        """Account integration wizard"""
        return render_template('integration/wizard.html')

    @app.route('/integration/api/policy/generate', methods=['POST'])
    def generate_policy():
        """Generate IAM policy for AWS integration"""
        try:
            data = request.get_json()
            provider = data.get('provider', 'aws')
            
            if provider == 'aws':
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "ce:GetCostAndUsage",
                                "ce:GetDimensionValues",
                                "ce:GetReservationCoverage",
                                "ce:GetReservationPurchaseRecommendation",
                                "ce:GetReservationUtilization",
                                "ce:GetSavingsPlansUtilization",
                                "ce:ListCostCategoryDefinitions",
                                "organizations:ListAccounts",
                                "organizations:ListCreateAccountStatus",
                                "organizations:DescribeOrganization",
                                "budgets:ViewBudget"
                            ],
                            "Resource": "*"
                        }
                    ]
                }
                
                return jsonify({
                    'success': True,
                    'policy_json': policy
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Unsupported provider'
                }), 400
                
        except Exception as e:
            logger.error(f"Error generating policy: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500

    @app.route('/integration/api/accounts', methods=['POST'])
    def create_account_integration():
        """Create a new account integration"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['displayName', 'provider', 'accessType']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400
            
            # Validate access type specific fields
            access_type = data.get('accessType')
            if access_type == 'accesskey':
                if not data.get('accessKeyId') or not data.get('secretAccessKey'):
                    return jsonify({
                        'success': False,
                        'error': 'Access Key ID and Secret Access Key are required for access key authentication'
                    }), 400
                
                # Test AWS credentials before storing
                test_result = test_aws_credentials(
                    data.get('accessKeyId'),
                    data.get('secretAccessKey'),
                    data.get('region', 'us-east-1')
                )
                
                if not test_result['valid']:
                    return jsonify({
                        'success': False,
                        'error': f'Invalid AWS credentials: {test_result["error"]}'
                    }), 400
                
                # Store account integration in database
                account_data = {
                    'id': generate_account_id(),
                    'displayName': data.get('displayName'),
                    'provider': data.get('provider'),
                    'accessType': access_type,
                    'credentials': {
                        'accessKeyId': data.get('accessKeyId'),
                        'secretAccessKey': data.get('secretAccessKey'),
                        'region': data.get('region', 'us-east-1')
                    },
                    'status': 'connected',
                    'accountInfo': test_result.get('accountInfo', {}),
                    'billing': data.get('billing', 'yes'),
                    'accountType': data.get('accountType', 'organization'),
                    'exportName': data.get('exportName'),
                    'startDate': data.get('startDate')
                }
                
                # Save using database service
                account_id = app.config['ACCOUNT_SERVICE'].create_account(account_data)
                
                return jsonify({
                    'success': True,
                    'accountId': account_id,
                    'message': 'Account integration created successfully'
                })
            
            elif access_type == 'iam':
                if not data.get('roleArn'):
                    return jsonify({
                        'success': False,
                        'error': 'Role ARN is required for IAM role authentication'
                    }), 400
                
                # Test IAM role access
                test_result = test_iam_role(data.get('roleArn'))
                
                if not test_result['valid']:
                    return jsonify({
                        'success': False,
                        'error': f'Invalid IAM role: {test_result["error"]}'
                    }), 400
                
                # Store IAM role integration
                account_data = {
                    'id': generate_account_id(),
                    'displayName': data.get('displayName'),
                    'provider': data.get('provider'),
                    'accessType': access_type,
                    'roleArn': data.get('roleArn'),
                    'status': 'connected',
                    'accountInfo': test_result.get('accountInfo', {}),
                    'billing': data.get('billing', 'yes'),
                    'accountType': data.get('accountType', 'organization'),
                    'exportName': data.get('exportName'),
                    'startDate': data.get('startDate')
                }
                
                account_id = app.config['ACCOUNT_SERVICE'].create_account(account_data)
                
                return jsonify({
                    'success': True,
                    'accountId': account_id,
                    'message': 'Account integration created successfully'
                })
            
            else:
                return jsonify({
                    'success': False,
                    'error': 'Unsupported access type'
                }), 400
                
        except Exception as e:
            logger.error(f"Error creating account integration: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
    
    @app.route('/integration/api/accounts', methods=['GET'])
    def list_account_integrations():
        """List all account integrations"""
        try:
            accounts = app.config['ACCOUNT_SERVICE'].get_all_accounts()
            
            return jsonify({
                'success': True,
                'accounts': accounts
            })
        except Exception as e:
            logger.error(f"Error listing account integrations: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
    
    @app.route('/integration/api/accounts/<account_id>/sync', methods=['POST'])
    def sync_account_data(account_id):
        """Trigger data sync for a specific account"""
        try:
            account = app.config['ACCOUNT_SERVICE'].get_account_by_id(account_id)
            
            if not account:
                return jsonify({
                    'success': False,
                    'error': 'Account not found'
                }), 404
            
            # Convert database model to dict for compatibility
            account_dict = {
                'id': account.id,
                'accessType': account.access_type,
                'provider': account.provider
            }
            
            # Perform sync
            sync_result = perform_account_sync(account_dict)
            
            if sync_result['success']:
                # Update last sync time in database
                app.config['ACCOUNT_SERVICE'].update_last_sync(account_id)
                
                return jsonify({
                    'success': True,
                    'message': 'Account sync completed successfully',
                    'syncData': sync_result.get('data', {})
                })
            else:
                return jsonify({
                    'success': False,
                    'error': sync_result.get('error', 'Sync failed')
                }), 500
                
        except Exception as e:
            logger.error(f"Error syncing account data: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
    
    @app.route('/integration/api/accounts/<account_id>', methods=['DELETE'])
    def delete_account_integration(account_id):
        """Delete an account integration"""
        try:
            success = app.config['ACCOUNT_SERVICE'].delete_account(account_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Account integration deleted successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Account not found or could not be deleted'
                }), 404
                
        except Exception as e:
            logger.error(f"Error deleting account integration: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500

    # Sync Management
    @app.route('/sync-management')
    def sync_management():
        """Data synchronization management"""
        return render_template('sync_management/dashboard.html')

    # API endpoints
    @app.route('/api/cost-data')
    def api_cost_data():
        """API endpoint for cost data"""
        return jsonify({
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'data': [2100, 2300, 2500, 2700, 2847]
        })

    @app.route('/api/recommendations')
    def api_recommendations():
        """API endpoint for recommendations"""
        recommendations = [
            {
                'id': 1,
                'title': 'Resize Underutilized EC2 Instances',
                'description': '3 instances running at <20% CPU utilization',
                'potential_savings': 234.50,
                'priority': 'high',
                'category': 'compute'
            },
            {
                'id': 2,
                'title': 'Delete Unused EBS Volumes',
                'description': '5 unattached volumes consuming storage',
                'potential_savings': 156.30,
                'priority': 'medium',
                'category': 'storage'
            }
        ]
        return jsonify(recommendations)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('base.html', title='Page Not Found'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('base.html', title='Internal Server Error'), 500

    # EC2 Dashboard Routes
    @app.route('/ec2')
    @app.route('/ec2/dashboard')
    def ec2_dashboard():
        """EC2 instances dashboard"""
        return render_template('ec2/dashboard.html')
    
    @app.route('/ec2/api/accounts/<account_id>/instances')
    def get_ec2_instances(account_id):
        """API endpoint to get EC2 instances for an account"""
        try:
            ec2_service = app.config['EC2_SERVICE']
            region = request.args.get('region')
            
            instances = ec2_service.get_ec2_instances(account_id, region)
            
            return jsonify({
                'success': True,
                'instances': instances,
                'count': len(instances)
            })
            
        except Exception as e:
            logger.error(f"Error fetching EC2 instances: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/ec2/api/accounts/<account_id>/instances/<instance_id>/utilization')
    def get_instance_utilization(account_id, instance_id):
        """API endpoint to get instance utilization metrics"""
        try:
            ec2_service = app.config['EC2_SERVICE']
            days = int(request.args.get('days', 7))
            
            utilization = ec2_service.get_ec2_utilization(account_id, instance_id, days)
            
            return jsonify({
                'success': True,
                'utilization': utilization
            })
            
        except Exception as e:
            logger.error(f"Error fetching utilization: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/ec2/api/accounts/<account_id>/recommendations')
    def get_ec2_recommendations(account_id):
        """API endpoint to get EC2 optimization recommendations"""
        try:
            ec2_service = app.config['EC2_SERVICE']
            
            recommendations = ec2_service.get_optimization_recommendations(account_id)
            
            return jsonify({
                'success': True,
                'recommendations': recommendations
            })
        
        except Exception as e:
            logger.error(f"Error getting recommendations for account {account_id}: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/ec2/api/accounts/<account_id>/stopped-duration')
    def get_stopped_instances_duration(account_id):
        """API endpoint to get stopped instances by duration"""
        try:
            ec2_service = app.config['EC2_SERVICE']
            region = request.args.get('region')
            
            # Get all instances first
            instances = ec2_service.get_ec2_instances(account_id, region)
            
            # Calculate stopped instances by duration
            duration_data = ec2_service.get_stopped_instances_by_duration(instances)
            
            return jsonify({
                'success': True,
                'duration_data': duration_data
            })
        
        except Exception as e:
            logger.error(f"Error getting stopped instances duration for account {account_id}: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/ec2/api/accounts/<account_id>/sync', methods=['POST'])
    def sync_ec2_data(account_id):
        """API endpoint to sync EC2 data for an account"""
        try:
            ec2_service = app.config['EC2_SERVICE']
            
            # Fetch fresh EC2 data
            instances = ec2_service.get_ec2_instances(account_id)
            
            # Store in database
            ec2_service.store_ec2_data(account_id, instances)
            
            return jsonify({
                'success': True,
                'message': f'Synced {len(instances)} EC2 instances',
                'instances_synced': len(instances)
            })
            
        except Exception as e:
            logger.error(f"Error syncing EC2 data: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # Terraform Analyzer Routes
    @app.route('/terraform')
    def terraform_analyzer():
        """Terraform state analyzer page"""
        return render_template('terraform/analyzer.html')

    @app.route('/terraform/api/analyze', methods=['POST'])
    def analyze_terraform_state():
        """Analyze uploaded terraform.tfstate file"""
        if 'tfstate_file' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'})
        
        file = request.files['tfstate_file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'})
            
        if file:
            try:
                state_content = file.read().decode('utf-8')
                graph_data = analyze_state_file(state_content)
                
                return jsonify({
                    'success': True,
                    'data': graph_data
                })
            except Exception as e:
                logger.error(f"Error analyzing Terraform state: {str(e)}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        return jsonify({'success': False, 'error': 'File processing error'}), 500
        """API endpoint to sync EC2 data for an account"""
        try:
            ec2_service = app.config['EC2_SERVICE']
            
            # Fetch fresh EC2 data
            instances = ec2_service.get_ec2_instances(account_id)
            
            # Store in database
            ec2_service.store_ec2_data(account_id, instances)
            
            return jsonify({
                'success': True,
                'message': f'Synced {len(instances)} EC2 instances',
                'instances_synced': len(instances)
            })
            
        except Exception as e:
            logger.error(f"Error syncing EC2 data: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    return app

if __name__ == '__main__':
    print("🌟 Starting AWS Cost Optimization Tool...")
    print("📍 Server running at: http://127.0.0.1:5000")
    print("🎯 Dashboard URL: http://127.0.0.1:5000/dashboard")
    print("🔧 EC2 Dashboard: http://127.0.0.1:5000/ec2")
    print("⚙️  Debug mode: ON")
    print("=" * 50)
    
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
