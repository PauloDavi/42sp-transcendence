import requests
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount


@receiver(post_save, sender=SocialAccount)
def save_42_avatar(sender, instance, created, **kwargs):
    if created and instance.provider == "fortytwo":
        user = instance.user
        avatar_url = instance.extra_data.get("avatar_url")

        if avatar_url:
            response = requests.get(avatar_url)
            image = BytesIO(response.content)
            image.name = "avatar.jpg"
            avatar_file = InMemoryUploadedFile(
                image, None, image.name, "image/jpeg", len(image.getvalue()), None
            )
            print(avatar_file)
            user.avatar.save(avatar_file.name, avatar_file, save=True)
            user.save()
