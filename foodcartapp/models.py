from django.db import models
from django.core.validators import MinValueValidator

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


class Order(models.Model):
    first_name = models.CharField('имя', max_length=30)
    last_name = models.CharField('фамилия', max_length=30)
    phonenumber = PhoneNumberField('телефон', db_index=True)
    address = models.CharField('адрес', max_length=100)


    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'


    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.address}'

    
class OrderDetails(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE, 
        related_name='orders', 
        verbose_name='заказ'
        )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='products', 
        verbose_name='продукты'
        )
    quantity = models.IntegerField('количество', validators=[MinValueValidator(1)])
    fixed_price = models.DecimalField(
        'фиксированная цена',
        null=True,
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
        )

    class Meta:
        verbose_name = 'детали заказа'
        verbose_name_plural = 'детали заказов'

    def __str__(self):
        return f'{self.product.name} {self.order.first_name} {self.order.last_name}'
        