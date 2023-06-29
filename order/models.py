from django.db import models
from inventory.models import Article, Car, Replacement, Branch_article
from login.models import Employee, Customer


# Create your models here.
class Work_order(models.Model):
    id=models.AutoField(primary_key=True)
    start_date=models.DateTimeField(auto_now_add=True)
    end_date=models.DateTimeField(null=True)
    model=models.CharField(max_length=50)
    model_date=models.CharField(max_length=10)
    plate=models.CharField(max_length=10)
    observation=models.TextField(null=True)
    id_employee=models.ForeignKey(Employee,on_delete=models.SET_NULL, null=True)
    id_customer=models.ForeignKey(Customer,on_delete=models.SET_NULL, null=True)

class Order_detail(models.Model):
    id=models.AutoField(primary_key=True)
    id_work_order=models.ForeignKey(Work_order,on_delete=models.SET_NULL, null=True)
    id_replacement=models.ForeignKey(Replacement,on_delete=models.SET_NULL, null=True)
    id_branch=models.ForeignKey(Branch_article,on_delete=models.CASCADE, null=True)
    amount=models.IntegerField()

class Quotation(models.Model):
    id=models.AutoField(primary_key=True)
    date=models.DateTimeField(auto_now_add=True)
    observation=models.TextField(null=True)
    total=models.IntegerField()
    id_customer=models.ForeignKey(Customer,on_delete=models.SET_NULL, null=True)
    id_employee=models.ForeignKey(Employee,on_delete=models.SET_NULL, null=True)

class Quotation_detail(models.Model):
    id=models.AutoField(primary_key=True)
    id_quotation=models.ForeignKey(Quotation,on_delete=models.CASCADE, null=True)
    id_car=models.ForeignKey(Car,on_delete=models.SET_NULL, null=True)
    amount=models.IntegerField()
    subtotal=models.FloatField()
    
class Bill(models.Model):
    PAYMENT_METHODS = [
        ("TC","Tarjeta de crédito"),
        ("EF","Efectivo"),
        ("PS","Pse")
    ]

    id=models.AutoField(primary_key=True)
    date=models.DateTimeField(auto_now_add=True)
    payment_method=models.CharField(max_length=2,choices=PAYMENT_METHODS)
    observation=models.TextField(null=True)
    total=models.IntegerField()
    id_customer=models.ForeignKey(Customer,on_delete=models.SET_NULL, null=True)
    id_employee=models.ForeignKey(Employee,on_delete=models.SET_NULL, null=True)

class Bill_detail(models.Model):
    id=models.AutoField(primary_key=True)
    id_bill=models.ForeignKey(Bill,on_delete=models.CASCADE, null=True)
    id_car=models.ForeignKey(Car,on_delete=models.SET_NULL, null=True)
    id_branch=models.ForeignKey(Branch_article,on_delete=models.SET_NULL, null=True)
    amount=models.IntegerField()
    subtotal=models.IntegerField()