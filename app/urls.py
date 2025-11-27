from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import ProductList, ProductDetail, ProductSearch
from app import views
from .views import UserList
from .views import ProductCreate
from .views import UserCreate, UserUpdate, UserDelete



urlpatterns = [
    # Các đường dẫn của trang web
    path('', views.home, name="home"),
    path('register/', views.register, name="register"),
    path('login/', views.loginPage, name="login"),
    path('search/', views.search, name="search"),
    path('cart/', views.cart, name="cart"),
    path('update_item/', views.updateItem, name="update_item"),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('category/', views.category, name='category'),
    path('detail/', views.detail, name='detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('myaccount/', views.myaccount_view, name='myaccount'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('order_history/', views.order_history, name='order_history'),



    
    # Các đường dẫn API cho sản phẩm
    path('api/products/', ProductList.as_view(), name='product-list'),  # Lấy tất cả sản phẩm
    path('api/products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),  # Lấy chi tiết sản phẩm theo ID
    path('api/products/search/', ProductSearch.as_view(), name='product-search'),  # Tìm kiếm sản phẩm
    path('api/users/', UserList.as_view(), name='user-list'),  # Đường dẫn lấy danh sách người dùng
    path('api/products/create/', ProductCreate.as_view(), name='product-create'),  # API để tạo mới sản phẩm
    path('api/users/create/', UserCreate.as_view(), name='user-create'),  # API để tạo mới người dùng
    path('api/users/<int:pk>/update/', UserUpdate.as_view(), name='user-update'),  # API để cập nhật thông tin người dùng theo ID
    path('api/users/<int:pk>/delete/', UserDelete.as_view(), name='user-delete'),  # API để xóa người dùng theo ID
]
