from django import forms
from .models import Product, User, Return, Purchase




class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'quantity_in_stock', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'quantity_in_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['image']

class AddProduct(forms.Form):
    name = forms.CharField(max_length=200)
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    description = forms.CharField(max_length=1000, widget=forms.Textarea)
    quantity_in_stock = forms.IntegerField(min_value=0)
    image = forms.ImageField(required=False)

class UpdateProduct(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'quantity_in_stock', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'quantity_in_stock': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
        }



class ReturnProduct(forms.Form):
    quantity = forms.IntegerField(min_value=1)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity'].widget.attrs['class'] = 'form-control'



class CreateProduct(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'quantity_in_stock', 'image']

class ReturnRequestForm(forms.ModelForm):
    class Meta:
        model = Return
        fields = ['purchase']

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "email",)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user



class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['quantity']

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')


        if self.product and quantity > self.product.quantity_in_stock:
            raise forms.ValidationError("Недостаточное количество товара на складе.")


        if self.user and self.user.wallet < (self.product.price * quantity):
            raise forms.ValidationError("Недостаточно средств в кошельке.")

        return quantity
