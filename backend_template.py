from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import Student
from django.db import connection


def getHome(request):
    data = Student.objects.raw('SELECT * from myapp_student')
    return render(request, 'index.html', {'title': 'Home', 'route': 'home', 'data': data})


def getLogin(request):
    return render(request, 'login.html', {'title': 'Login', 'route': 'login'})


def getAboutUs(request):
    if request.session.has_key('user'):
        return render(request, 'about.html', {'title': 'About us', 'route': 'about', 'user': request.session['user']})
    return HttpResponse('Not logged in !')


def getData(request):
    if request.method == 'POST':
        dbCompannion = connection.cursor()
        sid = request.POST['sid']
        name = request.POST['name']
        branch = request.POST['branch']
        try:
            dbCompannion.execute(
                'INSERT INTO myapp_student(sid,name,branch) VALUES (%s,%s,%s)', [sid, name, branch])
            return HttpResponse('Data inserted !')
        except:
            return HttpResponse('Failed !')
            # return render(request, 'index.html', {'err': 1})
    return HttpResponse('404')


def updateData(request):
    # dbCompannion = connection.cursor()
    # dbCompannion.execute('SELECT sid,name,branch FROM myapp_student')
    # data = dbCompannion.fetchall()
    data = Student.objects.raw(
        'SELECT sid,name,branch FROM myapp_student WHERE sid = %s', [222])

    return render(request, 'update.html', {'data': data, 'title': 'Edit', 'branches': ['IT', 'CSE', 'ENTC', 'CIVIL']})


def handelUpdate(request):
    if request.method == 'POST':
        dbCompannion = connection.cursor()
        sid = request.POST['sid']
        name = request.POST['name']
        branch = request.POST['branch']
        try:
            dbCompannion.execute(
                'UPDATE myapp_student SET  name = %s ,branch = %s WHERE sid = %s', (name, branch, sid))
            return redirect('/v1/edit/')
        except:
            return HttpResponse('Failed !')
    return HttpResponse('404')


def loginUser(request):
    if request.method == 'POST':
        sid = request.POST['sid']
        request.session['user'] = sid
        return redirect('/v1/about/')
    return HttpResponse('404')


def logoutUser(request):
    request.session.flush()
    return redirect('/v1/login/')
