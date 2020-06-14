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
        text = '''SELECT id FROM geo WHERE city = "{}"'''.format(city)
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
        res = cursor.fetchall()
        try: 
            if type(res[0][0]) == int:
                request.session['login'] = True
                request.session['id'] = res[0][0]
                return redirect('http://0.0.0.0:8080/spheres')
        except IndexError:
            return redirect('http://0.0.0.0:8080/login')                 
    return render(request, 'login.html')

def spheres(request):
    return render(request, 'spheres.html')

def znakomstva(request):
    if request.session.get('login') == True:
        return render(request, 'test.html', {'idha': request.session['id']})
    else:
        return redirect('http://0.0.0.0:8080/login')

def test(request):
    return render(request, 'test.html')

#APIS

def api_search_meets(request, idha, from_years, to_years, pp):
    cnx = mysql.connector.connect(user='root', password='root',host='docker.for.mac.localhost',database='znakomstva')
    cursor = cnx.cursor()
    text = '''select city_id, lang_id from users where id = {}'''.format(idha)
    cursor.execute(text)
    res = cursor.fetchall()
    lang_id = res[0][1]
    city_id = res[0][0]
    text = '''select name, instagram, facebook, vkontakte from users where (
                (YEAR(CURRENT_DATE) - YEAR(birthday)) -                            
                (DATE_FORMAT(CURRENT_DATE, '%m%d') < DATE_FORMAT(birthday, '%m%d'))
            ) <= {} and {} <= (
                (YEAR(CURRENT_DATE) - YEAR(birthday)) -                            
                (DATE_FORMAT(CURRENT_DATE, '%m%d') < DATE_FORMAT(birthday, '%m%d'))
            ) and city_id = {} and lang_id = {};'''.format(to_years, from_years, city_id, lang_id)
    cursor.execute(text)
    res = cursor.fetchall()
    res_json = []
    for i in res:
        js = {"name": i[0], "instagram": i[1], "facebook": i[2], "vkontakte": i[3]}
        res_json.append(js)
    print(res_json)
    return JsonResponse(res_json, safe=False)

def api_test(request, from_years, to_years, rad):
    if request.method == 'GET' and request.session.get('login'):
        city_id = None
        lat = None
        lng = None
        cities = None
        big_res = {}
        cnx = mysql.connector.connect(user='root', password='root',host='docker.for.mac.localhost',database='znakomstva')
        cursor = cnx.cursor()
        text = ''' select city_id, lang_id from users where id = {}'''.format(request.session['id'])
        cursor.execute(text)
        res = cursor.fetchall()
        city_id = res[0][0]
        lang_id = res[0][1]
        text = ''' select lat, lng from geo where id = {} '''.format(city_id)
        cursor.execute(text)
        res = cursor.fetchall()[0]
        lat = res[0]
        lng = res[1]
        text = ''' select id, city, lat, lng from geo where 6371 * ACOS(cos(radians(lat)) * cos(radians({})) * cos(radians(lng) - radians({})) + sin(radians(lat)) * sin(radians({}))) <= {} '''.format(lat, lng, lat, rad)
        cursor.execute(text)
        cities = cursor.fetchall()
        mas = []
        for i in cities:
            text = ''' select name, instagram, facebook, vkontakte from users where (
                (YEAR(CURRENT_DATE) - YEAR(birthday)) -                            
                (DATE_FORMAT(CURRENT_DATE, '%m%d') < DATE_FORMAT(birthday, '%m%d'))
            ) <= {} and {} <= (
                (YEAR(CURRENT_DATE) - YEAR(birthday)) -                            
                (DATE_FORMAT(CURRENT_DATE, '%m%d') < DATE_FORMAT(birthday, '%m%d'))
            ) and city_id = {} and lang_id = {} and id != {}'''.format(to_years, from_years, i[0], lang_id, request.session['id'])
            cursor.execute(text)
            res = cursor.fetchall()
            if res != []:
                for b in res:
                    ret = {'name': b[0], 'instagram': b[1], 'facebook': b[2], 'vkontakte': b[3]}
                    mas.append(ret)
                all_people = {'count': len(mas), 'lat': i[2], 'lng': i[3]}
                mas.append(all_people)
                big_res[i[1]] = mas
            mas = []
        print(big_res)
        return JsonResponse(big_res, safe=False) 
    else:
        return redirect('http://0.0.0.0:8080/login')

def api_user_id(request):
    if request.method == 'GET' and request.session.get('login'):
        res = {'id': request.session.get('id')}
        return JsonResponse(res, safe=False)     