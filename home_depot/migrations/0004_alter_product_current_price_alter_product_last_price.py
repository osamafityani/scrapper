# Generated by Django 4.2.4 on 2023-08-04 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_depot', '0003_remove_product_model_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='current_price',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='last_price',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=20, null=True),
        ),
    ]