from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime

# Try to import AWS libraries, fallback gracefully
try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', 'dev-secret-key-change-in-production')

# AWS Configuration
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', 'eu-west-1')
DYNAMODB_TABLE = os.environ.get(
    'DYNAMODB_TABLE', 'portfolio-dashboard-visitor-counter')
S3_BUCKET = os.environ.get('S3_BUCKET', 'portfolio-assets-bucket')

# Initialize AWS clients if available
if AWS_AVAILABLE:
    try:
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.Table(DYNAMODB_TABLE)
        aws_ready = True
        print(f"AWS services initialized for region: {AWS_REGION}")
    except Exception as e:
        print(f"AWS services unavailable: {e}")
        aws_ready = False
else:
    aws_ready = False
    print("Running in local development mode - AWS libraries not installed")

# Portfolio data
PORTFOLIO_DATA = {
    "personal_info": {
        "name": "Your Name",
        "title": "Cloud DevOps Engineer & Full Stack Developer",
        "email": "your.email@example.com",
        "location": "Your City, Country",
        "bio": "Passionate developer specializing in cloud infrastructure, CI/CD pipelines, and modern web applications. Expert in AWS, Terraform, and containerized deployments."
    },
    "skills": [
        {"name": "AWS Cloud", "level": 85},
        {"name": "Terraform", "level": 80},
        {"name": "Python", "level": 90},
        {"name": "Docker", "level": 75},
        {"name": "Jenkins/GitHub Actions", "level": 80},
        {"name": "JavaScript", "level": 70},
        {"name": "Flask/FastAPI", "level": 85},
        {"name": "Linux/DevOps", "level": 80}
    ],
    "projects": [
        {
            "id": 1,
            "name": "Cloud Portfolio Dashboard",
            "description": "Fully automated cloud portfolio built with Flask, deployed on AWS using Terraform IaC, featuring auto-scaling, load balancing, and CI/CD with GitHub Actions.",
            "technologies": ["Python", "Flask", "AWS", "Terraform", "GitHub Actions", "DynamoDB", "Route53"],
            "status": "In Progress",
            "github_url": "https://github.com/yourusername/portfolio-dashboard",
            "live_url": "https://portfolio.yourdomain.com"
        },
        {
            "id": 2,
            "name": "Microservices E-commerce Platform",
            "description": "Containerized e-commerce platform with microservices architecture, API gateway, and event-driven communication.",
            "technologies": ["Python", "FastAPI", "Docker", "Kubernetes", "PostgreSQL", "Redis"],
            "status": "Completed",
            "github_url": "https://github.com/yourusername/ecommerce-microservices"
        },
        {
            "id": 3,
            "name": "Infrastructure Automation Suite",
            "description": "Complete infrastructure automation using Terraform modules, Ansible playbooks, and monitoring stack.",
            "technologies": ["Terraform", "Ansible", "Prometheus", "Grafana", "AWS", "Linux"],
            "status": "Completed",
            "github_url": "https://github.com/yourusername/infra-automation"
        }
    ],
    "experience": [
        {
            "company": "Your Company",
            "position": "DevOps Engineer",
            "duration": "2023 - Present",
            "description": "Led cloud migration initiatives and implemented CI/CD pipelines for 15+ applications."
        }
    ]
}


@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html', data=PORTFOLIO_DATA)


@app.route('/api/portfolio')
def get_portfolio():
    """API endpoint to get complete portfolio data"""
    return jsonify(PORTFOLIO_DATA)


@app.route('/api/projects')
def get_projects():
    """API endpoint to get projects only"""
    return jsonify(PORTFOLIO_DATA['projects'])


@app.route('/api/skills')
def get_skills():
    """API endpoint to get skills only"""
    return jsonify(PORTFOLIO_DATA['skills'])


@app.route('/api/health')
def health_check():
    """Health check endpoint for load balancer"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "region": AWS_REGION,
        "aws_available": aws_ready
    })


@app.route('/api/visitor-count')
def visitor_count():
    """Get and increment visitor count from DynamoDB"""
    if not aws_ready:
        # Return mock data for local development
        import random
        return jsonify({
            "count": random.randint(100, 500),
            "source": "local-mock"
        })

    try:
        # Get current count
        response = table.get_item(Key={'id': 'visitor_count'})

        if 'Item' in response:
            current_count = int(response['Item']['count'])
        else:
            current_count = 0

        # Increment count
        new_count = current_count + 1

        # Update DynamoDB
        table.put_item(Item={
            'id': 'visitor_count',
            'count': new_count,
            'last_updated': datetime.now().isoformat()
        })

        return jsonify({
            "count": new_count,
            "source": "dynamodb"
        })

    except Exception as e:
        print(f"DynamoDB error: {e}")
        return jsonify({
            "count": 1,
            "source": "fallback"
        })


@app.route('/api/contact', methods=['POST'])
def contact():
    """Handle contact form submissions"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "No data received"
            }), 400

        # Validate required fields
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not data.get(field, '').strip():
                return jsonify({
                    "status": "error",
                    "message": f"Field '{field}' is required"
                }), 400

        # Basic email validation
        email = data.get('email', '').strip()
        if '@' not in email or '.' not in email:
            return jsonify({
                "status": "error",
                "message": "Please provide a valid email address"
            }), 400

        # Log contact form submission
        contact_info = {
            "name": data.get('name', '').strip(),
            "email": email,
            "message": data.get('message', '').strip(),
            "timestamp": datetime.now().isoformat(),
            "source_ip": request.remote_addr
        }

        print(f"Contact form submission: {json.dumps(contact_info, indent=2)}")

        # Here you could integrate with AWS SES for email notifications
        # For now, just return success
        return jsonify({
            "status": "success",
            "message": f"Thank you {contact_info['name']}! Your message has been received."
        })

    except Exception as e:
        print(f"Contact form error: {e}")
        return jsonify({
            "status": "error",
            "message": "Sorry, there was an error processing your message."
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "code": 404
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "status": "error",
        "message": "Internal server error",
        "code": 500
    }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'

    print("Starting Portfolio Dashboard...")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"AWS Region: {AWS_REGION}")
    print(f"AWS Ready: {aws_ready}")

    app.run(host='0.0.0.0', port=port, debug=debug)
