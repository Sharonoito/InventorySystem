from django.db import models
from inventory.models import Stock

#contains customer
class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=12, unique=True)
    address = models.CharField(max_length=200)
    email = models.EmailField(max_length=254, unique=True)
    gstin = models.CharField(max_length=15, unique=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
	    return self.name


#contains the Orders made
class OrderNo(models.Model):
    billno = models.AutoField(primary_key=True)
    time = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name='ordercustomer')

    def __str__(self):
	    return "Order no: " + str(self.orderno)

    def get_items_list(self):
        return OrderItem.objects.filter(orderno=self)

    def get_total_price(self):
        orderitems = Ordertem.objects.filter(orderno=self)
        total = 0
        for item in orderitems:
            total += item.totalprice
        return total

#contains the order stocks made
class OrderItem(models.Model):
    orderno = models.ForeignKey(OrderNo, on_delete = models.CASCADE, related_name='orderno')
    stock = models.ForeignKey(Stock, on_delete = models.CASCADE, related_name='orderitem')
    quantity = models.IntegerField(default=1)
    perprice = models.IntegerField(default=1)
    totalprice = models.IntegerField(default=1)

    def __str__(self):
	    return "Order no: " + str(self.orderno.orderno) + ", Item = " + self.stock.name

#contains the other details in the order no
class OrderNoDetails(models.Model):
    billno = models.ForeignKey(OrderNo, on_delete = models.CASCADE, related_name='orderetailsno')
    
    eway = models.CharField(max_length=50, blank=True, null=True)    
    veh = models.CharField(max_length=50, blank=True, null=True)
    destination = models.CharField(max_length=50, blank=True, null=True)
    po = models.CharField(max_length=50, blank=True, null=True)
    
    cgst = models.CharField(max_length=50, blank=True, null=True)
    sgst = models.CharField(max_length=50, blank=True, null=True)
    igst = models.CharField(max_length=50, blank=True, null=True)
    cess = models.CharField(max_length=50, blank=True, null=True)
    tcs = models.CharField(max_length=50, blank=True, null=True)
    total = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
	    return "Order no: " + str(self.orderno.orderno)


#contains the sale bills made
class SaleBill(models.Model):
    orderno = models.AutoField(primary_key=True)
    time = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    gstin = models.CharField(max_length=15)

    def __str__(self):
	    return "Order no: " + str(self.orderno)

    def get_items_list(self):
        return SaleItem.objects.filter(orderno=self)
        
    def get_total_price(self):
        saleitems = SaleItem.objects.filter(orderno=self)
        total = 0
        for item in saleitems:
            total += item.totalprice
        return total

#contains the sale stocks made
class SaleItem(models.Model):
    orderno = models.ForeignKey(SaleBill, on_delete = models.CASCADE, related_name='salebillno')
    stock = models.ForeignKey(Stock, on_delete = models.CASCADE, related_name='saleitem')
    quantity = models.IntegerField(default=1)
    perprice = models.IntegerField(default=1)
    totalprice = models.IntegerField(default=1)

    def __str__(self):
	    return "Order no: " + str(self.orderno.orderno) + ", Item = " + self.stock.name

#contains the other details in the sales bill
class SaleBillDetails(models.Model):
    orderno = models.ForeignKey(SaleBill, on_delete = models.CASCADE, related_name='saledetailsorderno')
    
    eway = models.CharField(max_length=50, blank=True, null=True)    
    veh = models.CharField(max_length=50, blank=True, null=True)
    destination = models.CharField(max_length=50, blank=True, null=True)
    po = models.CharField(max_length=50, blank=True, null=True)
    
    cgst = models.CharField(max_length=50, blank=True, null=True)
    sgst = models.CharField(max_length=50, blank=True, null=True)
    igst = models.CharField(max_length=50, blank=True, null=True)
    cess = models.CharField(max_length=50, blank=True, null=True)
    tcs = models.CharField(max_length=50, blank=True, null=True)
    total = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
	    return "Order no: " + str(self.orderno.billno)
