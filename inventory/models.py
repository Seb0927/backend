import cloudinary
from django.db import models
from login.models import Branch
from cloudinary.models import CloudinaryField

# Create your models here.
class Article(models.Model):
    id=models.AutoField(primary_key=True)
    deleted=models.BooleanField(default=False)

class Branch_article(models.Model):
    id=models.AutoField(primary_key=True)
    id_article=models.ForeignKey(Article,on_delete=models.CASCADE)
    id_branch=models.ForeignKey(Branch,on_delete=models.CASCADE)
    stock=models.IntegerField()
    color=models.CharField(max_length=30, null=True)

class Car(models.Model):
    id=models.CharField(max_length=20, primary_key=True) #VIN: Vehicle Identification Number
    brand=models.CharField(max_length=30)
    type=models.CharField(max_length=20)
    model=models.CharField(max_length=50)
    wheel=models.CharField(max_length=20)
    price=models.IntegerField()
    image = cloudinary.models.CloudinaryField(
        folder='media/car_images/', overwrite=True, resource_type='', blank=True)
    id_article=models.ForeignKey(Article,on_delete=models.SET_NULL, null=True)

class Replacement(models.Model):
    id=models.AutoField(primary_key=True)
    type=models.CharField(max_length=50)
    name=models.CharField(max_length=100)
    id_article=models.ForeignKey(Article,on_delete=models.SET_NULL, null=True)