from django.shortcuts import render

# Create your views here.


def getMainHome(request):
    return render(request, 'index.html',{"is_active": request.session.has_key('user') or request.session.has_key('lawyer')})
