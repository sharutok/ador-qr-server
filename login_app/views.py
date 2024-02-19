from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from login_app.models import AdminUsers
from login_app.sequelizers import AdminUsersSerializers
import bcrypt

@api_view(['POST'])
def create_user(request):
    try:
        print(request.data)
        unsalted_password = str(request.data["password"]).encode("utf-8")
        salted_password = bcrypt.hashpw(unsalted_password, bcrypt.gensalt(rounds=10))
        request.data["password"] = salted_password.decode()
        print(request.data)
        serializers=AdminUsersSerializers(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response({'status_code':200})
    except Exception as e:
        print("create_user",e)
        return Response({'status_code':400})
        


@api_view(['POST'])
def verify_user(request):
    try:
        user = request.data["user"]
        password = request.data["password"]
        if user:
            queryset_email = AdminUsers.objects.filter(user=user)
            obj = AdminUsers.objects.get(user=user)
            serializers = AdminUsersSerializers(obj)
            if queryset_email.exists():
                queryset_email = AdminUsers.objects.get(user=user)
                serializers = AdminUsersSerializers(queryset_email)
                hashed_password_from_database = serializers.data["password"].encode(
                    "utf-8"
                )
                provided_password = password.encode("utf-8")
                if bcrypt.checkpw(provided_password, hashed_password_from_database):
                    return Response(
                        {
                            "status": 200,
                            "emp_no": serializers.data["id"],
                        },
                    )
                else:
                    return Response({"status":400,'mess':'Incorrect username or password'})
            else:
                return Response({"status":400,'mess':'Incorrect username or password'})
    except Exception as e:
        print("verify_user",e)
        return Response({"status": 404,'mess':'Incorrect username or password'})
        

