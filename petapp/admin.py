from django.contrib import admin
from petapp.models import Pet, Cart, Order


# Register your models here.
class PetAdmin(admin.ModelAdmin):
    list_display = ['id','name','type','breed','gender','age','price','details','imagepath']
    list_filter = ['type','breed','price']


class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'pid', 'uid', 'quantity']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','orderid','pid','userid','quantity']
    list_filter = ['pid','userid']


admin.site.register(Pet, PetAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)




