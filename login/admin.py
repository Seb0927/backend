from django.contrib import admin
from .models import Branch,Customer, Employee

# Register your models here.

admin.site.register(Branch)
admin.site.register(Customer)
admin.site.register(Employee)