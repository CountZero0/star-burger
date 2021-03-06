from django.http import JsonResponse
from django.templatetags.static import static
import json

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, OrderDetails, Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order_data = request.data
    if 'products' not in order_data:
        content = {'error': 'no products'}
        return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

    if order_data['products'] is None:
        content = {'error': 'products key empty'}
        return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

    if not order_data['products']:
        content = {'error': 'products list empty'}
        return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
        
    if not isinstance(order_data['products'], list):
        content = {'error': 'products key not list'}
        return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

    order = Order.objects.create(
        first_name=order_data['firstname'],
        last_name=order_data['lastname'],
        phonenumber=order_data['phonenumber'],
        address=order_data['address']
    )

    for order_item in order_data['products']:
        OrderDetails.objects.create(
            order=order,
            product=Product.objects.get(pk=order_item['product']),
            quantity=order_item['quantity']
        )

    return Response(order_data)