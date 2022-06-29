from django.shortcuts import render

# Create your views here.
def chatbot_page(request):
    return render(request, "chatbot/chatbot.html",{"is_active": request.session.has_key('user') or request.session.has_key('lawyer')})