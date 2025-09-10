# AWS Cost Optimization Tool

A comprehensive Flask-based web application for monitoring, analyzing, and optimizing AWS costs with professional CloudSpend-inspired UI.

## Features

### 🎯 Core Functionality
- **Real-time Cost Dashboard** - Monitor current and historical AWS spending
- **Cost Trend Analysis** - Visualize spending patterns with interactive charts
- **Service Breakdown** - Detailed cost analysis by AWS service
- **Optimization Recommendations** - AI-powered suggestions to reduce costs
- **Business Unit Management** - Organize costs by department/team
- **Account Integration** - Secure AWS account connection wizard

### 🔧 Technical Features
- **Professional UI** - CloudSpend/Site24x7 inspired modern interface
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
cd /home/ubuntu/LocalAWS_CodeBuild/repos/cost_optimization
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Run the Application**
```bash
python app.py
```

3. **Access the Dashboard**
- Open your browser to: http://127.0.0.1:5000
- Dashboard URL: http://127.0.0.1:5000/dashboard

## Application Structure

```
cost_optimization/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── app/
│   ├── static/
│   │   └── css/
│   │       └── cloudspend-style.css # Modern UI styling
│   └── templates/
│       ├── base.html               # Base template
│       ├── cloudspend-dashboard.html # Main dashboard
│       ├── business_units/
│       │   └── index.html          # Business units page
│       └── integration/
│           ├── accounts.html       # Account management
│           └── wizard.html         # Integration wizard
```

## Key Pages

### 📊 Dashboard (`/`)
- Cost metrics cards with trend indicators
- Interactive cost trend chart
- Top services breakdown
- Optimization recommendations
- Real-time data updates

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

## API Endpoints

### Cost Data
- `GET /api/cost-data` - Retrieve cost trend data
- `GET /api/recommendations` - Get optimization recommendations

### Integration
- `POST /integration/api/policy/generate` - Generate IAM policy

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
        "budgets:ViewBudget"
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
