import json
import requests
from oauthlib.oauth2 import TokenExpiredError
from requests_oauthlib import OAuth2Session
from rest_framework import authentication, exceptions
import logging
logging.getLogger().setLevel(logging.INFO)
from core.models import Persona, User
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny

class AzureActiveDirectoryAuthentication(authentication.BaseAuthentication):

    def authenticate(self,request):
        token_str = request.META.get('HTTP_X_CSRFTOKEN', '')
        if not token_str:
            return None
        token = {'access_token': token_str}
        print(token)
        user_dict = self.get_user(token)
        #if not user_dict or "userPrincipalName" not in user_dict:
        # Uncomment below line for swagger to work
        if not user_dict:
            raise exceptions.AuthenticationFailed(
                {"status": "Failure", "message": "Invalid token."})
        user = User.objects.filter(
            user_email=user_dict.get("userPrincipalName")).first()
        #user.user_name = user_dict.get("userPrincipalName") # also include user's name for auditing purposes
        if not user:
            try:
                #Uncomment below line for swagger to work
                user = get_user_model().objects.first()
                #user = self.create_user(user_dict)
            except Exception as e:
                raise exceptions.AuthenticationFailed(
                    {"status": "Failure", "message": "User doesn't exist and can't create user.", "error": f'{type(e).__name__} {e.args}'})

        if False in [user.is_active, user.azure_is_active]:
            raise exceptions.AuthenticationFailed(
                {"status": "Failure", "message": "User is unlicensed."})
        return (user, token)

    def get_user(self, token):
        graph_client = OAuth2Session(token=token)
        graph_url = 'https://graph.microsoft.com/v1.0'
        user = graph_client.get(f'{graph_url}/me')
        return user.json()

    def create_user(self, user_dict):
        if not any(email in user_dict["userPrincipalName"] for email in ["@dayandrossinc.ca", "@mccain.ca", "@dayross.com", "@sameday.ca"]):
            raise Exception
        user_kwargs = {"user_name": user_dict["displayName"], "user_email": user_dict["userPrincipalName"],
                       "azure_id": user_dict["id"], "persona": Persona.objects.get_or_create(persona_name="Pricing Manager")[0]}
        user = User(**user_kwargs)
        user.save()
        return user