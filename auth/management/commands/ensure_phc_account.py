from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from api.models import Facility, PHCProfile


class Command(BaseCommand):
    help = 'Create or update the idempotent PHC portal account.'

    def handle(self, *args, **options):
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username='PHC1@gmail.com',
            defaults={
                'email': 'PHC1@gmail.com',
                'first_name': 'PHC Worker',
                'role': 'PHC',
                'is_active': True,
            },
        )
        changed = False
        for field, value in {
            'email': 'PHC1@gmail.com',
            'first_name': 'PHC Worker',
            'role': 'PHC',
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

        facility, _ = Facility.objects.get_or_create(
            name='PHC 1',
            defaults={'facility_type': 'PHC'},
        )
        PHCProfile.objects.get_or_create(
            user=user,
            defaults={'facility': facility, 'centre_id': f'PHC-{user.id:04d}'},
        )
        self.stdout.write(self.style.SUCCESS(
            f"PHC account {'created' if created else 'verified'}: {user.username}"
        ))