#!/bin/bash
set -e

# Build script for Railway deployment

echo "🚀 Starting build process..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create default superuser if it doesn't exist
echo "👤 Creating default superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@tastyfingers.com', 'admin123')
    print('Default superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

echo "✅ Build completed successfully!"
