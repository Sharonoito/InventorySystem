from django.contrib import admin
from .models import (
  
    Customer, 
    OrderNoDetails, 
    SaleBill, 
    SaleItem,
    SaleBillDetails
)

admin.site.register(Customer)
# admin.site.register(OrderNo)
# admin.site.register(OrderItem)
admin.site.register(OrderNoDetails)
admin.site.register(SaleBill)
admin.site.register(SaleItem)
admin.site.register(SaleBillDetails)