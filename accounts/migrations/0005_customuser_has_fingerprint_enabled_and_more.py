# Generated by Django 5.2.1 on 2025-07-13 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_verificationcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='has_fingerprint_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='pin_code',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
