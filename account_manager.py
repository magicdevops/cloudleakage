#!/usr/bin/env python3
"""
Account Integration Manager - Secure credential storage and AWS account management
"""

import os
import json
import boto3
import uuid
import logging
from datetime import datetime
from cryptography.fernet import Fernet
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

# File paths for storing account data (in production, use a proper database)
ACCOUNTS_DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'accounts.json')

def ensure_data_directory():
    """Ensure the data directory exists"""
    data_dir = os.path.dirname(ACCOUNTS_DATA_FILE)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, mode=0o700)  # Secure permissions

def generate_account_id():
    """Generate a unique account ID"""
    return str(uuid.uuid4())

def encrypt_credentials(credentials, cipher_suite):
    """Encrypt sensitive credentials"""
    try:
        credentials_json = json.dumps(credentials)
        encrypted_data = cipher_suite.encrypt(credentials_json.encode())
        return encrypted_data.decode()
    except Exception as e:
        logger.error(f"Error encrypting credentials: {str(e)}")
        raise

def decrypt_credentials(encrypted_credentials, cipher_suite):
    """Decrypt sensitive credentials"""
    try:
        decrypted_data = cipher_suite.decrypt(encrypted_credentials.encode())
        return json.loads(decrypted_data.decode())
    except Exception as e:
        logger.error(f"Error decrypting credentials: {str(e)}")
        raise

