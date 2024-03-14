#!/bin/sh

# Apply database migrations (if needed)
poetry run python manage.py migrate

# Check if superusers already exist for User model
existing_superusers=$(poetry run python manage.py shell -c "from accounts.models import User; User.objects.filter(is_superuser=True)")

if [ ! -z "$existing_superusers" ]; then
    echo "Superusers already exist:"
    echo "$existing_superusers"
else
    echo "Creating superuser..."
    poetry run python manage.py createsuperuser --noinput --username admin --email admin@example.com
fi

# Start the Django development server
poetry run python manage.py runserver 0.0.0.0:8000
