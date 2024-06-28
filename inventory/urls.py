from django.urls import path
from . import views

urlpatterns = [

    path("login", view=views.LoginView.as_view(), name="inventory.login"),
    path("dashboard", view=views.DashboardView.as_view(), name="inventory.dashboard"),
    path("logout", view=views.LogoutView.as_view(), name="inventory.logout"),

    # generate token
    path('generatetoken', view=views.GenerateToken.as_view(), name="inventory.generatetoken"),

    # get list of all items and add an item
    path('items/api', view=views.ItemsList.as_view()),

    # get details of an item
    path('items/api/<int:pk>/', view=views.ItemsDetail.as_view()),

    # get all supppliers of an item
    path('items/suppliers/api/<int:pk>/', view=views.ItemSuppliers.as_view()),

    # add supplier to an item
    path('items/suppliers/api/<int:pk>/<int:supplier_id>', view=views.ItemAddSuppliers.as_view()),

    # get all suppliers of an item
    path('items/suppliers/<int:pk>/', view=views.ItemsDetail.as_view()),

    # get list of suppliers and create a supplier
    path('suppliers/api', view=views.SupplierstList.as_view()),

    # get the suppliers details
    path('suppliers/api/<int:pk>/', view=views.SuppliersDetail.as_view()),
]

