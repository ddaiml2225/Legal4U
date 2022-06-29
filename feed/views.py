from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from django.core.paginator import Paginator
from collections import deque

# cur = connection.cursor()
# Create your views here.

def feed(request):
    dictionary = {"is_active": request.session.has_key('user') or request.session.has_key('lawyer')}
    if request.session.has_key('user') or request.session.has_key('lawyer'):
        session_user = 'user' if request.session.has_key('user') else 'lawyer'
        if request.method == 'POST':
            title = request.POST['title']
            content = request.POST['content']
            query = '''INSERT INTO post (user_id, title, content) VALUES ((SELECT id FROM user WHERE email= %s), %s, %s);'''
            cur = connection.cursor()
            cur.execute(query, [request.session[session_user], title, content])
            cur.close()
            # return redirect('/auth/profile')
        cur = connection.cursor()
        cur.execute("SELECT p.id, p.user_id, p.title, p.content, p.timestamp, u.nickname, u.verified FROM post as p inner join user as u on p.user_id=u.id where p.reply_id is null and p.id not in (select a.post_id from affair as a) order by p.timestamp desc;")
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
            temp['verified'] = True if i[6]=="" else False
            cur.execute("select enroll_id from lawyer where user_id=%s;", [i[1]])
            temp['is_lawyer'] = True if cur.fetchone() else False
            cards.append(temp)
        paginator = Paginator(cards, 3, orphans=1) # 3 post per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        dictionary['cards'] = page_obj
        cur.close()
        return render(request, 'feed/feed.html', dictionary)
    return render(request,'401.html',dictionary,status=401)

def post(request,post_id):
    dictionary = {"is_active": request.session.has_key('user') or request.session.has_key('lawyer')}
    if request.session.has_key('user') or request.session.has_key('lawyer'):
        session_user = 'user' if request.session.has_key('user') else 'lawyer'
        # if request is a reply to some post
        if request.method == 'POST': 
            title = request.POST['title']
            content = request.POST['content']
            reply_id = request.POST['reply_id']
            query = '''INSERT INTO post (user_id, title, content, reply_id) VALUES ((SELECT id FROM user WHERE email= %s),%s,%s,%s);'''
            cur = connection.cursor()
            cur.execute(query, [request.session[session_user], title, content, reply_id])
            cur.close()
            # return redirect('/feed/'+str(post_id))
        comments = dfs(post_id) # collecting data
        paginator = Paginator(comments, 3, orphans=1) # 3 post per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        dictionary['comments'] = page_obj
        return render(request, 'feed/post.html', dictionary)
    return render(request,'401.html',dictionary,status=401)

def dfs(post_id):
    # performs a depth-first-search for the given post in database, and returns list of json-data

    list_id = deque() # queue for maintaining dfs
    remaining = deque() # stack for maintaining dfs
    remaining.append(post_id)
    # while stack is not empty, pop element and search all children of that element
    cur = connection.cursor()
    while remaining:
        temp_id = remaining.pop()
        # add individual element to queue to maintain order
        list_id.append(temp_id)
        cur.execute(f"select id from post where reply_id={temp_id};")
        records = cur.fetchall()
        # add all children to stack
        for i in records:
            remaining.append(i[0])

    if len(list_id) > 1: # if post has childern
        ids_str = ", ".join(str(i) for i in list_id)
        cur.execute(f"SELECT p.id, p.user_id, p.title, p.content, p.timestamp, p.reply_id, u.nickname, u.verified FROM post as p inner join user as u on p.user_id=u.id where p.id IN {tuple(list_id)} order by FIELD(p.id, {ids_str});")
    else: # if post has no children
        cur.execute(f"SELECT p.id, p.user_id, p.title, p.content, p.timestamp, p.reply_id, u.nickname, u.verified FROM post as p inner join user as u on p.user_id=u.id where p.id = {list_id.pop()};")
    records = cur.fetchall()
    
    counter = 0 # calculating indent level
    reply_ids = {} # hashing id for indent level
    comments = [] # storing all data
    for i in records:
        temp = {}
        temp['id'] = i[0]
        temp['user'] = i[1]
        temp['title'] = i[2]
        temp['content'] = i[3]
        temp['timestamp'] = i[4]
        temp['reply_id'] = i[5]
        temp['nick'] = i[6]
        temp['verified'] = True if i[7]=="" else False
        cur.execute("select enroll_id from lawyer where user_id=%s;", [i[1]])
        temp['is_lawyer'] = True if cur.fetchone() else False

        # if reply_id not in hash table, add it and increment counter
        if i[5] not in reply_ids.keys():
            counter += 2
            reply_ids[i[5]] = counter
        # else fetch indentation level for that reply_id
        else:
            counter = reply_ids[i[5]]
        temp['indent'] = reply_ids[i[5]]

        # print(f"post id: {i[0]}, replying to: {i[5]}, counter: {temp['indent']}")
        comments.append(temp)
    cur.close()
    return comments

def case(request,case_id):
    dictionary = {"is_active": request.session.has_key('user')}
    if request.session.has_key('user'):
        case_id = int(case_id)
        card = {"is_active": request.session.has_key('user')}
        cur = connection.cursor()
        cur.execute("SELECT lawyer_id from affair where post_id = %s;",[case_id])
        record = cur.fetchone()[0]
        if record is None:
            query = '''select p.title, p.content, p.timestamp, vu.name, vu.verified
                    from affair as a
                    inner join post as p
                    on a.post_id = p.id
                    inner join user as vu
                    on p.user_id = vu.id
                    where a.post_id=%s;
            '''
            cur.execute(query,[case_id])
            record = cur.fetchone()
            card['status']='secondary'
            card['title']=record[0]
            card['content']=record[1]
            card['timestamp']=record[2]
            card['username']=record[3]
            card['verified']=True if record[4]=="" else False
        else:
            query = '''select p.title, p.content, p.timestamp, vu.name, lu.name, lu.email, l.sex, l.exp, l.phone, vu.verified
                    from affair as a
                    inner join post as p
                    on a.post_id=p.id
                    inner join user as vu
                    on p.user_id = vu.id
                    inner join user as lu
                    on a.lawyer_id=lu.id
                    inner join lawyer as l
                    on lu.id = l.user_id
                    where a.post_id = %s;
            '''
            cur.execute(query,[case_id])
            record = cur.fetchone()
            card['status'] = 'success'
            card['title'] = record[0]
            card['content'] = record[1]
            card['timestamp'] = record[2]
            card['username'] = record[3]
            card['lawyername'] = record[4]
            card['lawyeremail'] = record[5]
            card['lawyersex'] = "Male" if record[6] == "" else "Female"
            card['lawyerexp'] = record[7]
            card['lawyerphone'] = record[8]
            card['verified'] = True if record[9]=="" else False
        cur.close()
        return render(request,"feed/case.html",card)
    return render(request,'401.html',dictionary,status=401)