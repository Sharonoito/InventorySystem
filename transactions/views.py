from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    View, 
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import (
    OrderNo, 
    Customer, 
    OrderItem,
    OrderNoDetails,
    SaleBill,  
    SaleItem,
    SaleBillDetails
)
from .forms import (
    SelectCustomerForm, 
    OrderItemFormset,
    # OrderDetailsForm, 
    CustomerForm, 
    SaleForm,
    SaleItemFormset,
    SaleDetailsForm
)
from inventory.models import Stock




# shows a lists of all Customer
class CustomerListView(ListView):
    model = Customer
    template_name = "customers/customers_list.html"
    queryset = Customer.objects.filter(is_deleted=False)
    paginate_by = 10


# used to add a new customer
class SupplierCreateView(SuccessMessageMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    success_url = '/transactions/customer'
    success_message = "Customer has been created successfully"
    template_name = "customer/edit_supplier.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Customer'
        context["savebtn"] = 'Add Customer'
        return context     


# used to update a customer's info
class CustomerUpdateView(SuccessMessageMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    success_url = '/transactions/customer'
    success_message = "Customer details has been updated successfully"
    template_name = "customers/edit_customer.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Customer'
        context["savebtn"] = 'Save Changes'
        context["delbtn"] = 'Delete Customer'
        return context


# used to delete a Customer
class CustomerDeleteView(View):
    template_name = "customers/delete_customer.html"
    success_message = "Customer has been deleted successfully"

    def get(self, request, pk):
       customer = get_object_or_404(Customer, pk=pk)
       return render(request, self.template_name, {'object' : Customer})

    def post(self, request, pk):  
        customer = get_object_or_404(Supplier, pk=pk)
        customer.is_deleted = True
        customer.save()                                               
        messages.success(request, self.success_message)
        return redirect('customer-list')


# used to view a customer's profile
class CustomerView(View):
    def get(self, request, name):
        customerobj = get_object_or_404(Customer, name=name)
        bill_list = OrderNo.objects.filter(customer=customerobj)
        page = request.GET.get('page', 1)
        paginator = Paginator(bill_list, 10)
        try:
            bills = paginator.page(page)
        except PageNotAnInteger:
            bills = paginator.page(1)
        except EmptyPage:
            bills = paginator.page(paginator.num_pages)
        context = {
            'customer'  : customerobj,
            'bills'     : bills
        }
        return render(request, 'customer/customer.html', context)




# shows the list of bills of all customer
class CustomerView(ListView):
    model = OrderNo
    template_name = "orders/orders_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10


# used to select the customer
class SelectCustomerView(View):
    form_class = SelectCustomerForm
    template_name = 'orders/select_orders.html'

    def get(self, request, *args, **kwargs):                                   
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):                                   
        form = self.form_class(request.POST)
        if form.is_valid():
            customerid = request.POST.get("customer")
            customer = get_object_or_404(Customer, id=Customerid)
            return redirect('new-order', customer.pk)
        return render(request, self.template_name, {'form': form})



class OrderCreateView(View):                                                 
    template_name = 'order/new_order.html'

    def get(self, request, pk):
        formset = OrdertemFormset(request.GET or None)                     
        orderobj = get_object_or_404(Order, pk=pk)                       
        context = {
            'formset'   : formset,
            'order'  : orderobj,
        }                                                                      
        return render(request, self.template_name, context)

    def post(self, request, pk):
        formset = OrderItemFormset(request.POST)                            
        orderobj = get_object_or_404(Order, pk=pk)                        
        if formset.is_valid():
            # saves bill
            billobj = OrderBill(order=orderobj)                       
            billobj.save()                                                     
            # create bill details object
            billdetailsobj = OrderBillDetails(billno=billobj)
            billdetailsobj.save()
            for form in formset:                                               
                # false saves the item and links bill to the item
                billitem = form.save(commit=False)
                billitem.billno = billobj                                      
                # gets the stock item
                stock = get_object_or_404(Stock, name=billitem.stock.name)      
                # calculates the total price
                billitem.totalprice = billitem.perprice * billitem.quantity
                # updates quantity in stock db
                stock.quantity += billitem.quantity                              
                stock.save()
                billitem.save()
            messages.success(request, "Orderitems have been registered successfully")
            return redirect('order-bill', billno=billobj.billno)
        formset = OrderItemFormset(request.GET or None)
        context = {
            'formset'   : formset,
            'order'  : orderobj
        }
        return render(request, self.template_name, context)



class OrderDeleteView(SuccessMessageMixin, DeleteView):
    model = OrderNo
    template_name = "ordersdelete_orders.html"
    success_url = '/transactions/orders'
    
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = OrderItem.objects.filter(bilno=self.object.billno)
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name)
            if stock.is_deleted == False:
                stock.quantity -= item.quantity
                stock.save()
        messages.success(self.request, "Order bill has been deleted successfully")
        return super(OrderDeleteView, self).delete(*args, **kwargs)




# shows the list of bills of all sales 
class SaleView(ListView):
    model = SaleBill
    template_name = "sales/sales_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10


