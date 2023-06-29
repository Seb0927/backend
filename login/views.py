from urllib import response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.backends import ModelBackend
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.db import transaction
from rest_framework import status
from .models import *
from .serializers import *
from order.models import *

# Create your views here.

class CustomerAPI(APIView):
    def get(self,request):
        queryset = Customer.objects.all().exclude(id="000000000000")
        fullset = []
        for c in queryset:
            query = {"id":c.id,
             "first_name":c.id_user.first_name,
             "last_name":c.id_user.last_name,
             "email":c.id_user.email,
             "address":c.address,
             "phone":c.phone,
             "type":c.type}
            fullset.append(query)
        
        return Response({"status":"success","data":fullset})
    
    def post(self,request):
        data = self.request.data
        with transaction.atomic():
            username = data['first_name'] + "." + data['last_name']
            user = User.objects.create_user(username=username,
                                            password=data['password'],
                                            email=data['email'],
                                            first_name=data['first_name'],
                                            last_name=data['last_name'])
            user.save()
            last_user = User.objects.last()

            customer = Customer(id=data['id'],
                                address=data['address'],
                                phone=data['phone'],
                                type=data['type'],
                                id_user=last_user)
            customer.save()

        return Response({"status":"success","message":f"Customer {customer.id_user.first_name} was created"})

