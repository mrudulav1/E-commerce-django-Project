from django.shortcuts import render,redirect
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.views import View
import razorpay
from .models import Payment, Product,Customer,Cart
from .forms import CustomerRegisterationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.conf import settings

# Create your views here.
def home(request):
    return render(request,'home.html')

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')



class categoryView(View):
    #display the products
    def get(self,request,val):
        product=Product.objects.filter(category=val)
        title=Product.objects.filter(category=val).values('title')
        return render(request,'category.html',locals())
    
class CategoryTittle(View):
    def get(self,request,val):
        product=Product.objects.filter(title=val)
        title=Product.objects.filter(category=product[0].category).values('title')
        return render(request,'category.html',locals())




class ProductDetails(View):
    def get(self,request,pk):
        product=Product.objects.get(pk=pk)
        return render(request,'productdetails.html',locals())

class CustomerRegistrationView(View):
    def get(self,request):
        form=CustomerRegisterationForm()
        return render(request,'customerregistration.html',locals())
    def post(self,request):
        form=CustomerRegisterationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Congratulations! User register Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request,'customerregistration.html',locals())
class ProfileView(View):
    def get(self,request):
        form=CustomerProfileForm()
        return render(request,'profile.html',locals())
    def post(self,request):
        form=CustomerProfileForm(request.POST)
        if form.is_valid():
            user=request.user
            name=form.cleaned_data['name']
            locality=form.cleaned_data['locality']
            city=form.cleaned_data['city']
            mobile=form.cleaned_data['mobile']
            zipcode=form.cleaned_data['zipcode']
            state=form.cleaned_data['state']

            reg=Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,'Congradulations! profile save Successfully')
        else:
            messages.warning(request,'invalid input data')
        return render(request,'profile.html',locals())
    
def address(request):
    add=Customer.objects.filter(user=request.user)
    return render(request,'address.html',locals())

class UpdateAddress(View):
    def get(self,request,pk):
        add=Customer.objects.get(pk=pk)
        form=CustomerProfileForm(instance=add)
        return render(request,'UpdateAddress.html',locals())

    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data ['name']
            add.locality = form.cleaned_data ['locality']
            add.city = form.cleaned_data ['city']
            add.mobile = form.cleaned_data ['mobile']
            add.state = form.cleaned_data ['state']
            add.zipcode = form.cleaned_data ['zipcode']
            add.save()
            messages.success(request,"Congradulations! Profile Update Successfullly")
        else:
            messages.warning(request,"Invalid Input Data")
        return redirect("address")
    
def add_to_cart(request):
    user=request.user
    product_id=request.GET.get('prod_id')
    product=Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect('/cart/')

# class checkout(View):
#     def post(self,request):
#         print(request.method)
#         user=request.user
#         add=Customer.objects.filter(user=user)
#         cart_items=Cart.objects.filter(user=user)
#         famount=0
#         for p in cart_items:
#             value=p.quantity * p.product.discounted_price
#             famount=famount + value
#         totalamount=famount + 40
#         razoramount=int(totalamount * 100)
#         client=razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
#         data={"amount":razoramount,"currency":"INR","receipt":"order_rcptid_11"}
#         payment_response=client.order.create(data=data)
#         print(payment_response)
#         return render(request,'checkout.html',locals())

class checkout(View):
    def post(self, request):
        try:
            print(request.method)
            user = request.user
            add = Customer.objects.filter(user=user)
            cart_items = Cart.objects.filter(user=user)
            famount = 0
            for p in cart_items:
                value = p.quantity * p.product.discounted_price
                famount += value
            totalamount = famount + 40
            razoramount = int(totalamount * 100)
            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            data = {"amount": razoramount, "currency": "INR", "receipt": "order_rcptid_11"}
            payment_response = client.order.create(data=data)
            payment = Payment(
                user = user,
                amount = totalamount
            )
            payment.save()
            print(payment_response)
            return render(request, 'checkout.html', locals())
        except Exception as e:
            print("Error:", e)
            return HttpResponse("An error occurred during checkout. Please try again later.")
    
    # def post(self,request):
    #     print(request.method)
    #     user=request.user
    #     add=Customer.objects.filter(user=user)
    #     cart_items=Cart.objects.filter(user=user)
    #     famount=0
    #     for p in cart_items:
    #         value=p.quantity * p.product.discounted_price
    #         famount=famount + value
    #     totalamount=famount + 40
    #     razoramount=int(totalamount * 100)
    #     client=razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
    #     data={"amount":razoramount,"currency":"INR","receipt":"order_rcptid_11"}
    #     payment_response=client.order.create(data=data)
    #     print(payment_response)
    #     return render(request,'checkout.html',locals())

def show_cart(request):
    user=request.user
    cart=Cart.objects.filter(user=user)
    amount=0
    for p in cart:
        value=p.quantity * p.product.discounted_price
        amount=amount+value
    totalamount=amount+40
    return render(request,'addtocart.html',locals())


def plus_cart(request):
    if request.method == 'GET':
        print("button clicked")
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
        c.quantity+=1
        c.save()
        print(c)
        user=request.user
        cart=Cart.objects.filter(user=user) #to get card data
        amount=0
        for p in cart:
            value=p.quantity * p.product.discounted_price
            amount=amount+value
        totalamount=amount+40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount

        }
        print(data)
        return JsonResponse(data)


def minus_cart(request):
    print("minus reached")
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
        c.quantity-=1
        c.save()
        print(c)
        user=request.user
        cart=Cart.objects.filter(user=user) #to get card data
        amount=0
        for p in cart:
            value=p.quantity * p.product.discounted_price
            amount=amount+value
        totalamount=amount+40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount

        }
        print(data)
        return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
        c.delete()
        user=request.user
        cart=Cart.objects.filter(user=user) #to get card data
        amount=0
        for p in cart:
            value=p.quantity * p.product.discounted_price
            amount=amount+value
        totalamount=amount+40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount

        }
        return JsonResponse(data)
    


    