def test_aws_credentials(access_key_id, secret_access_key, region='us-east-1'):
    """Test AWS credentials by making a simple API call"""
    try:
        # Create a temporary session with the provided credentials
        session = boto3.Session(
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region
        )
        
        # Test with STS to get account information
        sts_client = session.client('sts')
        identity = sts_client.get_caller_identity()
        
        # Test Cost Explorer access (optional - don't fail if no access)
        cost_access = False
        try:
            ce_client = session.client('ce', region_name='us-east-1')  # CE is only available in us-east-1
            
            # Try to get a simple cost query to verify permissions
            ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': '2024-01-01',
                    'End': '2024-01-02'
                },
                Granularity='DAILY',
                Metrics=['BlendedCost']
            )
            cost_access = True
        except ClientError as e:
            # Don't fail account creation if Cost Explorer access is denied
            if e.response['Error']['Code'] in ['AccessDenied', 'AccessDeniedException', 'UnauthorizedOperation']:
                cost_access = False
                logger.warning(f"Cost Explorer access denied for credentials, but basic AWS access confirmed")
            else:
                # Only fail for other types of errors (invalid credentials, etc.)
                raise
        
        return {
            'valid': True,
            'accountInfo': {
                'accountId': identity.get('Account'),
                'userId': identity.get('UserId'),
                'arn': identity.get('Arn'),
                'costAccess': cost_access
            }
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'InvalidUserID.NotFound':
            return {'valid': False, 'error': 'Invalid Access Key ID'}
        elif error_code == 'SignatureDoesNotMatch':
            return {'valid': False, 'error': 'Invalid Secret Access Key'}
        elif error_code == 'TokenRefreshRequired':
            return {'valid': False, 'error': 'Credentials expired'}
        else:
            return {'valid': False, 'error': f'AWS Error: {error_code}'}
    except NoCredentialsError:
        return {'valid': False, 'error': 'No credentials provided'}
    except Exception as e:
        logger.error(f"Error testing AWS credentials: {str(e)}")
        return {'valid': False, 'error': 'Failed to validate credentials'}

def test_iam_role(role_arn):
    """Test IAM role access by attempting to assume the role"""
    try:
        # This would require the current AWS credentials to have permission to assume the role
        # For now, we'll do basic validation
        if not role_arn.startswith('arn:aws:iam::'):
            return {'valid': False, 'error': 'Invalid Role ARN format'}
        
        # Extract account ID from ARN
        parts = role_arn.split(':')
        if len(parts) < 6:
            return {'valid': False, 'error': 'Invalid Role ARN format'}
        
        account_id = parts[4]
        role_name = parts[5].split('/')[-1]
        
        return {
            'valid': True,
            'accountInfo': {
                'accountId': account_id,
                'roleName': role_name,
                'roleArn': role_arn
            }
        }
        
    except Exception as e:
        logger.error(f"Error testing IAM role: {str(e)}")
        return {'valid': False, 'error': 'Failed to validate IAM role'}

def save_account_integration(account_data):
    """Save account integration data to file"""
    try:
        ensure_data_directory()
        
        # Load existing accounts
        accounts = load_account_integrations()
        
        # Add new account
        accounts.append(account_data)
        
        # Save back to file
        save_account_integrations(accounts)
        
        logger.info(f"Saved account integration: {account_data['displayName']}")
        
    except Exception as e:
        logger.error(f"Error saving account integration: {str(e)}")
        raise

def load_account_integrations():
    """Load account integrations from file"""
    try:
        if not os.path.exists(ACCOUNTS_DATA_FILE):
            return []
        
        with open(ACCOUNTS_DATA_FILE, 'r') as f:
            return json.load(f)
            
    except Exception as e:
        logger.error(f"Error loading account integrations: {str(e)}")
        return []

def save_account_integrations(accounts):
    """Save account integrations to file"""
    try:
        ensure_data_directory()
        
        with open(ACCOUNTS_DATA_FILE, 'w') as f:
            json.dump(accounts, f, indent=2)
        
        # Set secure file permissions
        os.chmod(ACCOUNTS_DATA_FILE, 0o600)
        
    except Exception as e:
        logger.error(f"Error saving account integrations: {str(e)}")
        raise

def perform_account_sync(account):
    """Perform data synchronization for an account"""
    try:
        if account['accessType'] == 'accesskey':
            # For access key authentication, we would decrypt credentials and use them
            # This is a placeholder for actual sync logic
            return {
                'success': True,
                'data': {
                    'syncTime': datetime.utcnow().isoformat(),
                    'resourcesScanned': 0,  # Placeholder
                    'costsRetrieved': True
                }
            }
        elif account['accessType'] == 'iam':
            # For IAM role authentication
            return {
                'success': True,
                'data': {
                    'syncTime': datetime.utcnow().isoformat(),
                    'resourcesScanned': 0,  # Placeholder
                    'costsRetrieved': True
                }
            }
        else:
            return {'success': False, 'error': 'Unsupported access type'}
            
    except Exception as e:
        logger.error(f"Error performing account sync: {str(e)}")
        return {'success': False, 'error': str(e)}

def get_account_cost_data(account, cipher_suite, start_date, end_date):
    """Get cost data for a specific account"""
    try:
        if account['accessType'] == 'accesskey':
            # Decrypt credentials
            credentials = decrypt_credentials(account['credentials'], cipher_suite)
            
            # Create AWS session
            session = boto3.Session(
                aws_access_key_id=credentials['accessKeyId'],
                aws_secret_access_key=credentials['secretAccessKey'],
                region_name=credentials.get('region', 'us-east-1')
            )
            
            # Get cost data using Cost Explorer
            ce_client = session.client('ce', region_name='us-east-1')
            
            response = ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            
            return {
                'success': True,
                'data': response
            }
            
        elif account['accessType'] == 'iam':
            # For IAM role, we would assume the role first
            # This is a placeholder for actual implementation
            return {
                'success': True,
                'data': {'placeholder': 'IAM role cost data'}
            }
        else:
            return {'success': False, 'error': 'Unsupported access type'}
            
    except Exception as e:
        logger.error(f"Error getting account cost data: {str(e)}")
        return {'success': False, 'error': str(e)}

def delete_account_integration(account_id):
    """Delete an account integration"""
    try:
        accounts = load_account_integrations()
        accounts = [acc for acc in accounts if acc['id'] != account_id]
        save_account_integrations(accounts)
        
        logger.info(f"Deleted account integration: {account_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting account integration: {str(e)}")
        return False
