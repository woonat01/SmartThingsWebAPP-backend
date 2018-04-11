# @Author: Matthew Hale <matthale>
# @Date:   2018-02-28T00:25:25-06:00
# @Email:  mlhale@unomaha.edu
# @Filename: controllers.py
# @Last modified by:   matthale
# @Last modified time: 2018-03-02T04:06:42-06:00
# @Copyright: Copyright (C) 2018 Matthew L. Hale


# Handy Django Functions
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import authenticate, login, logout

# Models and serializers
from django.contrib.auth.models import User
import api.models as api

# REST API Libraries
from rest_framework import viewsets, parsers, renderers
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import list_route
from rest_framework.authentication import *
#email
from templated_email import send_templated_mail
# filters
# from filters.mixins import *
from api.pagination import *
from django.core import serializers
from django.core.exceptions import ValidationError
import json, datetime, pytz
import requests
# bleach for input sanitizing input
import bleach
# re for regex
import re
# os for environment variables
import os

from api.pagination import *
from django.core import serializers
from django.core.validators import validate_email, validate_image_file_extension

def home(request):
	"""
	Send requests to '/' to the ember.js clientside app
	"""

	return render(request, 'index.html')


"""
one post endpoint for lifecycles, must conform to ST reqs must have switch statement for lifecycles
"""
# weather api stuff definitions here
zipcode = "zip=68116"
weatherApiKeyEnv = str(os.getenv('WEATHER_API_KEY'))
#weatherApiKeyLocal = open("/weatherApiKeyLocalTEST.txt", "w")
weatherApiKey = "e5bb4047ac6378185823d9ae5aa2851a"
APPID = "APPID=" + weatherApiKey
weatherURL = ("https://api.openweathermap.org/data/2.5/weather?" + str(zipcode) + "&" + APPID)

class Lifecycles(APIView):
	# interacting with SmartThings Lifecycles



	permission_classes = (AllowAny,)
	parser_classes = (parsers.JSONParser, parsers.FormParser, parsers.MultiPartParser)
	renderer_classes = (renderers.JSONRenderer,)

	def get(self, request):
		print("REQUEST DATA: \n")
		print(str(request.data))
		print("weather URL: " + weatherURL)
		print("weather API key: " + weatherApiKey)
		#print("weather API key Local: " + weatherApiKeyLocal)
		print("weather API key environment variable: " + weatherApiKeyEnv)
		# API call to openweathermap
		currentWeather = requests.get(weatherURL)
		currentWeatherDict = json.loads(currentWeather.text) # converts JSON into dictionary
		print(currentWeatherDict)

		location = currentWeatherDict['name']
		weatherMain = currentWeatherDict['weather']
		print(location)
		print(weatherMain)

		#json_data = json.dumps(currentWeather)
		#description = json_data('weather')['main']

		#print(description)

		#description = currentWeather.json()
		#print(description)
		return Response(currentWeatherDict, content_type='json', status=status.HTTP_200_OK)
	def post(self, request):
		print("REQUEST DATA: \n")
		print(str(request.data))

		lifecycle = bleach.clean(request.data.get('lifecycle'))
		if lifecycle == 'PING':
			print("PING LIFECYCLE")
			print(request.data.get('pingData'))
			print(request.data.get('pingData')["challenge"])
			challenge = bleach.clean(request.data.get('pingData')["challenge"])
			print(challenge)

			# nested dictionary below to send appropriate nested json response
			response = {'pingData': {'challenge': challenge}}
			# garbage return "{\"pingData\": {\"challenge\": \"1a904d57-4fab-4b15-a11e-1c4bfe7cb502\"}}"
			# response = json.dumps({'pingData': {'challenge': challenge }})
			return Response(response, content_type='json', status=status.HTTP_200_OK)

		elif lifecycle == 'CONFIGURATION':
			print("CONFIGURATION LIFECYCLE")

			# this section has more complicated stuff to return

			return JsonResponse(response,  status=status.HTTP_200_OK)

		elif lifecycle == 'INSTALL':
			print("INSTALL LIFECYCLE")
			# do something here

			response = {'installData': {}}
			return Response(response, content_type='json', status=status.HTTP_200_OK)

		elif lifecycle == 'UPDATE':
			print("UPDATE LIFECYCLE")
			# do something here

			response = {'updateData': {}}
			return Response(response, content_type='json', status=status.HTTP_200_OK)

		elif lifecycle == 'UNINSTALL':
			print("UNINSTALL LIFECYCLE")
			# do something here

			response = {'uninstallData': {}}
			return Response(response, content_type='json', status=status.HTTP_200_OK)

		elif lifecycle == 'EVENT':
			print("EVENT LIFECYCLE")
			# weather API here


			# do handleEvent here like set mode (virtual switch) let the app take care of the rest.
			# do something here

			response = {'eventData': {}}
			return Response(response, content_type='json', status=status.HTTP_200_OK)

		else:
			print("Invalid POST")
			return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

