from django.urls import path
from .views import *

urlpatterns = [
    path('customer',CustomerAPI.as_view(),name="customer"),
    path('customer/login',CustomerLogin.as_view(),name='customer_login'),
    path('customerDetail/<str:pk>',CustomerDetailAPI.as_view(),name="customer_detail"),
    path('employee',EmployeeAPI.as_view(),name="employee"),
    path('employeeDetail/<str:pk>',EmployeeDetailAPI.as_view(),name="employee_detail"),
    path('branch/<str:pk>',BranchAPI.as_view(),name="branch"),
    path('customer/otp',otpLogin.as_view(),name='customer_otp'),
]