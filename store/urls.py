from django.urls import path

from . import views

urlpatterns = [

    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),

	#Leave as empty string for base url
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),

	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),

]
from django.urls import path
from .views import create_transaction

urlpatterns += [
    path('create-transaction/', create_transaction, name='create_transaction'),
]

from .views import create_transaction

urlpatterns += [
    path('create-transaction/', create_transaction, name='create_transaction'),
]

from .views import create_transaction

urlpatterns += [
    path('create-transaction/', create_transaction, name='create_transaction'),
]

from .views import create_transaction

urlpatterns += [
    path('create-transaction/', create_transaction, name='create_transaction'),
]

from .views import create_transaction

urlpatterns += [
    path('create-transaction/', create_transaction, name='create_transaction'),
]

from django.views.generic import TemplateView

urlpatterns += [
    path('checkout/', TemplateView.as_view(template_name="checkout.html"), name='checkout'),
]
