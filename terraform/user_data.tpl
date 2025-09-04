#!/bin/bash

# Update system
yum update -y

# Install required packages
yum install -y python3 python3-pip git nginx

# Create application user
useradd -m -s /bin/bash portfolio

# Create application directory
mkdir -p /opt/portfolio/app
mkdir -p /opt/portfolio/app/templates
chown -R portfolio:portfolio /opt/portfolio

# Create the Flask application
cat > /opt/portfolio/app/app.py << 'EOF'
from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'production-secret-key'

# AWS Configuration
AWS_REGION = "${aws_region}"
DYNAMODB_TABLE = "${dynamodb_table}"
S3_BUCKET = "${s3_bucket}"

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)

# Portfolio data
PORTFOLIO_DATA = {
    "personal_info": {
        "name": "Cloud Portfolio",
        "title": "DevOps Engineer & Developer",
        "email": "contact@example.com",
        "location": "Cloud Native",
        "bio": "Automated cloud portfolio built with Flask, AWS, and Terraform."
    },
    "skills": [
        {"name": "AWS", "level": 90},
        {"name": "Terraform", "level": 85},
        {"name": "Python", "level": 80},
        {"name": "DevOps", "level": 85}
    ],
    "projects": [
        {
            "id": 1,
            "name": "Cloud Portfolio",
            "description": "Automated cloud portfolio with CI/CD",
            "technologies": ["AWS", "Terraform", "Flask", "GitHub Actions"],
            "status": "In Progress"
        }
    ]
}

@app.route('/')
def dashboard():
    return render_template('dashboard.html', data=PORTFOLIO_DATA)

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    })

@app.route('/api/visitor-count')
def visitor_count():
    try:
        response = table.get_item(Key={'id': 'visitor_count'})
        if 'Item' in response:
            current_count = int(response['Item']['count'])
        else:
            current_count = 0
        
        new_count = current_count + 1
        table.put_item(Item={'id': 'visitor_count', 'count': new_count})
        
        return jsonify({"count": new_count, "source": "dynamodb"})
    except Exception as e:
        return jsonify({"count": 1, "source": "fallback"})

@app.route('/api/portfolio')
def get_portfolio():
    return jsonify(PORTFOLIO_DATA)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

# Create basic HTML template
cat > /opt/portfolio/app/templates/dashboard.html << 'HTML_EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Portfolio Dashboard</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: #0f0f23; 
            color: white; 
            margin: 40px; 
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #00d4ff; }
        .metric { 
            display: inline-block; 
            margin: 10px; 
            padding: 15px; 
            background: #00d4ff; 
            border-radius: 5px; 
            color: black; 
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ data.personal_info.name }}</h1>
        <h2>{{ data.personal_info.title }}</h2>
        <p>{{ data.personal_info.bio }}</p>
        
        <h3>Skills:</h3>
        {% for skill in data.skills %}
        <p>{{ skill.name }}: {{ skill.level }}%</p>
        {% endfor %}
        
        <h3>Projects:</h3>
        {% for project in data.projects %}
        <div>
            <h4>{{ project.name }}</h4>
            <p>{{ project.description }}</p>
        </div>
        {% endfor %}
        
        <div class="metric">Visitors: <span id="visitor-count">--</span></div>
    </div>
    
    <script>
        fetch('/api/visitor-count')
            .then(response => response.json())
            .then(data => {
                document.getElementById('visitor-count').textContent = data.count;
            });
    </script>
</body>
</html>
HTML_EOF

# Create requirements.txt
cat > /opt/portfolio/app/requirements.txt << 'REQ_EOF'
Flask==2.3.3
boto3==1.34.0
gunicorn==21.2.0
REQ_EOF

# Set ownership
chown -R portfolio:portfolio /opt/portfolio

# Install Python dependencies
cd /opt/portfolio/app
pip3 install -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/portfolio.service << 'SERVICE_EOF'
[Unit]
Description=Portfolio Flask App
After=network.target

[Service]
Type=simple
User=portfolio
WorkingDirectory=/opt/portfolio/app
Environment=AWS_DEFAULT_REGION=${aws_region}
Environment=DYNAMODB_TABLE=${dynamodb_table}
Environment=S3_BUCKET=${s3_bucket}
ExecStart=/usr/bin/python3 -m gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Start the service
systemctl daemon-reload
systemctl enable portfolio
systemctl start portfolio

# Configure nginx
cat > /etc/nginx/conf.d/portfolio.conf << 'NGINX_EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /health {
        access_log off;
        return 200 "healthy\n";
    }
}
NGINX_EOF

# Start nginx
systemctl enable nginx
systemctl start nginx

echo "Portfolio application setup completed" > /var/log/portfolio-setup.log