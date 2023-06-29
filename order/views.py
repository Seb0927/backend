from django.shortcuts import render
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from inventory.models import *
from order.models import *
from order.serializers import *
from datetime import datetime

class Order_detailAPI(APIView):
    order_detail_serializer = Order_detail_Serializer
    all_order_detail_serializer = All_Order_detail_Serializer

    def get(self, request):
        queryset = Order_detail.objects.all()
        serializer = self.all_order_detail_serializer(queryset,many=True)
        return Response(serializer.data)

    def post(self, request):        
        with transaction.atomic():
            serializer = self.order_detail_serializer(data=request.data)
            is_valid_order_detail = serializer.is_valid()

            if is_valid_order_detail:
                amount = serializer.validated_data['amount']
                id_replacement = serializer.validated_data['id_replacement']
                replacement = Replacement.objects.get(id= request.data['id_replacement'])
                article = Branch_article.objects.get(id_branch=request.data['id_branch'],id_article=replacement.id_article)
                if ((article.stock-amount) < 0):
                    return Response({"status": "fail", "message": f"Replacement: {id_replacement} has not enough stock for the required amount "}, status=status.HTTP_404_NOT_FOUND)

                article.stock -= amount
                article.save()

                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Order_detailDetailAPI(APIView):
    order_detail_serializer = Order_detail_Serializer
    all_order_detail_serializer = All_Order_detail_Serializer

    def get_order_detail(self, pk):
        try:
            return Order_detail.objects.get(pk=pk)
        except:
            return None

    def get(self, request, pk):
        order_detail = self.get_order_detail(pk=pk)
        if order_detail == None:
            return Response({"status": "fail", "message": f"Order_detail with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.all_order_detail_serializer(order_detail)
        return Response(serializer.data)
        
    def delete(self, request, pk):
        with transaction.atomic():
            order_detail = self.get_order_detail(pk=pk)
            if order_detail == None:
                return Response({"status": "fail", "message": f"Order_detail with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

            # Retrieve the amount and id_replacement
            amount = order_detail.amount
            replacement = Replacement.objects.get(id=order_detail.id_replacement.id)
            article = article = Branch_article.objects.get(id_branch=order_detail.id_branch.id ,id_article=replacement.id_article.id)

            order_detail.delete()

            # Update the id_replacement stock
            article.stock += amount
            article.save()

            return Response(status=status.HTTP_204_NO_CONTENT)


class Work_orderAPI(APIView):
    work_order_serializer = Work_order_Serializer
    all_work_order_serializer = All_work_order_Serializer
    all_order_detail_serializer = All_Order_detail_Serializer


    def get(self, request):
        queryset = Work_order.objects.all()
        fullset = []
        for w in queryset:
            order_details = Order_detail.objects.filter(id_work_order=w.id)
            order_details_serializer = self.all_order_detail_serializer(order_details, many=True)
            query = {
                "id":w.id,
                "start_date":w.start_date,
                "end_date":w.end_date,
                "model":w.model,
                "model_date":w.model_date,
                "plate":w.plate,
                "observation":w.observation,
                "id_employee":w.id_employee.id,
                "id_customer":w.id_customer.id,
                "order_details": order_details_serializer.data,
            }
            fullset.append(query)
        
        return Response(fullset)

    def post(self, request):
        with transaction.atomic():
            request.data["end_date"]= None
            serializer = self.work_order_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Work_orderDetailAPI(APIView):
    work_order_serializer = Work_order_Serializer
    all_work_order_serializer = All_work_order_Serializer
    all_order_detail_serializer = All_Order_detail_Serializer

    def get_work_order(self, pk):
        try:
            return Work_order.objects.get(pk=pk)
        except:
            return None
    
    def get(self, request, pk):
        w = self.get_work_order(pk=pk)
        if w == None:
            return Response({"status": "fail", "message": f"Work_order with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        order_details = Order_detail.objects.filter(id_work_order=w.id)
        order_details_serializer = self.all_order_detail_serializer(order_details, many=True)
        data = {
                "id":w.id,
                "start_date":w.start_date,
                "end_date":w.end_date,
                "model":w.model,
                "model_date":w.model_date,
                "plate":w.plate,
                "observation":w.observation,
                "id_employee":w.id_employee.id,
                "id_customer":w.id_customer.id,
                "order_detail": order_details_serializer.data,
            }
        return Response(data)

    def patch(self, request, pk):
        with transaction.atomic():
            request.data["end_date"]= datetime.now()
            work_order = self.get_work_order(pk=pk)
            if work_order == None:
                return Response({"status": "fail", "message": f"Work_order with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = self.work_order_serializer(work_order, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success", "data": {"work_order": serializer.data}})

            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        with transaction.atomic():
            work_order = self.get_work_order(pk=pk)
            if work_order is None:
                return Response({"status": "fail", "message": f"Work_order with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

            with transaction.atomic():
                order_details = Order_detail.objects.filter(id_work_order=work_order.id)

                for order_detail in order_details:
                    # Retrieve the amount and id_replacement
                    amount = order_detail.amount
                    replacement = Replacement.objects.get(id=order_detail.id_replacement.id)
                    article = article = Branch_article.objects.get(id_branch=order_detail.id_branch.id ,id_article=replacement.id_article.id)

                    order_detail.delete()

                    # Update the id_replacement stock
                    article.stock += amount
                    article.save()

            work_order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class Quotation_detailAPI(APIView):
    quotation_detail_serializer = Quotation_detail_Serializer
    all_quotation_detail_serializer = All_quotation_detail_Serializer

    def get(self, request):
        queryset = Quotation_detail.objects.all()
        serializer = self.all_quotation_detail_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        with transaction.atomic():
            price = Car.objects.filter(id=request.data['id_car']).first().price

            if len(Quotation_detail.objects.filter(id_quotation=request.data['id_quotation'],id_car=request.data['id_car'])) == 0:
                request.data['subtotal'] = price * request.data['amount']
                serializer = self.quotation_detail_serializer(data=request.data)
                is_valid_quotation_detail = serializer.is_valid()
            else:
                item = Quotation_detail.objects.get(id_quotation=request.data['id_quotation'],id_car=request.data['id_car'])
                item.subtotal = price * (request.data['amount'] + item.amount)
                request.data['amount'] = item.amount + request.data['amount']
                item.save()
                serializer = self.quotation_detail_serializer(item,data=request.data, partial=True)
                is_valid_quotation_detail = serializer.is_valid()

            if is_valid_quotation_detail:
                serializer.save()

                details = Quotation_detail.objects.filter(id_quotation=request.data['id_quotation'])
                total = 0
                for d in details:
                    total += d.subtotal
                q = Quotation.objects.get(id=request.data['id_quotation'])
                q.total = total
                q.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Quotation_detailDetailAPI(APIView):
    quotation_detail_serializer = Quotation_detail_Serializer
    all_quotation_detail_serializer = All_quotation_detail_Serializer

    def get_quotation_detail(self, pk):
        try:
            return Quotation_detail.objects.get(pk=pk)
        except:
            return None

    def get(self, request, pk):
        quotation_detail = self.get_quotation_detail(pk=pk)
        if quotation_detail == None:
            return Response({"status": "fail", "message": f"Quotation_detail with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.all_quotation_detail_serializer(quotation_detail)
        return Response(serializer.data)

    def patch(self, request, pk):
        with transaction.atomic():
            quotation_detail = self.get_quotation_detail(pk=pk)
            if quotation_detail == None:
                return Response({"status": "fail", "message": f"Quotation_detail with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

            quotation = quotation_detail.id_quotation

            #Selecting the car
            try:
                id_car = quotation_detail.id_car.id
            except:
                id_car = request.data['id_car']

            #Selecting the amount
            try:
                amount = quotation_detail.amount
            except:
                amount = request.data['amount']

            price = Car.objects.filter(id=id_car).first().price
            request.data['subtotal'] = price * amount
            print(request.data['subtotal'])
            
            serializer = self.quotation_detail_serializer(quotation_detail, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                details = Quotation_detail.objects.filter(id_quotation=quotation)
                total = 0
                for d in details:
                    total += d.subtotal
                quotation.total = total
                quotation.save()
                return Response({"status": "success", "data": {"quotation_detail": serializer.data}})
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        with transaction.atomic():
            quotation_detail = self.get_quotation_detail(pk=pk)
            if quotation_detail == None:
                return Response({"status": "fail", "message": f"Quotation_detail with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
            
            quotation = quotation_detail.id_quotation
            quotation_detail.delete()
            
            details = Quotation_detail.objects.filter(id_quotation=quotation)
            total = 0
            for d in details:
                total += d.subtotal
            quotation.total = total
            quotation.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

class QuotationAPI(APIView):
    quotation_serializer = Quotation_Serializer
    all_quotation_serializer = All_quotation_Serializer
    all_quotation_detail_serializer = All_quotation_detail_Serializer

    def get(self, request):
        queryset = Quotation.objects.all()
        fullset = []
        for q in queryset:
            quotation_details = Quotation_detail.objects.filter(id_quotation=q.id)
            quotation_details_serializer = self.all_quotation_detail_serializer(quotation_details, many=True)
            query = {
                "id":q.id,
                "date":q.date,
                "observation":q.observation,
                "total":q.total,
                "id_customer":q.id_customer.id,
                "id_employee":q.id_employee.id,
                "quotation_details": quotation_details_serializer.data,
            }
            fullset.append(query)

        return Response(fullset)

    def post(self, request):
        with transaction.atomic():
            request.data["total"] = 0
            serializer = self.quotation_serializer(data=request.data)
            is_valid_quotation = serializer.is_valid()

            if is_valid_quotation:
                serializer.save()
                last = Quotation.objects.last()
                data = {
                    "id":last.id,
                    "id_customer":last.id_customer.id,
                    "id_employee":last.id_employee.id,
                    "observation":last.observation,
                    "total":last.total
                }
                return Response(data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class QuotationDetailAPI(APIView):
    quotation_serializer = Quotation_Serializer
    all_quotation_serializer = All_quotation_Serializer

    def get_quotation(self, pk):
        try:
            return Quotation.objects.get(pk=pk)
        except:
            return None
        
    def get(self, request, pk):
        quotation = self.get_quotation(pk=pk)
        if quotation == None:
            return Response({"status": "fail", "message": f"Quotation with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        items = Quotation_detail.objects.filter(id_quotation=pk)
        info = []
        for i in items:
            infoAux = {
                "id": i.id,
                "amount": i.amount,
                "subtotal": i.subtotal,
                "id_car": i.id_car.id
            }
            info.append(infoAux)

        data = {
            "id": quotation.id,
            "date": quotation.date,
            "observation": quotation.observation,
            "total": quotation.total,
            "id_customer": quotation.id_customer.id,
            "id_employee": quotation.id_employee.id,
            "quotation_details": info
        }

        serializer = self.all_quotation_serializer(quotation)
        return Response(data)

    def patch(self, request, pk):
        with transaction.atomic():
            quotation = self.get_quotation(pk=pk)
            if quotation == None:
                return Response({"status": "fail", "message": f"Quotation with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

            #Collecting the total
            queryset = Quotation_detail.objects.filter(id_quotation=quotation.id)
            request.data["total"] = 0
            for q in queryset:
                request.data["total"] += q.subtotal
            
            serializer = self.quotation_serializer(quotation, data=request.data, partial=True)

            is_valid_quotation = serializer.is_valid()

            if is_valid_quotation:
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        with transaction.atomic():
            quotation = self.get_quotation(pk=pk)
            if quotation == None:
                return Response({"status": "fail", "message": f"Quotation with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
            
            quotation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class Bill_detailAPI(APIView):
    bill_detail_serializer = Bill_detail_Serializer
    all_bill_detail_serializer = All_bill_detail_Serializer

    def get(self, request):
        queryset = Bill_detail.objects.all()
        serializer = self.all_bill_detail_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        with transaction.atomic():
            price = Car.objects.filter(id=request.data['id_car']).first().price
            request.data['subtotal'] = price * request.data['amount']

            serializer = self.bill_detail_serializer(data=request.data)
            is_valid_bill_detail = serializer.is_valid()

            if is_valid_bill_detail:
                amount = serializer.validated_data['amount']
                id_car = serializer.validated_data['id_car']
                car = Car.objects.get(id=request.data['id_car'])
                article = Branch_article.objects.get(id_branch=request.data['id_branch'],id_article=car.id_article)
                if ((article.stock-amount) < 0):
                    return Response({"status": "fail", "message": f"Car: {id_car} has not enough stock for the required amount "}, status=status.HTTP_404_NOT_FOUND)

                article.stock -= amount
                article.save()

                serializer.save()

                details = Bill_detail.objects.filter(id_bill=request.data['id_bill'])
                total = 0
                for d in details:
                    total += d.subtotal
                b = Bill.objects.get(id = request.data['id_bill'])
                b.total = total
                b.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            

class Bill_detailDetailAPI(APIView):
    bill_detail_serializer = Bill_detail_Serializer
    all_bill_detail_serializer = All_bill_detail_Serializer

    def get_bill_detail(self, pk):
        try:
            return Bill_detail.objects.get(pk=pk)
        except:
            return None

    def get(self, request, pk):
        bill_detail = self.get_bill_detail(pk=pk)
        if bill_detail == None:
            return Response({"status": "fail", "message": f"Bill_detail with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
    
        serializer = self.all_bill_detail_serializer(bill_detail)
        return Response(serializer.data)

    def delete(self, request, pk):
        with transaction.atomic():
            bill_detail = self.get_bill_detail(pk=pk)
            if bill_detail == None:
                return Response({"status": "fail", "message": f"Bill_detail with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND) 

            # Retrieve the amount and id_replacement
            amount = bill_detail.amount
            car = Car.objects.get(id=bill_detail.id_car.id)
            article = Branch_article.objects.get(id_branch=bill_detail.id_branch.id ,id_article=car.id_article.id)

            bill = bill_detail.id_bill
            bill_detail.delete()

            # Update the id_replacement stock
            article.stock += amount
            article.save()

            details = Bill_detail.objects.filter(id_bill=bill)
            total = 0
            for d in details:
                total += d.subtotal
            bill.total = total
            bill.save()

            return Response(status=status.HTTP_204_NO_CONTENT)

class BillAPI(APIView):
    bill_serializer = Bill_Serializer
    all_bill_serializer = All_bill_Serializer
    all_bill_detail_serializer = All_bill_detail_Serializer

    def get(self, request):
        queryset = Bill.objects.all()
        fullset = []
        for b in queryset:
            bill_details = Bill_detail.objects.filter(id_bill=b.id)
            bill_details_serializer = self.all_bill_detail_serializer(bill_details, many=True)
            query = {
                "id":b.id,
                "date":b.date,
                "payment_method":b.payment_method,
                "observation":b.observation,
                "total":b.total,
                "id_customer":b.id_customer.id,
                "id_employee":b.id_employee.id,
                "bill_details":bill_details_serializer.data
            }
            fullset.append(query)
        
        return Response(fullset)
    
    def post(self, request):
        with transaction.atomic():
            request.data["total"] = 0
            serializer = self.bill_serializer(data=request.data)
            is_valid_quotation = serializer.is_valid()

            if is_valid_quotation:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class BillDetailAPI(APIView):
    bill_serializer = Bill_Serializer
    all_bill_serializer = All_bill_Serializer
    all_bill_detail_serializer = All_bill_detail_Serializer

    def get_bill(self, pk):
        try:
            return Bill.objects.get(pk=pk)
        except:
            return None

    def get(self, request, pk):
        b = self.get_bill(pk=pk)
        if b == None:
            return Response({"status": "fail", "message": f"Bill with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        bill_details = Bill_detail.objects.filter(id_bill=b.id)
        bill_details_serializer = self.all_bill_detail_serializer(bill_details, many=True)
        data = {
            "id":b.id,
            "date":b.date,
            "payment_method":b.payment_method,
            "observation":b.observation,
            "total":b.total,
            "id_customer":b.id_customer.id,
            "id_employee":b.id_employee.id,
            "bill_details":bill_details_serializer.data
        }
        return Response(data)

    def patch(self, request, pk):
        with transaction.atomic():
            bill = self.get_bill(pk=pk)
            if bill == None:
                return Response({"status": "fail", "message": f"Bill with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

            #Collects the total
            queryset = Bill_detail.objects.filter(id_bill=bill.id)
            request.data["total"] = 0
            for b in queryset:
                request.data["total"] += b.subtotal
            
            serializer = self.bill_serializer(bill, data=request.data, partial=True)

            is_valid_bill = serializer.is_valid()

            if is_valid_bill:
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        with transaction.atomic():
            bill = self.get_bill(pk=pk)
            if bill == None:
                return Response({"status": "fail", "message": f"Bill with Id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

            with transaction.atomic():
                bill_details = Bill_detail.objects.filter(id_bill=bill.id)

                for bill_detail in bill_details:
                    # Retrieve the amount and id_replacement
                    amount = bill_detail.amount
                    car = Car.objects.get(id=bill_detail.id_car.id)
                    article = Branch_article.objects.get(id_branch=bill_detail.id_branch.id ,id_article=car.id_article.id)

                    bill_detail.delete()

                    # Update the id_replacement stock
                    article.stock += amount
                    article.save()
            
            bill.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)