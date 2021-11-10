from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('customers/', views.CustomerListView.as_view(), name='customers-list'),
    path('customers//new', views.CustomerView.as_view(), name='new-cusomer'),
    path('customers//<pk>/edit', views.CustomerUpdateView.as_view(), name='edit-cusomer'),
    path('customers//<pk>/delete', views.CustomerDeleteView.as_view(), name='delete-cusomer'),
    path('customers//<name>', views.CustomerView.as_view(), name='cusomer'),

    # path('orders/', views.OrderView.as_view(), name='orders-list'), 
    path('orders/new', views.SelectCustomerView.as_view(), name='select-customer'), 
    path('orders/new/<pk>', views.OrderCreateView.as_view(), name='new-order'),    
    path('orders/<pk>/delete', views.OrderDeleteView.as_view(), name='delete-order'),
    
    path('sales/', views.SaleView.as_view(), name='sales-list'),
    path('sales/new', views.SaleCreateView.as_view(), name='new-sale'),
    path('sales/<pk>/delete', views.SaleDeleteView.as_view(), name='delete-sale'),

    path("orders/<billno>", views.OrderNoView.as_view(), name="order-no"),
    path("sales/<billno>", views.SaleBillView.as_view(), name="sale-bill"),
]