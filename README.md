# Portfolio Dashboard - Cloud Infrastructure Project

A professional portfolio dashboard built with Flask and deployed on AWS using Infrastructure as Code (Terraform) and automated CI/CD with GitHub Actions.

## Architecture Overview

```
GitHub → GitHub Actions → AWS (Terraform)
   ↓           ↓            ↓
Code Push → Build/Test → Deploy Infrastructure
                           ↓
                    Load Balancer → EC2 Instances
                           ↓            ↓
                    DynamoDB ← Flask App → S3
```

## Tech Stack

**Frontend & Backend:**
- Python Flask with Jinja2 templates
- Dark cyberpunk-themed responsive design
- RESTful API endpoints
- Real-time visitor counter

**Infrastructure:**
- AWS VPC with public subnets
- Application Load Balancer (ALB)
- Auto Scaling Group with EC2 instances
- DynamoDB for visitor counter
- S3 bucket for assets
- CloudWatch monitoring

**DevOps:**
- Terraform Infrastructure as Code
- GitHub Actions CI/CD pipeline
- Automated testing and deployment
- Environment-specific configurations

## Features

- **Portfolio Showcase**: Skills, projects, and experience
- **Live Metrics**: Real-time visitor counter via DynamoDB
- **Contact Form**: Functional contact form with validation
- **Health Monitoring**: Application health checks
- **Auto Scaling**: Automatic scaling based on demand
- **High Availability**: Multi-AZ deployment

## Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/portfolio-dashboard-clean.git
cd portfolio-dashboard-clean

# Setup Python environment
cd app/
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run locally
python app.py
# Visit http://localhost:5000
```

## Deployment

### Prerequisites

1. AWS Account with appropriate permissions
2. GitHub repository
3. AWS credentials configured as GitHub secrets

### GitHub Secrets Required

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

### Deploy Options

**Option 1: Automatic (Push to main)**
```bash
git push origin main
# Automatically triggers deployment
```

**Option 2: Manual Deployment**
1. Go to GitHub Actions tab
2. Select "Deploy Portfolio to AWS"
3. Click "Run workflow"
4. Choose action: plan/apply/destroy

**Option 3: Local Terraform**
```bash
cd terraform/
terraform init
terraform plan
terraform apply
```

## CI/CD Pipeline

The GitHub Actions workflow includes:

1. **Validate**: Code quality and Terraform syntax
2. **Plan**: Preview infrastructure changes (PRs)
3. **Deploy**: Apply changes to AWS (main branch)
4. **Test**: Health checks and verification
5. **Destroy**: Clean up infrastructure (manual)

## Infrastructure Components

### Networking
- **VPC**: 10.0.0.0/16 with public subnets
- **Subnets**: Multi-AZ for high availability
- **Security Groups**: Restricted access controls

### Compute
- **EC2 Instances**: t3.micro (free tier eligible)
- **Auto Scaling**: 1-3 instances based on demand
- **Load Balancer**: Application Load Balancer with health checks

### Storage & Database
- **DynamoDB**: Serverless visitor counter
- **S3**: Static assets and application storage

### Monitoring
- **CloudWatch**: Application and infrastructure monitoring
- **Health Checks**: Automatic failover and recovery

## Security

- **IAM Roles**: Least privilege access
- **Security Groups**: Network-level firewall
- **VPC**: Isolated network environment
- **HTTPS Ready**: SSL/TLS termination support

## Cost Optimization

- **Free Tier**: Designed to use AWS free tier resources
- **Auto Scaling**: Scale down during low usage
- **Serverless Components**: Pay-per-use DynamoDB
- **Efficient Instance Types**: t3.micro for cost efficiency

## Customization

### Update Personal Information
Edit `app/app.py` and update `PORTFOLIO_DATA`:
```python
PORTFOLIO_DATA = {
    "personal_info": {
        "name": "Your Name",
        "title": "Your Title",
        # ... your information
    }
}
```

### Infrastructure Changes
Modify `terraform/terraform.tfvars`:
```hcl
aws_region = "eu-west-1"
project_name = "your-project-name"
instance_type = "t3.micro"
```

## Troubleshooting

### Common Issues

**Terraform State Conflicts:**
```bash
cd terraform/
rm -rf .terraform/
terraform init
```

**Health Check Failures:**
- Check security group rules
- Verify application is running on port 5000
- Check CloudWatch logs

**Deployment Failures:**
- Verify AWS credentials
- Check resource limits
- Review CloudWatch logs

### Monitoring

**Application Logs:**
- CloudWatch Logs: `/aws/ec2/portfolio-dashboard`
- SSH to instances: `ssh ec2-user@instance-ip`

**Health Endpoints:**
- Health Check: `http://your-alb-dns/api/health`
- Visitor Count: `http://your-alb-dns/api/visitor-count`

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m "Add new feature"`
4. Push branch: `git push origin feature/new-feature`
5. Create Pull Request

## License

This project is open source and available under the MIT License.

## Contact

For questions or support, please open an issue in this repository.