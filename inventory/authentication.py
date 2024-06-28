import os, datetime, jwt
from django.contrib.auth import authenticate
from django.db.models.functions import Now
import datetime
from rest_framework.response import Response
import secrets
import string
from .models import *
import requests
import json
import re
from django.http import JsonResponse
from .logger import *


"""
This object will be used generate OTP to be sent to the data owner
"""

def generateOTP(user_email):
    # check for otp not expired for user
    # check if requester has same OTP to same data owner email in 24hrs
    try:
        res_otp = OTP.objects.get(
            user_email=user_email,
            created_on__gte=datetime.datetime.now() - datetime.timedelta(days=1),
        )
        res = res_otp.otp_value
    except Exception as e:
        # print(str(e))
        iLog({str(e)})
        N = 7
        res = "".join(
            secrets.choice(string.ascii_uppercase + string.digits) for i in range(N)
        )
        OTP.objects.create(
            user_email=user_email, otp_value=res
        )
        return res


"""
This object will be used to create json web token
"""

def createJWT(username, secret, auth):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now() + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": auth,
        },
        secret,
        algorithm="HS256",
    )


"""
This object will be used to validate the user credentials
"""

def validate_user_credentials(username, password):
    user = authenticate(username=username, password=password)
    if not user:
        return Response({"Message": "Unauthorized access"}, 401)
    return Response({"Message": "Success"}, 200)


"""
This objcet will be authenticate the user credentials
"""

def auth_user(username, password, apikey):
    username, password, apikey = (
        username, password, apikey
    )
    validate_user = validate_user_credentials(username=username, password=password)
    if validate_user.status_code == 200:
        try:
            user_api_key = User.objects.get(username=username).employee.apikey
            if user_api_key == apikey:
                token = createJWT(username, apikey, "admin")
                return Response({"Message": "Success", "SecureToken": token}, 200)
            return Response({"Message": "Invalid apikey provided"}, 400)
        except Exception as e:
            return Response({"Message": "Unauthorized Access"}, 401)
    else:
        return Response({"Message": "Unauthorized Access"}, 401)


"""
This object will validate the user token provided
"""

def validateToken(token, username, password):
    validate_user = validate_user_credentials(username, password)
    if validate_user.status_code == 200:
        try:
            user_obj = User.objects.get(username=username)
            try:
                decoded = jwt.decode(
                    token, user_obj.employee.apikey, algorithms="HS256"
                )
                # print(decoded)
                return Response({"Message": decoded}, 200)
            except Exception as e:
                return Response(
                    {
                        "Message": "Invalid token provided. Please re-authenticate to generate a new token"
                    },
                    400,
                )
        except Exception as e:
            return Response(
                {
                    "Message": "Invalid token provided. Please re-authenticate to generate a new token"
                },
                400,
            )
    return Response({"Message": "Unauthorized access"}, 401)


"""
This object will check that the calling client has provided the
required headers and return specific messages for specific missing headers
"""

def checkHeaders(request):
    try:
        if request.headers["Authorization"].split(" ")[0] == "Bearer":
            if request.headers["Authorization"].split(" ")[1] != "":
                return Response(
                    {
                        "Message": "Success",
                        "token": request.headers["Authorization"].split(" ")[1],
                    },
                    200,
                )
            return Response({"Message": "Please provide token"}, 400)
        return Response({"Message": "Authentication type is Bearer"}, 400)
    except Exception as e:
        return Response({"Message": "Invalid authorization values provided"}, 400)


"""
This object is an abstraction of user authentication that will be used repeatedly
"""

def gen_auth_checker(request):
    username, password = (
        request.data.get("username"),
        request.data.get("password"),
    )
    if checkHeaders(request).status_code == 200:
        token = checkHeaders(request).data.get("token")
        validate_user = validate_user_credentials(username, password)
        if validate_user.status_code == 200:
            validate_token = validateToken(token, username, password)
            if validate_token.status_code == 200:
                return Response({"Message": "Success"}, 200)
            return Response(
                {
                    "Message": "Invalid token provided. Please re-authenticate to generate a new token"
                },
                403,
            )
        return Response({"Message": "Unauthorized access"}, 401)
    return Response({"Message": "Required authorization headers missing"}, 401)
