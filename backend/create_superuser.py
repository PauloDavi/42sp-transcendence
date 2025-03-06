import logging
import os

from django.contrib.auth import get_user_model

logging.basicConfig(level=logging.INFO)
User = get_user_model()

logging.info("Creating superuser...")
if not User.objects.filter(username=os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")).exists():
    User.objects.create_superuser(
        username=os.getenv("DJANGO_SUPERUSER_USERNAME", "admin"),
        email=os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com"),
        password=os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin123"),
    )
    logging.info("Superuser created successfully")

logging.info("Creating AI user...")
if not User.objects.filter(username="AI").exists():
    User.objects.create_user(
        username="AI",
        email="ai@pong42.com",
        first_name="Artificial",
        last_name="Intelligence",
        is_active=True,
    )
    logging.info("AI user created successfully")
