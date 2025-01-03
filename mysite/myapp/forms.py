from django import forms
from .models import Product, User, Return

class PurchaseForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)


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

class UserForm(forms.Form):
    class Meta:
        model = User
        fields = ['username', 'password']

class CreateProduct(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'quantity_in_stock', 'image']

class ReturnRequestForm(forms.ModelForm):
    class Meta:
        model = Return
        fields = ['purchase']