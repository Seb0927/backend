# Generated by Django 4.2.1 on 2023-06-28 05:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_merge_20230628_0406'),
        ('order', '0005_bill_detail_id_branch_order_detail_id_branch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order_detail',
            name='id_branch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.branch_article'),
        ),
    ]