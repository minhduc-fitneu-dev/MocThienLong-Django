from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from .models import *
import json
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth import authenticate, login, logout
import unicodedata
from django.db.models import Q
from fuzzywuzzy import fuzz
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category, Product, Order, OrderItem, ShippingAdress
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer, OrderItemSerializer, ShippingAdressSerializer
from .serializers import UserSerializer
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from .forms import CheckoutForm

# Xác nhận đơn hàng 
from django.shortcuts import render
from .models import Order

from django.contrib import messages

from .forms import CheckoutForm  # Nếu bạn sử dụng form model







# order_confirmation
def order_confirmation(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "Đơn hàng không tồn tại!")
        return redirect('home')  # Quay lại trang chủ nếu không tìm thấy đơn hàng

    context = {
        'order': order,
    }

    return render(request, 'app/order_confirmation.html', context)


# My account
from .forms import UserUpdateForm, ProfileUpdateForm
@login_required
def checkout(request):
    if request.method == 'POST':


        # Lấy thông tin từ form
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        country = request.POST.get('country')
        payment_method = request.POST.get('payment_method')

        # Lấy hoặc tạo đơn hàng cho người dùng
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        
        if order.get_cart_items == 0:
            # Tránh việc tạo đơn hàng nếu giỏ hàng không có sản phẩm
            messages.error(request, "Giỏ hàng của bạn hiện tại trống!")
            return redirect('cart')  # Trở lại trang giỏ hàng nếu giỏ hàng trống
        # Cập nhật thông tin đơn hàng
        order.payment_method = payment_method
        order.complete = True  # Đánh dấu đơn hàng hoàn thành
        order.save()

        # RESET số lượng giỏ hàng trong session
        request.session['cartItems'] = 0
        request.session.modified = True

        # Lưu thông tin giao hàng vào ShippingAdress
        shipping_address = ShippingAdress(
            customer=request.user,
            order=order,
            name=name,  # Lưu tên người mua
            address=address,
            city=city,
            stage=state,
            mobile=phone
        )
        shipping_address.save()

        # Thêm thông báo thành công và chuyển hướng tới trang xác nhận đơn hàng
        messages.success(request, "Đặt hàng thành công!")
        return redirect('order_confirmation', order_id=order.id)  # Chuyển hướng tới trang xác nhận đơn hàng

    # Nếu không có POST, hiển thị form checkout
    order = Order.objects.get(customer=request.user, complete=False)
    items = order.orderitem_set.all()
    context = {
        'order': order,
        'items': items
    }
    return render(request, 'app/checkout.html', context)

# Trang category 

def category(request):
    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category', '')  # Nhận 'category' từ URL query
    
    if active_category:
        # Thay vì category_slug, dùng category__slug để truy vấn theo slug của category
        products = Product.objects.filter(category__slug=active_category)
    else:
        products = Product.objects.all()  # Nếu không có active_category, lấy tất cả sản phẩm
    
    context = {
        'categories': categories,
        'products': products,
        'active_category': active_category,  # Truyền active_category vào context
    }

    return render(request, 'app/category.html', context)

# Trang search
def normalize_text(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def search(request):
    searched = ""
    keys = []

    # Kiểm tra xem yêu cầu có phải là AJAX không
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        searched = request.POST.get("searched", "")
        normalized_query = normalize_text(searched)

        # Tìm kiếm trong tất cả các sản phẩm
        all_products = Product.objects.all()
        keys = [
            p for p in all_products
            if normalized_query in normalize_text(p.name)
        ]

        # Trả kết quả dưới dạng JSON nếu yêu cầu là AJAX
        return JsonResponse({'keys': [{'name': p.name, 'price': p.price, 'image': p.image.url} for p in keys]})
    else:
        # Nếu không phải yêu cầu AJAX, thực hiện tìm kiếm như bình thường
        if request.method == 'POST':
            searched = request.POST.get("searched", "")
            normalized_query = normalize_text(searched)

            all_products = Product.objects.all()
            keys = [
                p for p in all_products
                if normalized_query in normalize_text(p.name)
            ]

        categories = Category.objects.all()  # Lấy tất cả các danh mục
        return render(request, 'app/search.html', {
            "searched": searched,
            "keys": keys,
            "categories": categories  # Truyền danh mục vào context
        })
    

# Chi tiết sản phẩm 
from django.shortcuts import get_object_or_404

def detail(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {"get_cart_items": 0, "get_cart_total": 0}
        cartItems = 0

    id = request.GET.get('id', '')
    product = get_object_or_404(Product, id=id)  # ✅ chỉ lấy 1 sản phẩm duy nhất
    categories = Category.objects.all()

    context = {
        'product': product,  # ✅ truyền 1 biến product, không phải danh sách
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'categories': categories,
    }
    return render(request, 'app/detail.html', context)




# LOGIN VÀ REGISTER




def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Lưu username và password vừa tạo vào session (tạm thời)
            request.session['temp_username'] = form.cleaned_data.get('username')
            request.session['temp_password'] = form.cleaned_data.get('password1')

            messages.success(request, "Tạo tài khoản thành công! Đăng nhập để tiếp tục.")
            return redirect('login')
    return render(request, 'app/register.html', {'form': form})


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')

    # Lấy dữ liệu tạm từ session để autofill
    username = request.session.pop('temp_username', '')
    password = request.session.pop('temp_password', '')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Tên đăng nhập hoặc mật khẩu sai!')

    return render(request, 'app/login.html', {
        'prefill_username': username,
        'prefill_password': password
    })

def home(request):
    products = Product.objects.all()
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        cartItems = 0
    categories = Category.objects.filter(is_sub=False)
    context = {'categories': categories,'products': products, 'cartItems': cartItems}
    return render(request, 'app/home.html', context)





def order_history(request):
    orders = Order.objects.filter(customer=request.user, complete=True)  # Chỉ lấy các đơn hàng đã hoàn tất
    context = {
        'orders': orders,
    }
    return render(request, 'app/order_history.html', context)





# Trang cá nhân
@login_required
def myaccount_view(request):
    user = request.user
    profile = user.profile
    categories = Category.objects.all()

    if request.method == 'POST':
        if 'profile-form' in request.POST:
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, 'Cập nhật thông tin thành công.')
                return redirect('myaccount')
        elif 'account-form' in request.POST:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')

            if user.check_password(current_password):
                if new_password:
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Đổi mật khẩu thành công.')
                    return redirect('myaccount')
                else:
                    messages.error(request, 'Mật khẩu mới không được để trống.')
            else:
                messages.error(request, 'Mật khẩu hiện tại không đúng.')

    u_form = UserUpdateForm(instance=request.user)
    p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'user_form': u_form,
        'profile_form': p_form,
        'categories': categories,
    }
    return render(request, 'app/myaccount.html', context)






