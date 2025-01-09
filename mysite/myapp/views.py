



from django.urls import reverse_lazy,reverse
from django.views import View
from django.views.generic.edit import FormView, UpdateView, CreateView
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from .models import Return, Purchase, Product, User
from .forms import PurchaseForm, UserCreationForm,ProductForm
from django.contrib.auth import login,logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.timezone import now
from datetime import timedelta





@login_required(login_url='/login/')
def profile_view(request):
    user = request.user
    thirty_minutes_ago = now() - timedelta(minutes=30)
    Purchase.objects.filter(user=user, created_at__lt=thirty_minutes_ago).delete()
    Return.objects.filter(user=user, created_at__lt=thirty_minutes_ago).delete()
    purchases = Purchase.objects.filter(user=user)
    returns = Return.objects.filter(user=user)
    return render(request, 'profile.html', {
        'wallet': user.wallet,
        'purchases': purchases,
        'returns': returns,
        'current_time': now(),
    })

def custom_logout(request):
    logout(request)
    return redirect('main')


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
        if not request.user.is_authenticated:
            messages.error(request, "Вы должны быть авторизованы для совершения покупки.")
            return HttpResponseRedirect(reverse('login'))

        product = self.get_object()
        form = PurchaseForm(request.POST, product=product, user=request.user)

        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.user = request.user
            purchase.product = product

            quantity = form.cleaned_data['quantity']
            total_price = product.price * quantity


            if request.user.wallet < total_price:
                messages.error(request, "У вас недостаточно средств для покупки.")
                return self.render_to_response(self.get_context_data(form=form))


            if quantity > product.quantity_in_stock:
                messages.error(request, "Недостаточно товара на складе.")
                return self.render_to_response(self.get_context_data(form=form))


            purchase.save()
            product.reduce_stock(quantity)
            request.user.update_wallet(-total_price)

            messages.success(request, "Покупка успешно совершена!")
            return HttpResponseRedirect(reverse('profile'))
        else:
            messages.error(request, "Произошла ошибка при оформлении покупки.")
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['form'] = PurchaseForm(product=self.object, user=self.request.user)
        else:
            context['form'] = PurchaseForm()
        return context


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



class UserRegisterView(FormView):
    template_name = 'register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()
        login(self.request, user)
        messages.success(self.request, "Регистрация прошла успешно!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Произошла ошибка при регистрации.")
        return super().form_invalid(form)


def request_return(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id, user=request.user)


    time_since_purchase = now() - purchase.created_at
    if time_since_purchase.total_seconds() > 180:
        messages.error(request, "Возврат невозможен, так как прошло более 3 минут с момента покупки.")
        return redirect('profile')


    if purchase.returned:
        messages.error(request, "Этот товар уже был возвращен.")
    else:
        Return.objects.create(user=request.user, product=purchase.product, quantity=purchase.quantity, purchase=purchase)
        purchase.returned = True
        purchase.save()
        messages.success(request, "Запрос на возврат успешно создан и ожидает подтверждения администратора.")

    return redirect('profile')


class ReturnActionMixin:
    def get_return_request(self, return_id):
        try:
            return Return.objects.get(id=return_id)
        except Return.DoesNotExist:
            messages.error(self.request, "Запрос на возврат не найден.")
            return None

    def approve_return(self, return_request):
        product = return_request.purchase.product
        product.quantity_in_stock += return_request.purchase.quantity
        product.save()


        return_request.purchase.user.wallet += return_request.purchase.get_total_price()
        return_request.purchase.user.save()


        return_request.purchase.delete()
        return_request.delete()

    def reject_return(self, return_request):
        return_request.delete()

class ReturnListView(UserPassesTestMixin, ListView):
    model = Return
    template_name = 'return_list.html'
    context_object_name = 'returns'

    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request, *args, **kwargs):
        return_id = request.POST.get('return_id')
        action = request.POST.get('action')
        try:
            return_request = Return.objects.get(id=return_id)
            if action == 'approve':
                self.approve_return(return_request)
                messages.success(request, "Return approved successfully.")
            elif action == 'reject':
                self.reject_return(return_request)
                messages.success(request, "Return rejected.")
        except Return.DoesNotExist:
            messages.error(request, "Return request not found.")
        return redirect('return_list')

    def approve_return(self, return_request):
        product = return_request.purchase.product
        product.quantity_in_stock += return_request.purchase.quantity
        product.save()
        user = return_request.purchase.user
        user.wallet += return_request.purchase.get_total_price()
        user.save()
        return_request.purchase.delete()
        return_request.delete()

    def reject_return(self, return_request):
        return_request.delete()



class Login(LoginView):
    success_url = '/'
    template_name = 'login.html'

    def get_success_url(self):
        return self.success_url

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


