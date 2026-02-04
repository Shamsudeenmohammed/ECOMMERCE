from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError
import os


class EcommerceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ecommerce"

    def ready(self):
        # Only run when explicitly enabled
        if os.environ.get("CREATE_DEFAULT_ADMIN") != "true":
            return

        try:
            User = get_user_model()

            username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
            email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
            password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

            if not username or not password:
                return

            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                print("✅ Default test admin created")

        except OperationalError:
            # Database not ready yet (e.g. before migrate)
            pass
