"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from myapp.views import ProductListView,ProductDetailView,  ProductCreateView, ProductUpdateView,ReturnListView,Login,UserRegisterView,custom_logout,profile_view,request_return, product_list

urlpatterns = [
path('product/return/<int:pk>/', ReturnListView.as_view(), name='return_list'),
    path('return_purchase/<int:purchase_id>/', request_return, name='return_purchase'),
path('products/', product_list, name='product_list'),
    path('profile/', profile_view, name='profile'),
    path('', ProductListView.as_view(), name='main'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('produkt/create/', ProductCreateView.as_view(), name='product_create'),
    path('produkt/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('returns/', ReturnListView.as_view(), name='return_list'),
path('login/', Login.as_view(), name='login'),
path('register/', UserRegisterView.as_view(), name='register'),
path('logout/', custom_logout, name='logout'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