class CustomerDetailAPI(APIView):
    queryset = Customer.objects.all()
    serializer_class = Customer_Serializer

    def get_customer(self, pk):
        try:
            return Customer.objects.get(pk=pk)
        except:
            return None

    def get(self, request, pk):
        customer = self.get_customer(pk=pk)
        if customer == None:
            return Response({"status": "fail", "message": f"Customer with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        data = {"id":customer.id,
             "first_name":customer.id_user.first_name,
             "last_name":customer.id_user.last_name,
             "email":customer.id_user.email,
             "address":customer.address,
             "phone":customer.phone,
             "type":customer.type}
        return Response({"status": "success", "data": data})
    
    def patch(self, request, pk):
        customer = self.get_customer(pk=pk)
        if customer == None:
            return Response({"status": "fail", "message": f"Customer with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        #Modifying the user------------------------------------------------------------------------------------------------------
        with transaction.atomic():
            user = customer.id_user
            user.first_name = request.data.get('first_name',user.first_name)
            user.last_name = request.data.get('last_name',user.last_name)
            user.email = request.data.get('email',user.email)
            user.username = user.first_name + ' ' + user.last_name
            user.set_password(request.data.get('password', ''))
            user.save()
        
            #Modifying the customer---------------------------------------------------------------------------------------------------
            serializer = self.serializer_class(customer, data=request.data, partial=True)
            data = {"id":customer.id,
             "first_name":customer.id_user.first_name,
             "last_name":customer.id_user.last_name,
             "email":customer.id_user.email,
             "address":customer.address,
             "phone":customer.phone,
             "type":customer.type}
        
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": data})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    def delete(self, request, pk):
        with transaction.atomic():
            customer = self.get_customer(pk)
            user = customer.id_user
            if customer  == None:
                return Response({"status": "fail", "message": f"Customer with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
            
            def_user = Customer.objects.get(id="000000000000")
            
            work_order = Work_order.objects.filter(id_customer=pk)
            for w in work_order:
                w.id_customer = def_user
                w.save()

            quotation = Quotation.objects.filter(id_customer=pk)
            for q in quotation:
                q.id_customer = def_user
                q.save()

            bill = Bill.objects.filter(id_customer=pk)
            for b in bill:
                b.id_customer = def_user
                b.save()
                
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
class EmployeeAPI(APIView):
    def get(self, request):
        branch_id = int(request.query_params.get('branch', 0))
        fulldata = []

        if (branch_id == 0):
            queryset = Employee.objects.all().exclude(id="000000000000").exclude(id="00000000000")
        else:
            queryset = Employee.objects.filter(id_branch_id=branch_id)
            
        for emp in queryset:
            query = {
                "id": emp.id,
                "first_name": emp.id_user.first_name,
                "last_name": emp.id_user.last_name,
                "email": emp.id_user.email,
                "address": emp.address,
                "phone": emp.phone,
                "role": emp.role,
                "id_branch": emp.id_branch_id,
                "type": "No aplica"
            }
            fulldata.append(query)

        return Response({"status": "success", "data": fulldata})       

    def post(self, request):
        data = self.request.data

        with transaction.atomic():
            username = data['first_name'] + "." + data['last_name']
            user = User.objects.create_user(username=username,
                                            password=data['password'],
                                            email=data['email'],
                                            first_name=data['first_name'],
                                            last_name=data['last_name'])
            user.save()
            last_user = User.objects.last()

            branch_id = data['branch']
            branch = get_object_or_404(Branch, id=branch_id)  # Retrieve the Branch instance

            employee = Employee(id=data['id'],
                                address=data['address'],
                                phone=data['phone'],
                                role=data['role'],
                                id_user=last_user,
                                id_branch=branch)  # Assign the Branch instance
            employee.save() 

        return Response({'resp': "done"})

class EmployeeDetailAPI(APIView):
    queryset = Employee.objects.all()
    serializer_class = Employee_Serializer

    def get_employee(self, pk):
        try:
            return Employee.objects.get(pk=pk)
        except:
            return None

    def get(self, request, pk):
        employee = self.get_employee(pk=pk)
        if employee == None:
            return Response({"status": "fail", "message": f"Employee with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
    
        data = {"id":employee.id,
            "first_name":employee.id_user.first_name,
            "last_name":employee.id_user.last_name,
            "email":employee.id_user.email,
            "address":employee.address,
            "phone":employee.phone,
            "role":employee.role,
            "id_branch":employee.id_branch_id,
            "address_branch":employee.id_branch.address,
            "city_branch":employee.id_branch.city
        }
        return Response({"status": "success", "data": data})

    def patch(self, request, pk):
        employee = self.get_employee(pk=pk)
        if employee == None:
            return Response({"status": "fail", "message": f"Customer with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        #Modifying the user
        with transaction.atomic():
            user = employee.id_user
            user.first_name = request.data.get('first_name',user.first_name)
            user.last_name = request.data.get('last_name',user.last_name)
            user.email = request.data.get('email',user.email)
            user.username = user.first_name + ' ' + user.last_name
            user.set_password(request.data.get('password', ''))
            user.save()            

            #Modifying the employee
            serializer = self.serializer_class(employee, data=request.data, partial=True)
            data = {"id":employee.id,
            "first_name":employee.id_user.first_name,
            "last_name":employee.id_user.last_name,
            "email":employee.id_user.email,
            "address":employee.address,
            "phone":employee.phone,
            "role":employee.role,
            "id_branch":employee.id_branch_id
        }

        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": data})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
        with transaction.atomic():
            employee = self.get_employee(pk)
            user = employee.id_user
            if employee == None:
                return Response({"status": "fail", "message": f"Customer with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

            def_user = Employee.objects.get(id="000000000000")
            
            if employee.role == "Sel":
                def_user = Employee.objects.get(id="000000000000")
            elif employee.role == "Mec":
                def_user = Employee.objects.get(id="00000000000")

            work_order = Work_order.objects.filter(id_employee=pk)
            for w in work_order:
                w.id_employee = def_user
                w.save()

            quotation = Quotation.objects.filter(id_employee=pk)
            for q in quotation:
                q.id_employee = def_user
                q.save()

            bill = Bill.objects.filter(id_employee=pk)
            for b in bill:
                b.id_employee = def_user
                b.save()            

            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None

class CustomerLogin(APIView):
    def post(self,request):
        data = self.request.data
        user = authenticate(username=data['email'],password=data['password'])
        if user is not None:
            login(request,user)
            if(len(Customer.objects.filter(id_user=user.id)) == 1):    
                customer = Customer.objects.filter(id_user=user.id)[0]       
                data = {"id":customer.id,
                "first_name":customer.id_user.first_name,
                "last_name":customer.id_user.last_name,
                "email":customer.id_user.email,
                "address":customer.address,
                "phone":customer.phone,
                "type":customer.type,
                "role": "Cliente",
                "branch": "No aplica"
                }
            else:
                emp = Employee.objects.filter(id_user=user.id)[0]
                data = {"id":emp.id,
                "first_name":emp.id_user.first_name,
                "last_name":emp.id_user.last_name,
                "email":emp.id_user.email,
                "address":emp.address,
                "phone":emp.phone,
                "role":emp.role,
                "branch":emp.id_branch_id,
                "type": "No aplica"}

            return Response({"data":data})
        else:
            logout(request)
            return Response({"detail":"invalid user"})

class CustomerLogout(APIView):
    def post(self, request):
        logout(request)
        return Response({"detail":"Logout successful"})
    
class BranchAPI(APIView):
    serializer_class = Branch_Serializer
    def get_branch(self, pk):
        try:
            return Branch.objects.get(pk=pk)
        except:
            return None

    def get(self,request,pk):
        branch = self.get_branch(pk=pk)
        if branch == None:
            return Response({"status": "fail", "message": f"Branch with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "city": branch.city,
            "address": branch.address    
        }
        return Response({"status": "success", "data": data})

    def patch(self, request, pk):
        branch = Branch.objects.get(id=pk)

        if branch == None:
            return Response({"status": "fail", "message": f"Branch with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

        #Modifying the user
        with transaction.atomic():
            serializer = self.serializer_class(branch, data=request.data, partial=True)
            data = {
                "city" : branch.city,
                "address" : branch.address
            }

        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": data})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class otpLogin(APIView):
    def post(self, request):
        data = self.request.data
        message = 'Tu código de verificación es: ' + str(data['code'])
        email = data['email']
        send_mail(
            'Litio - Tu código de verificación de dos pasos',
            message,
            'settings.EMAIL_HOST_USER',
            [email],
            fail_silently=False)
        return Response({"detail":str(data['code'])})