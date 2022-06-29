from django.urls import path
from . import views


urlpatterns = [

    path("register/", views.getUsersRigistration, name='register'),
    path("login_users/", views.handleUsersLogin),
    path("profile/", views.dashboard),
    path("logout_users/", views.logout),
    path("user1/", views.registerUser),
    path("user2/", views.registerLawyer),
    path("case/",views.case),
    path("verify/",views.verify),
]
