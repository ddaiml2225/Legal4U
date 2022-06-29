from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db import connection
from deepface import DeepFace
import tensorflow as tf
from io import BytesIO
import numpy as np
import bcrypt
import base64
import cv2
import re

session = tf.compat.v1.Session()
tf.compat.v1.keras.backend.set_session(session)

def getUsersRigistration(request):
    return render(request, 'register/signup.html',{"is_active": request.session.has_key('user') or request.session.has_key('lawyer')})


def handleUsersLogin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user_type = request.POST['usertyp']
        dbCompannion = connection.cursor()
        dbCompannion.execute(
            'SELECT pswd, role FROM user WHERE email = %s', [email])
        data = dbCompannion.fetchall()
        dbCompannion.close()
        # checks if any such record exists
        if len(data) == 0:
            return render(request, 'index.html', {'indres': 1})
            # return HttpResponse('Not Registered Account')
        pswd = data[0][0]
        role = data[0][1]
        # verifing password
        if bcrypt.checkpw(password.encode('utf-8'), pswd.encode('utf-8')):
            # verifing role and entered role
            if role is None and user_type == 'V':
                request.session['user'] = email
                return redirect('/feed')  # redirecting to dashboard
                # return HttpResponse('Logged in as Victim')
            elif role is not None and user_type == 'L':
                request.session['lawyer'] = email
                return redirect('/lawyer') # redirecting to dashboard
            else:
                return HttpResponse('Not Valid Registration')

        else:
            # return HttpResponse('Incorrect password !')
            return render(request, 'index.html', {'invalid': 1})
    return HttpResponse('404')


def dashboard(request):
    dictionary = {"is_active": request.session.has_key('user'),'alert':False}
    if request.session.has_key('user'):
        query = '''SELECT p.id, p.user_id, p.title, p.content, p.timestamp, u.nickname , a.lawyer_id, u.verified
                    FROM post as p 
                    inner join user as u 
                    on p.user_id=u.id 
                    inner join affair as a
                    on p.id=a.post_id
                    where u.email = %s
                    order by p.timestamp desc;'''
        cur = connection.cursor()
        cur.execute(query,[request.session['user']])
        records = cur.fetchall()
        cur.execute("select verified from user where email = %s",[request.session['user']])
        verified = cur.fetchone()
        dictionary['user_verified'] = True if verified else False
        cur.close()
        cards = [] # collecting data
        for i in records:
            temp = {}
            temp['id'] = i[0]
            temp['user'] = i[1]
            temp['title'] = i[2]
            temp['content'] = i[3]
            temp['timestamp'] = i[4]
            temp['nick'] = i[5]
            temp['status'] = 'success' if i[6] else 'secondary'
            temp['verified'] = True if i[7]=="" else False
            cards.append(temp)
        paginator = Paginator(cards, 3, orphans=1) # 3 post per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        dictionary['cards'] = page_obj
        return render(request,'register/dashboard.html',dictionary) # dashboard
    return render(request,'401.html',dictionary, status=401)

def verify(request):
    dictionary = {"is_active": request.session.has_key('user')}
    if 'user' in request.session:
        if request.method=="POST":
            data=request.POST
            image_width = int(data.get('width'))
            image_height = int(data.get('height'))
            face = data.get('face')
            face = re.sub("^data:image/jpeg;base64,", "", face)
            face = base64.b64decode(face)
            face = BytesIO(face)
            img = cv2.imdecode(np.frombuffer(face.read(), np.uint8), 1)
            with session.as_default():
                with session.graph.as_default():
                    try:
                        status = DeepFace.analyze(img,actions=['gender'])['gender']
                    except:
                        dictionary['alert'] = True
                        dictionary['status'] = 'danger'
                        dictionary['heading'] = 'Failed'
                        dictionary['message'] = "Face cannot be detected"
                        return render(request,"register/verify.html",dictionary)
            if status == 'Woman':
                cur = connection.cursor()
                query = '''update user set verified = ""
                where email = %s;
                '''
                cur.execute(query,[request.session['user']])
                cur.close()
                dictionary['alert'] = True
                dictionary['status'] = 'success'
                dictionary['heading'] = 'Success'
                dictionary['message'] = "User verified"
            else:
                dictionary['alert'] = True
                dictionary['status'] = 'danger'
                dictionary['heading'] = 'Failed'
                dictionary['message'] = "User is Not a Woman. Only woman can be verified"
        return render(request,"register/verify.html",dictionary)
    return render(request,'401.html',dictionary, status=401)

