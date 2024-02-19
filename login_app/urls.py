from django.urls import path, include
from login_app.views import (create_user,verify_user)

urlpatterns = [
    path("create/", create_user, name="create-user"),
    path("verify/", verify_user, name="verify-user"),
]
