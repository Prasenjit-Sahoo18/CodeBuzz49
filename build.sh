#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip to the latest version
pip install --upgrade pip

# Install dependencies (use Render-specific requirements file if available)
if [ -f "requirements_render.txt" ]; then
    echo "Using Render-specific requirements file"
    pip install -r requirements_render.txt
else
    echo "Using default requirements file"
    pip install -r requirements.txt
fi

# Test computer vision libraries (optional)
echo "Testing computer vision libraries (optional)..."
python test_cv.py || echo "Warning: Computer vision libraries not available, proctoring will be disabled"

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate