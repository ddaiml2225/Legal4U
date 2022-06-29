from django.urls import path
from . import views


urlpatterns = [

    path("", views.feed),
    path("<int:post_id>", views.post),
    path("case/<int:case_id>", views.case),
]