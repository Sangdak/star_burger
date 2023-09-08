from django import forms
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Order, OrderItem, Product, Restaurant, RestaurantMenuItem
from restaurateur.services import fetch_coordinates, compute_distance


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('category', 'menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    restaurants = {restaurant.id: restaurant.name for restaurant in Restaurant.objects.all()}
    addresses = {restaurant.id: restaurant.address for restaurant in Restaurant.objects.all()}
    print(restaurants)

    orders = (
        Order.objects.with_cost_in_total().select_related('restaurant')
        .exclude(status=Order.DONE).order_by('registered_at', 'status'))

    restaurants_menus = RestaurantMenuItem.objects.select_related('restaurant', 'product').filter(availability=True).order_by('product')
    restaurants_menus_product_ids = {}
    for menu in restaurants_menus:
        restaurants_menus_product_ids.setdefault(menu.restaurant.id, [])
        restaurants_menus_product_ids[menu.restaurant.id].append(menu.product_id)
    print(restaurants_menus_product_ids)

    for order in orders:
        order.status = dict(Order.STATE_CHOICES)[order.status]
        order.payment_type = (
            'Не выбрано' if order.payment_type == '' else dict(Order.PAYMENT_TYPE_CHOICES)[order.payment_type])

        if not order.restaurant:
            order_items = Order.objects.get(id=order.id).items.select_related('product').all()
            order_items = [item.product.id for item in order_items]

            available_restaurants = []
            for restaurant_id in restaurants.keys():
                if set(order_items).issubset(restaurants_menus_product_ids[restaurant_id]):
                    available_restaurants.append(restaurant_id)

            print(available_restaurants, '=>', order_items)

            customer_coords = fetch_coordinates(settings.YANDEX_GEO_API_KEY, order.address)


            order.restaurants = [restaurants[rest_id] for rest_id in available_restaurants]

            for index, restaurant in enumerate(available_restaurants):
                restaurant_coords = fetch_coordinates(settings.YANDEX_GEO_API_KEY, addresses[restaurant])

                distance = compute_distance(customer_coords, restaurant_coords)
                order.restaurants[index] = f'{restaurants[restaurant]} - {round(distance, 2)} км.'

        else:
            order.restaurants = [order.restaurant, ]

        print(order.restaurants)

    # restaurants_addresses = \
    #     {restaurant['name']: restaurant['address'] for restaurant in Restaurant.objects.all().values('name', 'address')}

    # for order in orders:
    #     order.status = dict(Order.STATE_CHOICES)[order.status]
    #     order.payment_type = 'Не выбрано' if order.payment_type == '' \
    #         else dict(Order.PAYMENT_TYPE_CHOICES)[order.payment_type]
    #
    #     if order.restaurant is None:
    #         order_product_ids = [x.product.id for x in OrderItem.objects.filter(order__id=order.id)]
    #
    #         restaurants_raw = []
    #         for product_id in order_product_ids:
    #             restaurant_ids_by_products = \
    #                 [x.restaurant.id for x in RestaurantMenuItem.objects.filter(product__id=product_id)]
    #             restaurants_raw.append(restaurant_ids_by_products)
    #
    #         restaurants = restaurants_raw[0]
    #         for rest in restaurants_raw[1:]:
    #             restaurants = set(restaurants).intersection(set(rest))
    #
    #         order.restaurants = [Restaurant.objects.get(id=rest_id).name for rest_id in list(restaurants)]
    #
    #         customer_coords = fetch_coordinates(settings.YANDEX_GEO_API_KEY, order.address)
    #
    #         # print('COORD', customer_coords)
    #         for index, restaurant in enumerate(order.restaurants):
    #             restaurant_coords = fetch_coordinates(settings.YANDEX_GEO_API_KEY, restaurants_addresses[restaurant])
    #
    #             distance = compute_distance(customer_coords, restaurant_coords)
    #             order.restaurants[index] = f'{restaurant} - {round(distance, 2)} км.'
    #
    #     else:
    #         order.restaurants = [order.restaurant, ]

    return render(request, template_name='order_items.html', context={
        'order_items': orders,
    })
