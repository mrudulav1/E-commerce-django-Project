from django.shortcuts import render
from django.db.models import Count
# from django.http import HttpResponse
from django.views import View
from .models import Product
from .forms import CustomerRegisterationForm
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
            messages.error(request,"Invalid Input Data")
        return render(request,'customerregistration.html',locals())
