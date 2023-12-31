# Generated by Django 4.2.1 on 2023-06-26 21:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_car_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='color',
        ),
        migrations.RemoveField(
            model_name='article',
            name='stock',
        ),
        migrations.AddField(
            model_name='article',
            name='deleted',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='branch_article',
            name='color',
            field=models.CharField(default=None, max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='branch_article',
            name='stock',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='car',
            name='id_article',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.article'),
        ),
        migrations.AlterField(
            model_name='replacement',
            name='id_article',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.article'),
        ),
    ]
