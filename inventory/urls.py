from django.urls import path
from .views import *

urlpatterns = [
    path('car',CarAPI.as_view(),name="car"),
    path('carDetail/<str:pk>/<int:bid>',CarDetailAPI.as_view(),name="car_detail"),
    path('car_stock/<int:pk>',Car_Stock.as_view(),name="car_stock"),
    path('article',ArticleAPI.as_view(),name="article"),
    path('articleDetail/<int:pk>',ArticleDetailAPI.as_view(),name="article"),
    path('replacement',ReplacementAPI.as_view(),name="replacement"),
    path('replacementDetail/<str:pk>/<int:bid>',ReplacementDetailAPI.as_view(),name="replacement_detail"),
    path('replacement_stock/<int:pk>',Replacement_Stock.as_view(),name="replacement_stock"),
]