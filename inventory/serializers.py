from rest_framework import serializers
from . models import *

"""
This class will serialize supplier python objects to json
"""
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['pk', 'name', 'address', 'telephone', 'date_added']

"""
This class will serialize items python objects to json
"""
class ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Items
        fields = ['pk','supplier', 'name', 'description', 'price', 'date_added']