from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm 

from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username 
    
# Tạo các bảng 
# class Customer(models.Model):
#     user = models.OneToOneField(User,on_delete=models.SET_NULL,null=True,blank=False )
#     name = models.CharField(max_length=200,null=True)
#     email = models.CharField(max_length=200,null=True)

#     def __str__(self):
#         return self.name

# Bảng Danh Mục 
class Category(models.Model):
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sub_categories', null=True, blank=True)
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null=True)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.name

    
# Bảng sản phẩm 
class Product(models.Model):
    category = models.ManyToManyField(Category, related_name="product")
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    digital = models.BooleanField(default=False, null=True, blank=False)
    detail = models.TextField(null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)  # Thêm trường kích thước
    wood_material = models.CharField(max_length=100, null=True, blank=True)  # Thêm trường chất liệu gỗ
    suitable_space = models.CharField(max_length=100, null=True, blank=True)  # Thêm trường không gian phù hợp

    def __str__(self):
        return self.name

    @property
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    
# Order 

class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Tiền mặt khi nhận hàng'),
        ('online', 'Thanh toán online'),
    ]

    customer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    date_order = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD_CHOICES, null=True)  # Sử dụng choices cho phương thức thanh toán

    def __str__(self):
        return f"Order #{self.id}"

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    
# Order-item 

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=1, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        if self.product:
            return self.product.price * self.quantity
        return 0

# Thông tin mua 
class ShippingAdress(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=200, null=True)  # Tên người nhận
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    stage = models.CharField(max_length=200, null=True)
    mobile = models.CharField(max_length=10, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Trả về tên người nhận nếu có, nếu không có tên thì trả về thông tin địa chỉ giao hàng
        return self.name if self.name else f"Địa chỉ: {self.address}"