class Register(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # Login
		username = request.POST.get('username')
		password = request.POST.get('password')
		email = request.POST.get('email')
		if username is not None and password is not None and email is not None:
	        # lastname = request.POST.get('lastname')
	        # firstname = request.POST.get('firstname')
	        # org = request.POST.get('org')
	        # college = request.POST.get('college')
	        # dept = request.POST.get('dept')
	        # other_details = request.POST.get('otherdetails')
	        # areas_of_interest = request.POST.get('areasofinterest')
	        # areas_of_interest = api.Areaofinterest.objects.get_or_create(name=areas_of_interest)

			print request.POST.get('username')
			if User.objects.filter(username=username).exists():
			    return Response({'username': 'Username is taken.', 'status': 'error'})
			elif User.objects.filter(email=email).exists():
			    return Response({'email': 'Email is taken.', 'status': 'error'})
			# especially before you pass them in here
			newuser = User.objects.create_user(email=email, username=username, password=password)

			newprofile = api.Profile(user=newuser)

			newprofile.save()
			# Send email msg
			# send_templated_mail(
			#     template_name='welcome',
			#     from_email='from@example.com',
			#     recipient_list=[email],
			#     context={
			#         'username':username,
			#         'email':email,
			#     },
			#     # Optional:
			#     # cc=['cc@example.com'],
			#     # bcc=['bcc@example.com'],
			# )
			return Response({'status': 'success', 'userid': newuser.id, 'profile': newprofile.id})
		else:
			return Response({'status': 'error'})


class Session(APIView):
	"""
	Returns a JSON structure: {'isauthenticated':<T|F>,'userid': <int:None>,'username': <string|None>,'profileid': <int|None>}
	"""
	permission_classes = (AllowAny,)
	def form_response(self, isauthenticated, userid, username, profileid, error=""):
		data = {
			'isauthenticated': 	isauthenticated,
			'userid': 			userid,
			'username': 		username,
			'profileid':		profileid,
		}
		if error:
			data['message'] = error

		return Response(data)

	def get(self, request, *args, **kwargs):
		# Get the current user
		user = request.user
		if user.is_authenticated():
			profile = get_object_or_404(api.Profile,user__username=user.username)
			return self.form_response(True, user.id, user.username, profile.id)
		return self.form_response(False, None, None, None)

	def post(self, request, *args, **kwargs):
		print(request.data)
		# Login
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				profile = get_object_or_404(api.Profile,user__username=user.username)
				return self.form_response(True, user.id, user.username, profile.id)
			return self.form_response(False, None, None, None, "Account is suspended")
		return self.form_response(False, None, None, None, "Invalid username or password")

	def delete(self, request, *args, **kwargs):
		# Logout
		logout(request)
		return Response(status=status.HTTP_204_NO_CONTENT)
