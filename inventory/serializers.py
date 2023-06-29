from rest_framework import serializers
from inventory.models import Article, Car, Replacement, Branch_article

class Article_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
        
class All_Car_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

class Car_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id','brand','type','model','wheel','price','image']

class All_Replacement_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Replacement
        fields = '__all__'

class Replacement_Serializer(serializers.ModelSerializer):
  class Meta:
    model = Replacement
    fields = ['type','name']

class Branch_Article_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Branch_article
        fields = '__all__'