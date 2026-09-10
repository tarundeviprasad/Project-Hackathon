from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import ASHAProfile


class Command(BaseCommand):
    help = 'Create or update the idempotent ASHA portal account.'

    def handle(self, *args, **options):
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username='ASHA1@gmail.com',
            defaults={
                'email': 'ASHA1@gmail.com',
                'first_name': 'ASHA Worker',
                'role': 'ASHA',
                'is_active': True,
            },
        )
        changed = False
        for field, value in {
            'email': 'ASHA1@gmail.com',
            'first_name': 'ASHA Worker',
            'role': 'ASHA',
            'is_active': True,
        }.items():
            if getattr(user, field) != value:
                setattr(user, field, value)
                changed = True
        if created or not user.check_password('123456789'):
            user.set_password('123456789')
            changed = True
        if changed:
            user.save()
        ASHAProfile.objects.get_or_create(
            user=user,
            defaults={'worker_id': f'ASHA-{user.id:04d}'},
        )
        self.stdout.write(self.style.SUCCESS(
            f"ASHA account {'created' if created else 'verified'}: {user.username}"
        ))
