# Generated by Django 5.0.3 on 2024-06-13 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_payment_paynow_poll_url_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointment',
            old_name='appointment_end_datetime',
            new_name='end',
        ),
        migrations.RenameField(
            model_name='appointment',
            old_name='appointment_start_datetime',
            new_name='start',
        ),
        migrations.AlterField(
            model_name='applicantdetails',
            name='birth_certificate',
            field=models.FileField(upload_to='files/2024/6/13'),
        ),
        migrations.AlterField(
            model_name='applicantdetails',
            name='national_id',
            field=models.FileField(upload_to='files/2024/6/13'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='venue',
            field=models.CharField(choices=[('Harare', 'Harare'), ('Gweru', 'Gweru'), ('Mberengwa', 'Mberengwa'), ('Bulawayo', 'Bulawayo'), ('Masvingo', 'Masvingo')], max_length=255),
        ),
    ]