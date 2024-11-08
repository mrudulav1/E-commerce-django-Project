from django.shortcuts import render,redirect
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.views import View
import razorpay
from .models import OrderPlaced, Payment, Product,Customer,Cart,Wishlist
from .forms import CustomerRegisterationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.decorators import login_required


# Create your views here.
def home(request):
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request,'home.html',locals())

def about(request):
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request,'about.html',locals())

def contact(request):
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request,'contact.html',locals())



class categoryView(View):
    #display the products
    def get(self,request,val):
        totalitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
        product=Product.objects.filter(category=val)
        title=Product.objects.filter(category=val).values('title')
        return render(request,'category.html',locals())
    
class CategoryTittle(View):
    def get(self,request,val):
        product=Product.objects.filter(title=val)
        title=Product.objects.filter(category=product[0].category).values('title')
        totalitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
        return render(request,'category.html',locals())




class ProductDetails(View):
    def get(self,request,pk):
        product=Product.objects.get(pk=pk)
        wishlist = Wishlist.objects.filter(Q(product=product) & Q(user=request.user)).exists()
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()
        return render(request, 'productdetails.html', {'product': product, 'wishlist': wishlist, 'totalitem': totalitem})

class CustomerRegistrationView(View):
    def get(self,request):
        form=CustomerRegisterationForm()
        totalitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
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
        totalitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
        return render(request,'profile.html',locals())


        # form=CustomerProfileForm()
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
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        add=Customer.objects.filter(user=request.user)
    return render(request,'address.html',locals())

class UpdateAddress(View):
    def get(self,request,pk):
        add=Customer.objects.get(pk=pk)
        form=CustomerProfileForm(instance=add)
        totalitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
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



from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class checkout(View):
    def get(self, request):
        totalitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
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
            order_id=payment_response['id']
            order_status = payment_response['status']

            if order_status=='created':
                payment = Payment(
                    user = user,
                    amount = totalamount,
                    razorpay_order_id = order_id,
                    razorpay_payment_status=order_status

                )
                payment.save()
                print(payment_response)
            return render(request, 'checkout.html', locals())
        except Exception as e:
            print("Error:", e)
            return HttpResponse("An error occurred during checkout. Please try again later.")
        




def paymentdone(request):
    print(" paymentdone view reached")
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    cust_id = request.GET.get('cust_id')

    print(cust_id,payment_id,order_id)
    user = request.user
    customer = Customer.objects.get(id=cust_id)
    payment = Payment.objects.get(razorpay_order_id = order_id)
    payment.paid = True
    payment.razorpay_payment_id = payment_id
    payment.save()
    print("paymet saved")
    
    print(user)

    user_id = user.id
    print(user_id)

    cart = Cart.objects.filter(user=user_id)
    
    

    for c in cart:
        print(c)
        purchase=OrderPlaced (
            user = user,
            customer = customer,
            product= c.product,
            quantity = c.quantity,
            payment = payment
            )
        purchase.save()
        print(purchase)
        c.delete()

    return redirect('orders')




def show_cart(request):
    user=request.user
    cart=Cart.objects.filter(user=user)
    amount=0
    for p in cart:
        value=p.quantity * p.product.discounted_price
        amount=amount+value
    totalamount=amount+40
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request,'addtocart.html',locals())



def orders(request):
    totalitem=0
    print("view reached")
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        print(request.user)
        order_placed=OrderPlaced.objects.filter(user=request.user)
    else:
        print("user not authenticated")
    context = {
        'order_placed': order_placed
    }
    print(context)
    return render(request,'orders.html',context)





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
    
def plus_wishlist(request):
    print("data : ",request)
    print("clicked")
    if request.method == 'POST':
        prod_id = request.POST.get('prod_id')
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist.objects.create(user=user, product=product)
        data = {
            'message': 'Wishlist Added Successfully',
        }
        return JsonResponse(data)
    

def minus_wishlist(request):
    if request.method=='GET':
        prod_id=request.GET['prod_id']
        product=Product.objects.get(id=prod_id)
        user=request.user
        Wishlist.objects.filter(user=user,product=product).delete()
        data={
            'message':'Wishlist Remove Successfully',
        }
        return JsonResponse(data)

    


    