# used to generate a bill object and save items
class SaleCreateView(View):                                                      
    template_name = 'sales/new_sale.html'

    def get(self, request):
        form = SaleForm(request.GET or None)
        formset = SaleItemFormset(request.GET or None)                          # renders an empty formset
        stocks = Stock.objects.filter(is_deleted=False)
        context = {
            'form'      : form,
            'formset'   : formset,
            'stocks'    : stocks
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = SaleForm(request.POST)
        formset = SaleItemFormset(request.POST)                                 # recieves a post method for the formset
        if form.is_valid() and formset.is_valid():
            # saves bill
            billobj = form.save(commit=False)
            billobj.save()     
            # create bill details object
            billdetailsobj = SaleBillDetails(billno=billobj)
            billdetailsobj.save()
            for form in formset:                                               
                # false saves the item and links bill to the item
                billitem = form.save(commit=False)
                billitem.billno = billobj                                     
                # gets the stock item
                stock = get_object_or_404(Stock, name=billitem.stock.name)      
                # calculates the total price
                billitem.totalprice = billitem.perprice * billitem.quantity
                # updates quantity in stock db
                stock.quantity -= billitem.quantity   
                # saves bill item and stock
                stock.save()
                billitem.save()
            messages.success(request, "Sold items have been registered successfully")
            return redirect('sale-bill', billno=billobj.billno)
        form = SaleForm(request.GET or None)
        formset = SaleItemFormset(request.GET or None)
        context = {
            'form'      : form,
            'formset'   : formset,
        }
        return render(request, self.template_name, context)


# used to delete a bill object
class SaleDeleteView(SuccessMessageMixin, DeleteView):
    model = SaleBill
    template_name = "sales/delete_sale.html"
    success_url = '/transactions/sales'
    
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = SaleItem.objects.filter(billno=self.object.billno)
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name)
            if stock.is_deleted == False:
                stock.quantity += item.quantity
                stock.save()
        messages.success(self.request, "Sale bill has been deleted successfully")
        return super(SaleDeleteView, self).delete(*args, **kwargs)



class OrderNoView(View):
    model = OrderNo
    template_name = "bill/orderNo.html"
    bill_base = "bill/bill_base.html"

    def get(self, request, billno):
        context = {
            'bill'          : c.objects.get(orderno=orderno),
            'items'         : OrderItem.objects.filter(orderno=orderno),
            'billdetails'   : OrderIDetails.objects.get(orderno=orderno),
            'bill_base'     : self.bill_base,
        }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = PurchaseDetailsForm(request.POST)
        if form.is_valid():
            billdetailsobj = PurchaseBillDetails.objects.get(billno=billno)
            
            billdetailsobj.eway = request.POST.get("eway")    
            billdetailsobj.veh = request.POST.get("veh")
            billdetailsobj.destination = request.POST.get("destination")
            billdetailsobj.po = request.POST.get("po")
            billdetailsobj.cgst = request.POST.get("cgst")
            billdetailsobj.sgst = request.POST.get("sgst")
            billdetailsobj.igst = request.POST.get("igst")
            billdetailsobj.cess = request.POST.get("cess")
            billdetailsobj.tcs = request.POST.get("tcs")
            billdetailsobj.total = request.POST.get("total")

            billdetailsobj.save()
            messages.success(request, "Bill details have been modified successfully")
        context = {
            'bill'          : OrderBill.objects.get(orderno=orderno),
            'items'         : OrderItem.objects.filter(orderno=orderno),
            'billdetails'   : OrderBillDetails.objects.get(orderno=orderno),
            'bill_base'     : self.bill_base,
        }
        return render(request, self.template_name, context)


# used to display the sale bill object
class SaleBillView(View):
    model = SaleBill
    template_name = "bill/sale_bill.html"
    bill_base = "bill/bill_base.html"
    
    def get(self, request, billno):
        context = {
            'bill'          : SaleBill.objects.get(billno=billno),
            'items'         : SaleItem.objects.filter(billno=billno),
            'billdetails'   : SaleBillDetails.objects.get(billno=billno),
            'bill_base'     : self.bill_base,
        }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = SaleDetailsForm(request.POST)
        if form.is_valid():
            billdetailsobj = SaleBillDetails.objects.get(billno=billno)
            
            billdetailsobj.eway = request.POST.get("eway")    
            billdetailsobj.veh = request.POST.get("veh")
            billdetailsobj.destination = request.POST.get("destination")
            billdetailsobj.po = request.POST.get("po")
            billdetailsobj.cgst = request.POST.get("cgst")
            billdetailsobj.sgst = request.POST.get("sgst")
            billdetailsobj.igst = request.POST.get("igst")
            billdetailsobj.cess = request.POST.get("cess")
            billdetailsobj.tcs = request.POST.get("tcs")
            billdetailsobj.total = request.POST.get("total")

            billdetailsobj.save()
            messages.success(request, "Bill details have been modified successfully")
        context = {
            'bill'          : SaleBill.objects.get(billno=billno),
            'items'         : SaleItem.objects.filter(billno=billno),
            'billdetails'   : SaleBillDetails.objects.get(billno=billno),
            'bill_base'     : self.bill_base,
        }
        return render(request, self.template_name, context)