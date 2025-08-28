#!/bin/bash

# 🚀 TASTY FINGERS - Railway Deployment Script
# This script helps automate the deployment process to Railway

echo "🚀 Starting TASTY FINGERS deployment to Railway..."
echo "=================================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not found. Please initialize git first:"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
    exit 1
fi

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "⚠️  Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if user is logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway:"
    railway login
fi

echo "📋 Pre-deployment checklist:"
echo "============================"

# Check for environment file
if [ -f "backend/.env" ]; then
    echo "⚠️  WARNING: .env file found. Make sure it's not committed to git!"
    echo "   Check your .gitignore file includes .env"
fi

# Check for hardcoded secrets
echo "🔍 Checking for hardcoded secrets..."
if grep -r "sk_test\|pk_test\|your-secret-key\|your-password" backend/ --exclude-dir=__pycache__ --exclude-dir=.git; then
    echo "⚠️  WARNING: Found potential hardcoded secrets!"
    echo "   Please review and remove before deployment"
fi

echo ""
echo "📦 Preparing for deployment..."

# Build static files
echo "📁 Building static files..."
cd backend
python manage.py collectstatic --noinput

# Run migrations locally to check for issues
echo "🗄️  Running migrations..."
python manage.py migrate --check

echo ""
echo "🚀 Ready to deploy!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Go to https://railway.app"
echo "2. Create new project"
echo "3. Connect your GitHub repository"
echo "4. Add PostgreSQL database"
echo "5. Configure environment variables (see env.example)"
echo "6. Deploy!"
echo ""
echo "Environment variables needed:"
echo "============================"
echo "SECRET_KEY=your-generated-secret-key"
echo "DEBUG=False"
echo "ALLOWED_HOSTS=your-railway-app.railway.app"
echo "DATABASE_URL=postgresql://... (Railway will provide)"
echo "PAYSTACK_PUBLIC_KEY=pk_live_..."
echo "PAYSTACK_SECRET_KEY=sk_live_..."
echo "CLOUDINARY_CLOUD_NAME=your-cloud-name"
echo "CLOUDINARY_API_KEY=your-api-key"
echo "CLOUDINARY_API_SECRET=your-api-secret"
echo "EMAIL_HOST_USER=your-email@gmail.com"
echo "EMAIL_HOST_PASSWORD=your-gmail-app-password"
echo ""
echo "📚 For detailed instructions, see: PRODUCTION_DEPLOYMENT_GUIDE.md"
echo "🔒 For security checklist, see: SECURITY_CHECKLIST.md"
echo ""
echo "✅ Deployment script completed!"
