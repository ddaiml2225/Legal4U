from django.urls import path
from . import views

urlpatterns = [
    path("",views.dashboard),
    path("login", views.login),
    path("register", views.register),
    path("verify", views.verify_lawyer),
    path("verify/<int:user_id>", views.detail),
    path("verified/<int:user_id>", views.verified),
    path("check", views.check),

]