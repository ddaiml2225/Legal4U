from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard),
    path("case",views.case),
    path("case/<int:case_id>",views.accept_case),
    path("case/detail/<int:case_id>",views.detail_case),
]