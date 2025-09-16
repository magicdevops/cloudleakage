# CloudLeakage - AWS Cost Optimization Tool

A comprehensive Flask-based web application for monitoring, analyzing, and optimizing AWS costs with professional CloudSpend-inspired UI and advanced EC2 instance management.

## Features

### 🎯 Core Functionality
- **Real-time Cost Dashboard** - Monitor current and historical AWS spending
- **EC2 Instance Management** - Comprehensive EC2 dashboard with real-time monitoring
- **Snapshot Management** - Advanced EBS snapshot monitoring and optimization
- **Cost Trend Analysis** - Visualize spending patterns with interactive charts
- **Service Breakdown** - Detailed cost analysis by AWS service
- **Optimization Recommendations** - AI-powered suggestions to reduce costs
- **Data Export** - Export EC2, snapshot, and cost data in CSV, JSON, and Excel formats
- **Business Unit Management** - Organize costs by department/team
- **Account Integration** - Secure AWS account connection wizard
- **Terraform State Analyzer** - Visualize infrastructure from `terraform.tfstate` files

### 🔧 Technical Features
- **Professional UI** - CloudSpend/Site24x7 inspired modern interface
- **Multi-Database Support** - SQLite, PostgreSQL, MySQL compatibility
- **Encrypted Credentials** - Secure storage with Fernet encryption
- **Responsive Design** - Works seamlessly on desktop and mobile
- **Real-time Updates** - Auto-refreshing data and charts
- **Secure Integration** - IAM role-based AWS access
- **RESTful APIs** - JSON endpoints for data access

## Quick Start

### Prerequisites
- Python 3.8+
- AWS Account with appropriate permissions
- Modern web browser

### Installation

1. **Clone and Setup**
```bash
cd /home/ubuntu/LocalAWS_CodeBuild/repos/cloudleakage
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Run the Application**
```bash
python app.py
```

3. **Access the Dashboard**
- Open your browser to: http://127.0.0.1:5000
- Main Dashboard: http://127.0.0.1:5000/dashboard
- EC2 Dashboard: http://127.0.0.1:5000/ec2
- Snapshots Dashboard: http://127.0.0.1:5000/snapshots

## 🗄️ Database Setup

CloudLeakage supports multiple database backends for flexible deployment options:

### SQLite (Default - Development)
```bash
# No additional setup required
# Database file 'cloudleakage.db' created automatically
python app.py
```

### PostgreSQL (Production Recommended)
```bash
# 1. Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib libpq-dev

# 2. Create database and user
sudo -u postgres psql
CREATE DATABASE cloudleakage;
CREATE USER cloudleakage_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE cloudleakage TO cloudleakage_user;
\q

# 3. Install Python dependencies
pip install psycopg2-binary

# 4. Set environment variable
export DATABASE_URL="postgresql://cloudleakage_user:secure_password@localhost:5432/cloudleakage"

# 5. Run application
python app.py
```

### MySQL (Production Alternative)
```bash
# 1. Install MySQL
sudo apt-get install mysql-server libmysqlclient-dev

# 2. Create database and user
sudo mysql
CREATE DATABASE cloudleakage;
CREATE USER 'cloudleakage_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON cloudleakage.* TO 'cloudleakage_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 3. Install Python dependencies
pip install mysqlclient

# 4. Set environment variable
export DATABASE_URL="mysql://cloudleakage_user:secure_password@localhost:3306/cloudleakage"

# 5. Run application
python app.py
```

### Database Schema
The application automatically creates these tables:
- **`cloud_accounts`** - Encrypted AWS credentials and account info
- **`cost_data`** - AWS cost and usage data
- **`sync_history`** - Synchronization operation tracking
- **`ec2_instances`** - EC2 instance data and metadata
- **`snapshots`** - EBS snapshot data and metadata
- **`volumes`** - EBS volume information and snapshot relationships

### Security Configuration
```bash
# Required for production
export ENCRYPTION_KEY="your-32-byte-base64-encoded-key"
export DATABASE_URL="your-database-connection-string"
export SECRET_KEY="your-flask-secret-key"

# Required for Terraform Analyzer (Gemini Integration)
export GEMINI_API_KEY="your-google-ai-studio-api-key"
```

## Application Structure

```
cloudleakage/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── DATABASE_SETUP.md               # Database configuration guide
├── cloudleakage.db                 # SQLite database (auto-created)
├── account_manager.py              # AWS account management
├── ec2_service.py                  # EC2 instance operations
├── snapshot_service.py             # EBS snapshot operations
├── terraform_analyzer.py           # Terraform state parsing logic
├── simple_database.py              # Simple database implementation
├── static/
│   └── css/
│       └── cloudspend-style.css    # Modern UI styling
└── templates/
    ├── cloudspend-dashboard.html   # Main dashboard
    ├── business_units/
    │   └── index.html              # Business units page
    ├── ec2/
    │   └── dashboard.html          # EC2 management dashboard
    ├── snapshots/
    │   └── dashboard.html          # Snapshot management dashboard
    ├── integration/
    │   ├── accounts.html           # Account management
    │   └── wizard.html             # Integration wizard
    └── terraform/
        └── analyzer.html           # Terraform state analyzer
