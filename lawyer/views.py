from django.shortcuts import render, redirect
from django.db import connection
from django.core.paginator import Paginator

# Create your views here.
def dashboard(request):
    dictionary = {"is_active": request.session.has_key('lawyer')}
    if 'lawyer' in request.session:
        return render(request, 'lawyer/dashboard.html',dictionary)
    return render(request,'401.html',dictionary, status=401)

def case(request):
    dictionary = {"is_active": request.session.has_key('lawyer')}
    if 'lawyer' in request.session:
        cur = connection.cursor()
        cur.execute("SELECT verified from user where email=%s",[request.session['lawyer']])
        record = cur.fetchone()[0]
        if record is None:
            dictionary['alert'] = True
            dictionary['message'] = "Please verify your email first."
            cur.close()
            return render(request, 'lawyer/dashboard.html',dictionary)
        query='''SELECT p.id, p.user_id, p.title, p.content, p.timestamp, u.nickname 
                 FROM affair as a 
                 inner join post as p 
                 on a.post_id=p.id 
                 inner join user as u
                 on p.user_id=u.id
                 where a.lawyer_id is NULL order by p.timestamp desc;'''
        cur.execute(query)
        records = cur.fetchall()
        cards = [] # collecting data
        for i in records:
            temp = {}
            temp['id'] = i[0]
            temp['user'] = i[1]
            temp['title'] = i[2]
            temp['content'] = i[3]
            temp['timestamp'] = i[4]
            temp['nick'] = i[5]
            cards.append(temp)

        query='''SELECT p.id, p.user_id, p.title, p.content, p.timestamp, u.nickname 
                 FROM affair as a 
                 inner join post as p 
                 on a.post_id=p.id 
                 inner join user as u
                 on p.user_id=u.id
                 where a.lawyer_id = (select id from user where email=%s) order by p.timestamp desc;'''
        cur.execute(query,[request.session['lawyer']])
        records = cur.fetchall()
        accepted_cards = [] # collecting data
        for i in records:
            temp = {}
            temp['id'] = i[0]
            temp['user'] = i[1]
            temp['title'] = i[2]
            temp['content'] = i[3]
            temp['timestamp'] = i[4]
            temp['nick'] = i[5]
            accepted_cards.append(temp)
        

        paginator = Paginator(cards, 3, orphans=1) # 3 post per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        dictionary['cards'] = page_obj
        dictionary['accepted_cards'] = accepted_cards
        cur.close()
        return render(request, 'lawyer/case.html',dictionary)
    return render(request,'401.html',dictionary, status=401)

def detail_case(request, case_id):
    dictionary = {"is_active": request.session.has_key('lawyer')}
    if request.session.has_key('lawyer'):
        case_id = int(case_id)
        card = {"is_active": request.session.has_key('lawyer')}
        cur = connection.cursor()
        query = '''SELECT p.title, p.content, p.timestamp, u.name, u.nickname, u.email, u.dob, u.verified
        from affair as a
        inner join post as p
        on a.post_id = p.id
        inner join user as u
        on p.user_id = u.id
        where a.post_id = %s and a.lawyer_id = (select id from user where email=%s);
        '''
        cur.execute(query,[case_id, request.session['lawyer']])
        record = cur.fetchone()
        card['title'] = record[0]
        card['content'] = record[1]
        card['timestamp'] = record[2]
        card['username'] = record[3]
        card['usernick'] = record[4]
        card['useremail'] = record[5]
        card['userdob'] = record[6]
        card['userverified'] = True if record[7] is not None else False
        cur.close()
        return render(request,"lawyer/detailcase.html",card)
    return render(request,'401.html',dictionary,status=401)

def accept_case(request,case_id):
    dictionary = {"is_active": request.session.has_key('lawyer')}
    if 'lawyer' in request.session:
        cur = connection.cursor()
        query='''UPDATE affair SET lawyer_id=(select id from user where email=%s) WHERE post_id=%s;'''
        cur.execute(query,[request.session['lawyer'],case_id])
        cur.close()
        return redirect('/lawyer/case')
    return render(request,'401.html',dictionary, status=401)
