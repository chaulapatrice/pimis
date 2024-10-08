# Generated by Django 5.0.3 on 2024-03-15 08:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='application',
            name='city',
        ),
        migrations.RemoveField(
            model_name='application',
            name='street',
        ),
        migrations.RemoveField(
            model_name='application',
            name='suburb',
        ),
        migrations.AddField(
            model_name='applicantdetails',
            name='city',
            field=models.CharField(default=1, max_length=150),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='applicantdetails',
            name='street',
            field=models.CharField(default=1, max_length=150),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='applicantdetails',
            name='suburb',
            field=models.CharField(default=1, max_length=150),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='applicantdetails',
            name='application',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='applicant', to='core.application'),
        ),
        migrations.AlterField(
            model_name='applicantdetails',
            name='birth_cerificate',
            field=models.FileField(upload_to='files/2024/3/15'),
        ),
        migrations.AlterField(
            model_name='applicantdetails',
            name='national_id',
            field=models.FileField(upload_to='files/2024/3/15'),
        ),
    ]
