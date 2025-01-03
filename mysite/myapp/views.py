

from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView, UpdateView, CreateView
from .forms import Product, ProductForm
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Return, Purchase
from .forms import PurchaseForm


class SignUpView(FormView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class ProductListView(ListView):
    model = Product
    template_name = 'main.html'
    context_object_name = 'products'
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(f"Number of products: {context['products'].count()}")
        for product in context['products']:
            print(f"Product ID: {product.id}")
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        form = PurchaseForm(request.POST)

        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            total_price = product.price * quantity

            if product.quantity_in_stock >= quantity and request.user.wallet >= total_price:
                Purchase.objects.create(user=request.user, product=product, quantity=quantity)
                request.user.wallet -= total_price
                request.user.save()
                return HttpResponseRedirect(reverse('main'))
            else:
                message = "Insufficient stock or wallet balance."
                return self.render_to_response({'product': product, 'form': form, 'message': message})
        return self.render_to_response({'product': product, 'form': form})

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_create.html'
    success_url = reverse_lazy('main')

class ProductUpdateView(UpdateView):
    model = Product
    fields = ['name', 'price', 'description', 'quantity_in_stock', 'image']
    template_name = 'product_update.html'
    success_url = reverse_lazy('main')

class ReturnListView(ListView):
    model = Return
    template_name = 'return_list.html'
    context_object_name = 'returns'

    def post(self, request, *args, **kwargs):
        return_request = Return.objects.get(id=request.POST['return_id'])
        if request.POST['action'] == 'approve':
            product = return_request.purchase.product
            product.quantity_in_stock += return_request.purchase.quantity
            product.save()
            return_request.purchase.user.wallet += return_request.purchase.get_total_price()
            return_request.purchase.user.save()
            return_request.purchase.delete()
        return_request.delete()
        return self.get(request, *args, **kwargs)








