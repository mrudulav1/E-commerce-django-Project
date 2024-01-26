from django.shortcuts import render,redirect
from django.db.models import Count
# from django.http import HttpResponse
from django.views import View
from .models import Product,Customer
from .forms import CustomerRegisterationForm,CustomerProfileForm
from django.contrib import messages
# from django.http import HttpResponse


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
        form=CustomerProfileForm(request.POST)
        if form.is_valid():
            add=Customer.objects.get(pk=pk)
            add.name=form.changed_data['name']
            add.locality=form.changed_data['locality']
            add.city=form.changed_data['city']
            add.mobile=form.changed_data['mobile']
            add.state=form.changed_data['state']
            add.zipcode=form.changed_data['zipcode']
            add.save()
            messages.success(request,"Congradulations! Profile Update Successfullly")
        else:
            messages.warning(request,"Invalid Input Data")
        return redirect('address')




