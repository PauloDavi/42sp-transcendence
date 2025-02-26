from django.contrib.auth import get_user_model
import os

print("Creating superuser...")
User = get_user_model()
if not User.objects.filter(
    username=os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
).exists():
    User.objects.create_superuser(
        username=os.getenv("DJANGO_SUPERUSER_USERNAME", "admin"),
        email=os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com"),
        password=os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin123"),
    )
    print("Superuser created successfully")