def registerUser(request):
    if request.method == 'POST':
        name = request.POST['fname']
        dob = request.POST['dob']
        email = request.POST['email']
        password = request.POST['password']
        # aadhar = request.POST['aadhar']
        nick = request.POST['nick']
        hsdPassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        dbCompannion = connection.cursor()
        dbCompannion.execute(f"SELECT id FROM user WHERE email='{email}';")
        record = dbCompannion.fetchone()
        if record is not None:
            dbCompannion.close()
            return HttpResponse('Email already registered')
        dbCompannion.execute(f"SELECT id FROM user WHERE nickname='{nick}';")
        record = dbCompannion.fetchone()
        if record is not None:
            dbCompannion.close()
            return HttpResponse('NickName already registered, Pick another one')
        else:
            dbCompannion.execute("INSERT INTO user (name,dob,email,pswd,nickname) VALUES (%s,%s,%s,%s,%s);", [
                                 name, dob, email, hsdPassword, nick])
            # dbCompannion.execute(f"SELECT id FROM user WHERE email='{email}';")
            # userid = dbCompannion.fetchone()
            # dbCompannion.execute(
            #     "INSERT INTO victim (aadhar, user_id) VALUES (%s,%s);", [aadhar, userid])
            dbCompannion.close()
            return redirect('/')
        # try:
        #     dbCompannion.execute(
        #         'INSERT INTO victim(email,name,mobile,password) VALUES (%s,%s,%s,%s)', [email, name, mobNo, hsdPassword])
        #     return HttpResponse('Data inserted !')
        # except:
        #     return HttpResponse('Failed !')
            # return render(request, 'register/signup.html',{'error':1})
    return HttpResponse('404')


def registerLawyer(request):

    if request.method == 'POST':
        name = request.POST['fname']
        dob = request.POST['dob']
        email = request.POST['email']
        password = request.POST['password']
        enroll_id = request.POST['enroll_id']
        gender = "" if request.POST['gender'] == 'M' else None
        yearOfExp = request.POST['exp']
        file = request.FILES['idImg']
        mobNo = request.POST['number']
        nick = request.POST['nick']
        role = ""

        file_name = file.name
        temp = bytes('', encoding='utf-8')
        for chunk in file.chunks():
            temp += chunk
        file = base64.b64encode(temp)

        hsdPassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        dbCompannion = connection.cursor()
        dbCompannion.execute(f"SELECT id FROM user WHERE email='{email}';")
        record = dbCompannion.fetchone()
        if record is not None:
            dbCompannion.close()
            return HttpResponse('Email already registered')
        else:
            dbCompannion.execute("INSERT INTO user (name,dob,email,pswd,role,nickname) VALUES (%s,%s,%s,%s,%s,%s);", [
                                 name, dob, email, hsdPassword, role, nick])
            dbCompannion.execute(f"SELECT id FROM user WHERE email='{email}';")
            userid = dbCompannion.fetchone()
            dbCompannion.execute("INSERT INTO lawyer (enroll_id, sex, exp, proof, phone, user_id) VALUES (%s,%s,%s,%s,%s,%s);", [
                                 enroll_id, gender, yearOfExp, file, mobNo, userid])
            dbCompannion.close()
            return redirect('/')
        # try:
        #     dbCompannion.execute(
        #         'INSERT INTO lawyer(email,name,mobile,password,year_exp,gender,dob,probono,id_proof,img_name) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', [email, name, mobNo, hsdPassword, yearOfExp, gender, dob, probono, file, file_name])
        #     return HttpResponse('Data inserted !')
        # except:
        #     return HttpResponse('Failed !')
            # return render(request, 'register/signup.html',{'error':1})
    return HttpResponse('404')


def logout(request):
    if request.session.has_key('user'):
        del request.session['user']
    elif request.session.has_key('lawyer'):
        del request.session['lawyer']
    else:
        del request.session['admin']
    return redirect('/')

def case(request):
    dictionary = {"is_active": request.session.has_key('user')}
    if request.session.has_key('user'):
        if request.method=="POST":
            data = request.POST
            title = data['title']
            content = data['content']
            cur = connection.cursor()
            query = "INSERT INTO post (user_id,title,content) VALUES ((SELECT id FROM user WHERE email= %s),%s,%s);"
            cur.execute(query,[request.session['user'], title, content])
            cur.execute("SELECT id from post where user_id = (SELECT id FROM user WHERE email= %s) and title =%s and content=%s;",[request.session['user'], title, content])
            post_id = cur.fetchone()[0]
            cur.execute("INSERT INTO affair (post_id) values (%s);",[post_id])
            dictionary['alert'] = True
            cur.close()
            return redirect('/auth/profile')
        return HttpResponse('404')
    return render(request,'401.html',dictionary,status=401)