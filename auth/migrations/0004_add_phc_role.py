from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal_auth', '0003_add_asha_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[
                    ('PATIENT', 'Patient'),
                    ('DOCTOR', 'Doctor'),
                    ('PHC', 'Primary Health Centre'),
                    ('ASHA', 'ASHA Worker'),
                    ('ADMIN', 'Admin'),
                    ('HOSPITAL_ADMIN', 'Hospital Admin'),
                ],
                default='PATIENT',
                max_length=20,
            ),
        ),
    ]