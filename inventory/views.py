from . models import *
from . serializers import *
from . forms import *
from . helpers import *
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . logger import *
from . authentication import *
from datetime import datetime
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
import uuid
from django.contrib.auth.models import User
import environ
import os



# Create your views here.

# initialize environment variable to use environ variables
env = environ.Env()
environ.Env.read_env()

"""
this class will be used to generate token for a registered employee or user account
if the employee or account already has a token that has not expired then the token
will be returned to be reused 
"""
class GenerateToken(APIView):
    """
    This class will only take post request to generate a token
    for registered employees or user accounts. token is needed for
    every request to any endpoint. this is to secure the api
    """
    def post(self, request, format=None):
        rp = request.POST
        res = auth_user(rp.get("username"), rp.get("password"), rp.get("apikey"))
        return res

"""
This class return the login page
this page can be viewed by every type of user
"""
class IndexView(View):
    template_name = "inventory/login.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(f"/inventory/dashboard")
        return render(request, self.template_name)

"""
This class with login the user and create a session
only super user can login
"""
class LoginView(View):
    intended = None

    def get(self, request):
        self.intended = (
            request.GET.get("next")
            if request.GET.get("next") is not None
            else "/inventory/dashboard"
        )
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect(f"/inventory/dashboard")
        return render(request, "inventory/login.html")

    def post(self, request):
        self.intended = (
            request.GET.get("next")
            if request.GET.get("next") is not None
            else "/inventory/dashboard"
        )

        # print(request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            iLog(f"{user.email} logged in @ {datetime.now()}")
            return redirect(self.intended)
        else:
            messages.error(request, "Invalid username or password!")
            return redirect("%s" % ("/inventory/login"))

"""
This class will redirect user to dashboard to create employees after succesful login
only super user can create other employees or user accounts 
"""
class DashboardView(LoginRequiredMixin, View):
    model = Employee
    template_name = "inventory/dashboard.html"

    def get_success_url(self):
        return redirect(f"/inventory/dashboard")

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            context={},
        )

    def post(self, request, *args, **kwargs):
        self.intended = (
            request.GET.get("next")
            if request.GET.get("next") is not None
            else f"/inventory/dashboard/{self.request.user.username}"
        )
        form_obj = EmployeeCreationForm(request.POST or None, request.FILES or None)
        if form_obj.is_valid():
            form_obj.save(commit=False)
            user_obj = User.objects.create_user(
                username=request.POST.get("name"), email=request.POST.get("email"), password=request.POST.get("password"))
            user_obj.save()
            employee_obj = Employee.objects.create(
                employee=user_obj, apikey=randomXters(request.POST.get("name"))
            )
            employee_obj.name = request.POST.get("name")
            employee_obj.email = request.POST.get("email")
            employee_obj.save()
            messages.success(request, "Employee successfully created")
        else:
            messages.warning(request, form_obj.errors)
        return self.get_success_url()

# -------------------- ITEMS STARTS HERE --------------------

class ItemsList(APIView):
    """
    This class will list out all the items and crate a new one
    """

    """this class method will fetch all items
        this class method can be accessed by all users
        in production environmnent this calss will be throttlled to
        prevent unfair usage
    """
    def get(self, request, format=None):
        items = Items.objects.all()
        iLog(f"Request for item: {request} @ {datetime.now()}")
        serializer = ItemsSerializer(items, many=True)
        return Response(serializer.data)

    """this class method will allow creation of a new item
        this class method can only be used by employyes or accounts with access token
    """
    def post(self, request, format=None):
        rp = request.POST
        # print(rp)
        res = gen_auth_checker(request)
        if res.status_code != 200:
            return res
        serializer = ItemsSerializer(data=request.data)
        iLog(f"New item to be uploaded: {request.data} @ {datetime.now()}")
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemSuppliers(APIView):
    """this class method will allow fetching of all supliers of an item
        this class method can be accessed by all users
        in production environmnent this calss will be throttlled to
        prevent unfair usage
    """
    def get(self, request, pk, format=None):
        try:
            items = Items.objects.get(pk=pk)
        except Exception as e:
            return Response({"Message": str(e)}, 404)
        iLog(f"ID of item fetched is: {pk} @ {datetime.now()}")
        suppliers = items.supplier.all()
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(serializer.data)


