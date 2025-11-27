from rest_framework import serializers
from .models import Category, Product, Order, OrderItem, ShippingAdress
from django.contrib.auth.models import User
# Serializer cho Category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

# Serializer cho Product
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)  # Liên kết với Category
    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'price', 'image', 'digital', 'detail', 'ImageURL']
# Serializer cho OrderItem
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  # Liên kết với Product
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'order', 'quantity', 'date_added', 'get_total']

# Serializer cho Order
class OrderSerializer(serializers.ModelSerializer):
    orderitem_set = OrderItemSerializer(many=True)  # Liên kết với OrderItem
    class Meta:
        model = Order
        fields = ['id', 'customer', 'date_order', 'complete', 'transaction_id', 'get_cart_items', 'get_cart_total', 'orderitem_set']

# Serializer cho ShippingAdress
class ShippingAdressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAdress
        fields = ['id', 'customer', 'order', 'adress', 'city', 'stage', 'mobile', 'date_added']
# serializers.py


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'write_only': True}  # Đảm bảo mật khẩu chỉ được ghi vào
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)  # Tạo người dùng với mật khẩu đã được mã hóa
        return user