from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def with_cost_in_total(self):
        return Order.objects.annotate(
            total_cost=models.Sum(
                models.F('items__quantity') * models.F('items__price')
            ))


class Order(models.Model):
    CREATE = 'CREATE'
    PREPARE = 'PREPARE'
    DELIVER = 'DELIVER'
    DONE = 'DONE'
    STATE_CHOICES = [
        (CREATE, 'Создан'),
        (PREPARE, 'Готовится'),
        (DELIVER, 'Доставляется'),
        (DONE, 'Выполнен'),
    ]

    CASH = 'CASH'
    CARD = 'CARD'
    PAYMENT_TYPE_CHOICES = [
        (CASH, 'Наличные'),
        (CARD, 'Карта'),
    ]

    id = models.BigAutoField(
        primary_key=True,
    )
    status = models.CharField(
        max_length=15,
        choices=STATE_CHOICES,
        default=CREATE,
        verbose_name='Статус заказа',
    )
    payment_type = models.CharField(
        max_length=10,
        choices=PAYMENT_TYPE_CHOICES,
        default='',
        verbose_name='Форма оплаты',
    )
    firstname = models.CharField(
        max_length=30,
        verbose_name='Имя',
    )
    lastname = models.CharField(
        max_length=30,
        verbose_name='Фамилия',
    )
    phonenumber = PhoneNumberField(
        region='RU',
        verbose_name='Телефон',
    )
    address = models.CharField(
        max_length=150,
        verbose_name='Адрес',
    )
    comment = models.TextField(
        blank=True,
        default='',
        verbose_name='Комментарий',
    )
    registered_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Создан',
    )
    called_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Звонок',
    )
    delivered_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Доставлен',
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        indexes = [
            models.Index(fields=[
                'phonenumber',
                'status',
                'registered_at',
                'called_at',
                'delivered_at',
            ])
        ]

    def __str__(self):
        return f'{self.registered_at} - {self.firstname} {self.lastname} {self.address}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар',
    )
    quantity = models.PositiveSmallIntegerField(
        # validators=
        verbose_name='Количество'
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Цена товара',
    )

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f'{self.order}: {self.product} - {self.quantity}'
