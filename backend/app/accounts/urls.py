from django.urls import path

from . import views

urlpatterns = [
    path("auth/login", views.LoginView.as_view(), name="auth-login"),
    path("auth/refresh", views.RefreshView.as_view(), name="auth-refresh"),
    path("me", views.me, name="me"),
    path("invoices", views.InvoiceListView.as_view(), name="invoice-list"),
]
