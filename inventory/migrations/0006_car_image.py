# Generated by Django 4.2.1 on 2023-06-15 14:17

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_remove_car_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255),
        ),
    ]