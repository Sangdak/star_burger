# Generated by Django 4.2.3 on 2023-09-04 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(verbose_name='Дата/время обновления')),
                ('address', models.CharField(max_length=150, unique=True, verbose_name='Адрес')),
                ('longitude', models.FloatField(verbose_name='Долгота')),
                ('latitude', models.FloatField(verbose_name='Широта')),
            ],
            options={
                'verbose_name': 'Локация',
                'verbose_name_plural': 'Локации',
                'indexes': [models.Index(fields=['updated_at'], name='location_lo_updated_a974a8_idx')],
            },
        ),
    ]
