# Generated by Django 4.2.3 on 2023-08-21 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_remove_order_foodcartapp_phonenu_5f4ceb_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, default='', verbose_name='Комментарий'),
        ),
    ]
