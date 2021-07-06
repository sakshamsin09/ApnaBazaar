from django.shortcuts import render, redirect
from django.views import View
from .models import Customer, Product, Cart, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required   #for function base views
from django.utils.decorators import method_decorator    #for class based views

# def home(request):
#  return render(request, 'app/home.html')
class ProductView(View):
    def get(self, request):
        topwears = Product.objects.filter(category='TW')
        bottomwears = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='M')
        return render(request, 'app/home.html', 
        {'topwears':topwears, 'bottomwears':bottomwears, 'mobiles':mobiles})

# def product_detail(request):
#  return render(request, 'app/productdetail.html')
class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        item_in_cart = False
        if request.user.is_authenticated:
            item_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        return render(request, 'app/productdetail.html', {'product':product, 'item_in_cart':item_in_cart})



def change_password(request):
 return render(request, 'app/changepassword.html')


def mobile(request, data=None):
    if data==None:
        mobiles = Product.objects.filter(category='M')
    elif (data.lower()=='samsung' or data.lower()=="apple"):
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data=='below':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__lt=10000)  
    elif data=='above':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__gt=10000)      
    return render(request, 'app/mobile.html', {'mobiles':mobiles})

# def login(request):
#  return render(request, 'app/login.html')

# def customerregistration(request):
#  return render(request, 'app/customerregistration.html')
class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form':form})
    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Registered Successfully')
            form.save()
        return render(request, 'app/customerregistration.html', {'form':form})

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'}) 
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid(): 
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            zipcode = form.cleaned_data['zipcode']
            state = form.cleaned_data['state']
            reg = Customer(user=user, name=name, locality=locality, city=city, zipcode=zipcode, state=state)
            reg.save()
            messages.success(request, 'Profile Updated! Successfully')
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})    
@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'address':add, 'active':'btn-primary'})
@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    obj = Cart(user=user, product=product)
    obj.save()
    return redirect('/cart')
@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        shipping_amount = 70.0
        amount = 0.0
        total_amount = 0.0
        # cart_product = [ for p in Cart.objects.all() if p.user == user]
        # print(cart_product)
        for pro in cart:
            amount+=(pro.quantity * pro.product.discounted_price)
        total_amount = amount+shipping_amount    
        # print(total_amount)
        if amount==0:
            return render(request, 'app/emptycart.html')
        return render(request, 'app/addtocart.html', {'carts':cart, 'totam':total_amount, 'amount':amount})
def plus_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        shipping_amount = 70.0
        amount = 0.0
        total_amount = 0.0
        for pro in cart:
            amount+=(pro.quantity * pro.product.discounted_price)
        total_amount = amount+shipping_amount    
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'total_amount':total_amount
        }
        return JsonResponse(data)
def minus_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        shipping_amount = 70.0
        amount = 0.0
        total_amount = 0.0
        for pro in cart:
            amount+=(pro.quantity * pro.product.discounted_price)
        total_amount = amount+shipping_amount    
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'total_amount':total_amount
        }
        return JsonResponse(data)
def remove_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        user = request.user
        cart = Cart.objects.filter(user=user)
        shipping_amount = 70.0
        amount = 0.0
        total_amount = 0.0
        for pro in cart:
            amount+=(pro.quantity * pro.product.discounted_price)
        total_amount = amount+shipping_amount    
        data = {
            'amount': amount,
            'total_amount':total_amount
        }
        return JsonResponse(data)        
@login_required
def checkout(request):
    user = request.user
    address = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    shipping_amount = 70.0
    amount = 0.0
    total_amount = 0.0
    for pro in cart_items:
        amount+=(pro.quantity * pro.product.discounted_price)
    total_amount = amount+shipping_amount   
    return render(request, 'app/checkout.html', {'address':address, 'total_amount':total_amount, 'cart_items':cart_items})
@login_required
def placeorder(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for item in cart:
        OrderPlaced(user=user, customer=customer, product=item.product, quantity=item.quantity).save()
        item.delete()
    return redirect('/orders')    

@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'ordered_placed':op})

def buy_now(request):
 return render(request, 'app/buynow.html')


