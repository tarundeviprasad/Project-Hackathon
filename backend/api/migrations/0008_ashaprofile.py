from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_alter_auditlog_action'),
        ('portal_auth', '0003_add_asha_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='ASHAProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('worker_id', models.CharField(max_length=40, unique=True)),
                ('area', models.CharField(blank=True, default='', max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assigned_patients', models.ManyToManyField(blank=True, related_name='asha_workers', to='api.patient')),
                ('user', models.OneToOneField(limit_choices_to={'role': 'ASHA'}, on_delete=django.db.models.deletion.CASCADE, related_name='asha_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]