```

## Key Pages

### 📊 Main Dashboard (`/dashboard`)
- Cost metrics cards with trend indicators
- Interactive cost trend chart
- Top services breakdown
- Optimization recommendations
- Real-time data updates

### 🖥️ EC2 Dashboard (`/ec2`)
- Real-time EC2 instance monitoring
- Instance state management (running, stopped, pending)
- Comprehensive instance details with tags
- Cost optimization recommendations
- Data export (CSV, JSON, Excel formats)
- Multi-region support
- Sync functionality for real-time updates

### 📸 Snapshots Dashboard (`/snapshots`)
- **EBS Snapshot Management** - Monitor all EBS snapshots across AWS regions
- **Enterprise-Style Widgets** - Professional metrics cards with meaningful icons
- **Comprehensive Export Options** - Export snapshot data in CSV, JSON, and Excel formats
- **Advanced Filtering** - Filter by region, age, and snapshot status
- **Cost Optimization Insights** - Identify old snapshots (30, 60, 90+ days) for cleanup
- **Volume Relationship Tracking** - Monitor volumes with and without snapshots
- **Multi-Region Support** - Complete coverage of all 34 AWS regions
- **Real-Time Data Sync** - Automatic data refresh and synchronization

### 🏢 Business Units (`/business-units`)
- Cost allocation by department
- Resource tracking per unit
- Month-over-month comparisons
- Detailed cost breakdowns

### 🔗 Account Integration (`/integration`)
- Secure AWS account connection
- Step-by-step integration wizard
- IAM role setup guidance
- Connection status monitoring

### 🗺️ Terraform Analyzer (`/terraform`)
- Upload `terraform.tfstate` files to visualize your infrastructure
- View a network graph of resources and their dependencies
- Understand connections and relationships between components

## API Endpoints

### Cost Data
- `GET /api/cost-data` - Retrieve cost trend data
- `GET /api/recommendations` - Get optimization recommendations

### EC2 Management
- `GET /ec2/api/accounts/{id}/instances` - Get EC2 instances
- `POST /ec2/api/accounts/{id}/sync` - Sync EC2 data
- `GET /ec2/api/accounts/{id}/recommendations` - Get EC2 optimization recommendations

### Snapshots Management
- `GET /snapshots/api/accounts/{id}/snapshots` - Get EBS snapshots
- `GET /snapshots/api/accounts/{id}/analysis` - Get snapshot analysis data
- `GET /snapshots/api/accounts/{id}/volumes-without-snapshots` - Get volumes without snapshots
- `POST /snapshots/api/accounts/{id}/sync` - Sync snapshot data

### Integration
- `POST /integration/api/accounts` - Create AWS account integration
- `POST /integration/api/policy/generate` - Generate IAM policy

### Terraform
- `POST /terraform/api/analyze` - Upload and analyze a `terraform.tfstate` file

## AWS Integration

The tool uses IAM roles for secure access to AWS Cost Explorer and other services:

### Required AWS Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "ce:GetDimensionValues",
        "organizations:ListAccounts",
        "budgets:ViewBudget",
        "ec2:DescribeInstances",
        "ec2:DescribeInstanceTypes",
        "ec2:DescribeRegions",
        "ec2:DescribeAvailabilityZones",
        "ec2:DescribeSnapshots",
        "ec2:DescribeVolumes",
        "cloudwatch:GetMetricStatistics",
        "pricing:GetProducts"
      ],
      "Resource": "*"
    }
  ]
}
```

## UI Design System

### Color Palette
- **Primary Blue**: `#1a73e8` - Main actions and highlights
- **Secondary Green**: `#34a853` - Success states and positive metrics
- **Warning Yellow**: `#fbbc04` - Warnings and attention items
- **Danger Red**: `#ea4335` - Errors and negative metrics

### Components
- **Metric Cards** - Key performance indicators with trend arrows
- **Charts** - Interactive Chart.js visualizations
- **Tables** - Responsive data tables with sorting
- **Navigation** - Fixed sidebar with section organization

## Development

### Adding New Features
1. Create route in `app.py`
2. Add template in `app/templates/`
3. Update navigation in sidebar
4. Add API endpoints if needed

### Styling Guidelines
- Use CSS variables from `cloudspend-style.css`
- Follow existing component patterns
- Maintain responsive design principles
- Test on multiple screen sizes

## Production Deployment

### Environment Variables
```bash
export SECRET_KEY="your-production-secret-key"
export FLASK_ENV="production"
```

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Troubleshooting

### Common Issues
1. **Port 5000 in use**: Change port in `app.py` or kill existing process
2. **AWS permissions**: Ensure IAM role has required Cost Explorer permissions
3. **Missing dependencies**: Run `pip install -r requirements.txt`

### Debug Mode
The application runs in debug mode by default for development. Disable for production:
```python
app.run(debug=False)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the troubleshooting section
- Review AWS IAM permissions
- Ensure all dependencies are installed
- Verify Python version compatibility

---

**Built with ❤️ for AWS cost optimization**
