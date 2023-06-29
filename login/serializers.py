from rest_framework import serializers
from .models import *

class Branch_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'

class Customer_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class Employee_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'