class ItemAddSuppliers(APIView):
    """this class method will allow adding items to suppliers
        this class method can only be used by employyes or accounts with access token
    """
    def post(self, request, pk, supplier_id, format=None):
        res = gen_auth_checker(request)
        if res.status_code != 200:
            return res
        try:
            items = Items.objects.get(pk=pk)
        except Exception as e:
            return Response({"Message": str(e)}, 404)
        try:
            supplier_obj = Supplier.objects.get(pk=supplier_id)
        except Exception as e:
            return Response({"Message": str(e)}, 404)
        items.supplier.add(supplier_obj)
        iLog(f"ID of item - {items} fetched is added to : supplier - {supplier_obj.name} @ {datetime.now()}")
        serializer = ItemsSerializer(items)
        return Response(serializer.data)


class ItemsDetail(APIView):
    """
    This class will fetch, update and delete an items object.
    """
    def get_object(self, pk):
        try:
        	iLog(f"ID of item fetched is: {pk} @ {datetime.now()}")
        	return Items.objects.get(pk=pk)
        except Items.DoesNotExist:
            raise Http404

    """this class method will allow fetching of an item details
        this class method can be accessed by all users
        in production environmnent this calss will be throttlled to
        prevent unfair usage
    """
    def get(self, request, pk, format=None):
        items = self.get_object(pk)
        iLog(f"ID of item fetched is: {pk} @ {datetime.now()}")
        serializer = ItemsSerializer(items)
        return Response(serializer.data)

    """this class method will allow update of an item information
        only employyes with valid token and credentials can update items
    """
    def put(self, request, pk, format=None):
        res = gen_auth_checker(request)
        if res.status_code != 200:
            return res
        items = self.get_object(pk)
        iLog(f"ID of item to be updated is: {pk} @ {datetime.now()}")
        serializer = ItemsSerializer(items, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    """this class method will allow deletion of an item
        only employyes with valid token and credentials can delete items
    """
    def delete(self, request, pk, format=None):
        res = gen_auth_checker(request)
        if res.status_code != 200:
            return res
        items = self.get_object(pk)
        iLog(f"ID of item to be deleted is: {pk} @ {datetime.now()}")
        items.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# -------------------- ITEMS ENDS HERE --------------------

# -------------------- SUPPLIERS STARTS HERE --------------------

class SupplierstList(APIView):
    """
    This class will list out all the suppliers and create new ones
    """

    """this class method will fetch all suppliers
        this class method can be accessed by all users
        in production environmnent this calss will be throttlled to
        prevent unfair usage
    """
    def get(self, request, format=None):
        suppliers = Supplier.objects.all()
        # print(suppliers)
        iLog(f"Request for supplier: {request} @ {datetime.now()}")
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(serializer.data)

    """this class method will allow creation of a new supplier
        only employees that have token can have access to this endpoint
    """
    def post(self, request, format=None):
        res = gen_auth_checker(request)
        if res.status_code != 200:
            return res
        serializer = SupplierSerializer(data=request.data)
        iLog(f"New supplier to be added: {request.data} @ {datetime.now()}")
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SuppliersDetail(APIView):
    """
    This class will fetch, update or delete an suppliers object.
    only employees that have token can have access to this endpoint
    """
    def get_object(self, pk):
        try:
            return Supplier.objects.get(pk=pk)
        except Supplier.DoesNotExist:
            raise Http404

    """ this class method will allow fetching of a supplier details
        this class method can be accessed by all users
        in production environmnent this calss will be throttlled to
        prevent unfair usage
    """
    def get(self, request, pk, format=None):
        suppliers = self.get_object(pk)
        iLog(f"ID of supplier fetched is: {pk} @ {datetime.now()}")
        serializer = SupplierSerializer(suppliers)
        return Response(serializer.data)

    """this class method will allow update of a supplier details
    """
    def put(self, request, pk, format=None):
        suppliers = self.get_object(pk)
        iLog(f"ID of supplier to be updated is: {pk} @ {datetime.now()}")
        serializer = SupplierSerializer(suppliers, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    """this class method will allow deletion of an supplier
        this function is not required 
    """
    # def delete(self, request, pk, format=None):
    #     suppliers = self.get_object(pk)
    #     iLog(f"ID of supplier to be deleted is: {pk} @ {datetime.now()}")
    #     suppliers.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

# -------------------- SUPPLIERS END HERE --------------------

"""
This class with logout the user and clear all sessions
only super user can logout
"""
class LogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("/inventory/login")