from django.shortcuts import render
from django import forms
from django.utils.translation import ugettext as _
from django.shortcuts import redirect
from django.http import JsonResponse
import http.cookies
import urllib.request
import requests
import mysql.connector
import json

class UserRegistrationForm(forms.Form):
    name = forms.CharField(label=_(u'name'))
    surname = forms.CharField(label=_(u'surname'))
    email = forms.CharField(label=_(u'email'))
    password = forms.CharField(label=_(u'password'))
    city = forms.CharField(label=_(u'city'))
    lang = forms.CharField(label=_(u'lang'))
    birthday = forms.CharField(label=_(u'birthday'))

class LoginForm(forms.Form):
    email = forms.CharField(label=_(u'email'))
    password = forms.CharField(label=_(u'password'))    

def welcome_page(request):
    return render(request, 'main_page.html')

def registration(request):
    form = UserRegistrationForm(data=request.POST)
    if request.method == 'POST' and form.is_valid():
        name = form.cleaned_data.get('name', None)
        surname = form.cleaned_data.get('surname', None)
        email = form.cleaned_data.get('email', None)
        password = form.cleaned_data.get('password', None)
        city = form.cleaned_data.get('city', None)
        lang = form.cleaned_data.get('lang', None)
        birthday = form.cleaned_data.get('birthday', None)
        cnx = mysql.connector.connect(user='root', password='root',host='docker.for.mac.localhost',database='znakomstva')
        cursor = cnx.cursor()
        text = '''SELECT id FROM cities WHERE name = "{}"'''.format(city)
        cursor.execute(text)
        city = cursor.fetchall()[0][0]
        text = '''SELECT id FROM langs WHERE name = "{}"'''.format(lang)
        cursor.execute(text)
        lang = cursor.fetchall()[0][0]
        text = '''INSERT INTO users(name, surname, email, password, city_id, lang_id, birthday, instagram) VALUES 
        ("{}","{}","{}","{}",{},{},"{}","https://www.instagram.com/artemzinkovetss/")'''.format(name, surname, email, password, city, lang, birthday)  
        cursor.execute(text)
        cnx.commit()
        cnx.close()
        return redirect('http://0.0.0.0:8080/welcome_page')      
    return render(request, 'registration.html')

def login(request):
    form = LoginForm(data=request.POST)
    print(form.is_valid())
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data.get('email', None)
        password = form.cleaned_data.get('password', None)
        cnx = mysql.connector.connect(user='root', password='root',host='docker.for.mac.localhost',database='znakomstva')
        cursor = cnx.cursor()
        text = '''SELECT id FROM users WHERE email = "{}" AND password = "{}"'''.format(email, password)
        cursor.execute(text)
        try: 
            type(cursor.fetchall()[0][0])
            request.session['login'] = True
            request.session['id'] = cursor.fetchall()[0][0]
            return redirect('http://0.0.0.0:8080/spheres')
        except IndexError:
            return redirect('http://0.0.0.0:8080/login')                 
    return render(request, 'login.html')

def spheres(request):
    return render(request, 'spheres.html')

def znakomstva(request):
    if request.session['login']:
        return render(request, 'znakomstva.html', {'idha': request.session['id']})
    else:
        return render(request, 'login.html')

def test(request):
    return render(request, 'test.html')

def api_search_meets(request, idha, from_years, to_years):
    cnx = mysql.connector.connect(user='root', password='root',host='docker.for.mac.localhost',database='znakomstva')
    cursor = cnx.cursor()
    text = ''' select name, instagram, facebook, vkontakte from users where (
                (YEAR(CURRENT_DATE) - YEAR(birthday)) -                            
                (DATE_FORMAT(CURRENT_DATE, '%m%d') < DATE_FORMAT(birthday, '%m%d'))
            ) <= {} and {} <= (
                (YEAR(CURRENT_DATE) - YEAR(birthday)) -                            
                (DATE_FORMAT(CURRENT_DATE, '%m%d') < DATE_FORMAT(birthday, '%m%d'))
            ) and city_id = {} and lang_id = {};  '''
