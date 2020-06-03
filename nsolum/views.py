from django.shortcuts import render
from django import forms
from django.utils.translation import ugettext as _
from django.shortcuts import redirect
from django.http import JsonResponse
import http.cookies
import urllib.request
import requests
import json

def welcome_page(request):
    return render(request, 'main_page.html')

def registration(request):
    return render(request, 'registration.html')