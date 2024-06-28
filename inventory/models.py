from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.

"""
This model will create the table that holds information about the employees
and other applications that can access the API
Returns:
    _type_: model object
"""
class Employee(models.Model):
    employee = models.OneToOneField(
        User, unique=True, null=True, blank=True, on_delete=models.CASCADE
    )
    name = models.CharField(unique=True, max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, max_length=255, null=True, blank=True)
    role = models.CharField(max_length=255, null=True, blank=True)
    apikey = models.CharField(max_length=50, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return "%s" % (self.name)


"""
This model will create the table that holds information about the suppliers
Returns:
    _type_: model object
"""
class Supplier(models.Model):
    name = models.CharField(unique=True, max_length=150, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    date_added = models.DateField(auto_now_add=True)

    @classmethod
    def all_suppliers(cls):
        return Supplier.objects.all()

    class Meta:
        verbose_name_plural = "Suppliers"
        ordering = ["-date_added"]

    def __str__(self) -> str:
        return "%s" % (self.name)


"""
This model will create the table that holds information about the items
Returns:
    _type_: model object
"""
class Items(models.Model):
    supplier = models.ManyToManyField(Supplier)
    name = models.CharField(max_length=150, null=True)
    description = models.CharField(max_length=500, null=True)
    price = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, default=0
    )
    date_added = models.DateField(auto_now_add=True)

    @classmethod
    def all_items(cls):
        return Items.objects.all()

    class Meta:
        verbose_name_plural = "Items"
        ordering = ["-date_added"]

    def __str__(self) -> str:
        return "%s" % (self.name)


