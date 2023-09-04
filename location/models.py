from django.db import models


class Location(models.Model):
    updated_at = models.DateTimeField(
        verbose_name='Дата/время обновления',
    )
    address = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Адрес',
    )
    longitude = models.FloatField(
        verbose_name='Долгота',
    )
    latitude = models.FloatField(
        verbose_name='Широта',
    )

    class Meta:
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'
        indexes = [
            models.Index(fields=['updated_at'])
        ]

    def __str__(self):
        return f'{self.address} - ({self.longitude},{self.latitude})'
