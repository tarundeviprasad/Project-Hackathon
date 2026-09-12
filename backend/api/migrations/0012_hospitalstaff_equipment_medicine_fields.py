from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('api', '0011_appointment_reason')]

    operations = [
        migrations.CreateModel(
            name='HospitalStaff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)), ('staff_id', models.CharField(max_length=50)),
                ('role', models.CharField(max_length=50)), ('department', models.CharField(max_length=120)),
                ('status', models.CharField(default='Active', max_length=30)), ('contact', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('facility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staff_members', to='api.facility')),
            ],
        ),
        migrations.AddConstraint(model_name='hospitalstaff', constraint=models.UniqueConstraint(fields=('facility', 'staff_id'), name='unique_hospital_staff_id')),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)), ('quantity', models.PositiveIntegerField()),
                ('category', models.CharField(choices=[('basic', 'Basic Resource'), ('advanced', 'Advanced Equipment')], default='basic', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('facility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='equipment', to='api.facility')),
            ],
        ),
        migrations.AddField(model_name='medicinestock', name='medicine_id', field=models.CharField(default='', max_length=50)),
        migrations.AddField(model_name='medicinestock', name='category', field=models.CharField(default='', max_length=80)),
        migrations.AddField(model_name='medicinestock', name='unit', field=models.CharField(default='Tablets', max_length=40)),
        migrations.AddField(model_name='medicinestock', name='reorder_level', field=models.PositiveIntegerField(default=1)),
        migrations.AddField(model_name='medicinestock', name='expiry_date', field=models.DateField(blank=True, null=True)),
    ]