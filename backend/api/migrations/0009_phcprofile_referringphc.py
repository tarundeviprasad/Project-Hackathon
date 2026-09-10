from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_ashaprofile'),
        ('portal_auth', '0004_add_phc_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='PHCProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('centre_id', models.CharField(max_length=40, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assigned_patients', models.ManyToManyField(blank=True, related_name='phc_centres', to='api.patient')),
                ('facility', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='phc_profiles', to='api.facility')),
                ('user', models.OneToOneField(limit_choices_to={'role': 'PHC'}, on_delete=django.db.models.deletion.CASCADE, related_name='phc_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='referral',
            name='referring_doctor',
            field=models.ForeignKey(blank=True, limit_choices_to={'role': 'DOCTOR'}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='sent_referrals', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='referral',
            name='referring_phc',
            field=models.ForeignKey(blank=True, limit_choices_to={'role': 'PHC'}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='phc_referrals', to=settings.AUTH_USER_MODEL),
        ),
    ]