def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items  # Đảm bảo gọi dưới dạng thuộc tính (không có dấu ngoặc)
    else:
        items = []
        order = {"get_cart_items": 0, "get_cart_total": 0}
        cartItems = 0

    categories = Category.objects.all()  # Lấy tất cả danh mục sản phẩm
    context = {'items': items, 'order': order, 'cartItems': cartItems, 'categories': categories}
    return render(request, 'app/cart.html', context)



@login_required
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    if orderItem.quantity <= 0:
        orderItem.delete()
    else:
        orderItem.save()

    cartItems = order.get_cart_items  # tính lại đúng số lượng

    return JsonResponse({
    'message': 'Item updated',
    'cartItems': cartItems,
    'productId': product.id,
    'newQuantity': orderItem.quantity if orderItem.quantity > 0 else 0,
})






# Trang về chúng tôi
def about(request):
    categories = Category.objects.all()  # Lấy tất cả danh mục sản phẩm
    context = {'categories': categories}  # Truyền danh mục vào context
    return render(request, 'app/about.html', context)

def contact(request):
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')

        # Kiểm tra nếu tất cả các trường đều hợp lệ
        if name and email and subject and message:
            try:
                # Gửi email
                send_mail(
                    f'Contact Us - {subject}',  # Tiêu đề email
                    f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}',  # Nội dung email
                    email,  # Email người gửi
                    ['your-email@example.com'],  # Thay đổi email này thành email của bạn
                    fail_silently=False,  # Nếu có lỗi sẽ ném ngoại lệ
                )
                return HttpResponse("Thank you for contacting us!")  # Thông báo thành công
            except Exception as e:
                return HttpResponse(f"An error occurred: {str(e)}")  # Thông báo lỗi
        else:
            return HttpResponse("All fields are required!")  # Thông báo thiếu thông tin

    categories = Category.objects.all()  # Lấy tất cả danh mục sản phẩm
    context = {'categories': categories}  # Truyền danh mục vào context
    return render(request, 'app/contact.html', context)  # Render lại form khi chưa submit




























# API 
# API lấy tất cả Category
class CategoryList(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

# API lấy tất cả Product
class ProductList(APIView):
    def get(self, request):
        products = Product.objects.all()  # Lấy tất cả sản phẩm
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)  # Trả về danh sách sản phẩm dưới dạng JSON

# API tạo mới Product
class ProductCreate(APIView):
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Lưu sản phẩm vào cơ sở dữ liệu
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # Trả về dữ liệu sản phẩm vừa thêm
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Nếu dữ liệu không hợp lệ, trả về lỗi
    
# views.py
class ProductDetail(APIView):
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)  # Tìm sản phẩm theo ID
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)  # Nếu không tìm thấy, trả về lỗi 404
        serializer = ProductSerializer(product)
        return Response(serializer.data)  # Trả về thông tin chi tiết sản phẩm

    

class ProductSearch(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')  # Lấy từ tham số query của URL
        if query:
            products = Product.objects.filter(name__icontains=query)  # Tìm kiếm sản phẩm
        else:
            products = Product.objects.all()  # Nếu không có query, trả về tất cả sản phẩm
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
class UserList(APIView):
    def get(self, request):
        users = User.objects.all()  # Lấy tất cả người dùng từ cơ sở dữ liệu
        serializer = UserSerializer(users, many=True)  # Serialize danh sách người dùng
        return Response(serializer.data)  # Trả về danh sách người dùng dưới dạng JSON

class UserCreate(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Lưu người dùng vào cơ sở dữ liệu
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # Trả về dữ liệu người dùng vừa tạo
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Nếu dữ liệu không hợp lệ, trả về lỗi

class UserUpdate(APIView):
    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()  # Lưu thông tin đã cập nhật
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDelete(APIView):
    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)  # Tìm người dùng theo ID
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)  # Nếu không tìm thấy người dùng, trả về lỗi 404

        user.delete()  # Xóa người dùng khỏi cơ sở dữ liệu
        return Response(status=status.HTTP_204_NO_CONTENT)  # Trả về mã trạng thái 204 nếu xóa thành công