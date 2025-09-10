#!/usr/bin/env python3
"""
AWS Cost Optimization Tool - Main Flask Application
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
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

    return app

if __name__ == '__main__':
    print("🌟 Starting AWS Cost Optimization Tool...")
    print("📍 Server running at: http://127.0.0.1:5000")
    print("🎯 Dashboard URL: http://127.0.0.1:5000/dashboard")
    print("⚙️  Debug mode: ON")
    print("=" * 50)
    
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True)
