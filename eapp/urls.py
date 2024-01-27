from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_view
from .forms import LoginForm, MyPasswordResetForm,MyPasswordChangeForm


urlpatterns = [
    path("",views.home),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path("category/<slug:val>",views.categoryView.as_view(),name="category"),
    path("category-title/<val>",views.CategoryTittle.as_view(),name="category-title"),
    path("product-details/<int:pk>",views.ProductDetails.as_view(),name="product-details"),
    path('profile/',views.ProfileView.as_view(),name='profile'),
    path('address/',views.address,name='address'),
    path('UpdateAddress/<int:pk>',views.UpdateAddress.as_view(),name='UpdateAddress'),


#login authentication
    path('registration/',views.CustomerRegistrationView.as_view(),name='customerregistration'),
    path('accounts/login/',auth_view.LoginView.as_view(template_name='login.html',authentication_form=LoginForm),name='login'),
    path('password-reset/',auth_view.PasswordResetView.as_view(template_name='password_reset.html',form_class=MyPasswordResetForm ),name='password_reset'),
         
    path('passwordchange/',auth_view.PasswordChangeView.as_view (template_name='changepassword.html',form_class=MyPasswordChangeForm,success_url='passwordchangedone'),name='passwordchange'),
    path('passwordchangedone/',auth_view.PasswordChangeDoneView.as_view(template_name='passwordchangedone.html'),name='passwordchangedone'),

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
