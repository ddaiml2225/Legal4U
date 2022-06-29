from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db import connection
import bcrypt

# cur = connection.cursor()

# Create your views here.
def dashboard(request):
    dictionary = {"alert":False,"is_active":request.session.has_key('admin')}
    if request.session.has_key('admin'):
        return render(request,'admin/dashboard.html',dictionary)
    return render(request,'401.html',dictionary,status=401)

def login(request):
    dictionary = {"alert": False, "is_active": request.session.has_key('admin')}
    if request.method == "POST":
        data = request.POST
        email = data['email']
        password = data['password']
        cur = connection.cursor()
        cur.execute("SELECT pswd FROM admin where email=%s;",[email])
        pswd = cur.fetchone()
        cur.close()
        if pswd is None:
            dictionary['alert'] = True
            return render(request, 'admin/adminLogin.html', dictionary)
        pswd = pswd[0]
        if bcrypt.checkpw(password.encode('utf-8'), pswd.encode('utf-8')):
        # if password == pswd:
            request.session['admin'] = email
            return redirect('/admin')
        dictionary['alert'] = True
    return render(request, 'admin/adminLogin.html', dictionary)

def register(request):
    dictionary = {"is_active": request.session.has_key('admin')}
    if request.session.has_key('admin'):
        if request.method == "POST":
            data = request.POST
            name=data['name']
            email=data['email']
            dob=data['dob']
            password=data['password']
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cur = connection.cursor()
            cur.execute("insert into admin (name,dob,email,pswd) values (%s,%s,%s,%s);",[name,dob,email,hashed])
            cur.close()
            dictionary['alert'] = True
            return render(request,'admin/dashboard.html',dictionary)
        return render(request, 'admin/register.html', dictionary)
    return render(request,'401.html',dictionary,status=401)

def verify_lawyer(request):
    dictionary = {"is_active": request.session.has_key('admin')}
    if request.session.has_key('admin'):
        # count of unverified lawyers
        query = ''' SELECT COUNT(l.enroll_id) 
                    FROM lawyer AS l 
                    INNER JOIN user AS u
                    ON l.user_id = u.id
                    WHERE u.verified IS NULL;'''
        cur = connection.cursor()
        cur.execute(query)
        unverified = cur.fetchone()[0]
        dictionary['unverified'] = unverified
        # count of verified lawyers
        query = ''' SELECT COUNT(l.enroll_id) 
                    FROM lawyer AS l 
                    INNER JOIN user AS u
                    ON l.user_id = u.id
                    WHERE u.verified = %s;'''
        cur.execute(query,[""])
        verified = cur.fetchone()[0]
        dictionary['verified'] = verified
        #total
        dictionary['total'] = unverified + verified
        dictionary['progress'] = (verified/dictionary['total'])*100
        # data of unverified
        query = ''' SELECT u.id, u.name, u.dob, l.enroll_id, l.sex, l.exp 
                    FROM lawyer AS l
                    INNER JOIN user AS u
                    ON l.user_id=u.id
                    WHERE u.role = %s AND u.verified IS NULL;'''
        cur.execute(query,[""])
        records = cur.fetchall()
        cur.close()
        cards = [] # collecting data
        for i in records:
            temp = {}
            temp['id'] = i[0]
            temp['name'] = i[1]
            temp['dob'] = i[2]
            temp['enroll'] = i[3]
            temp['sex'] = "Male" if i[4]=="" else "Female"
            temp['exp'] = i[5]
            cards.append(temp)
        paginator = Paginator(cards, 9, orphans=1) # 9 lawyer per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        dictionary['cards'] =  page_obj
        return render(request, 'admin/verifyLawyer.html', dictionary)
    return render(request,'401.html',dictionary,status=401)

def detail(request, user_id):
    dictionary = {"is_active": request.session.has_key('admin')}
    if request.session.has_key('admin'):
        query = ''' SELECT u.id, u.name, u.nickname, u.dob, u.email, l.enroll_id, l.sex, l.exp, l.proof, l.phone
                    FROM lawyer AS l
                    INNER JOIN user AS u
                    ON l.user_id = u.id
                    WHERE u.id = %s;'''
        cur = connection.cursor()
        cur.execute(query,[user_id])
        record = cur.fetchone()
        cur.close()
        dictionary['id'] = record[0]
        dictionary['name'] = record[1]
        dictionary['nickname'] = record[2]
        dictionary['dob'] = record[3]
        dictionary['email'] = record[4]
        dictionary['enroll'] = record[5]
        dictionary['sex'] = "Male" if record[6]=="" else "Female"
        dictionary['exp'] = record[7]
        dictionary['proof'] = "data:image/png;base64,"+record[8].decode('utf-8')
        dictionary['phone'] = record[9]
        return render(request, 'admin/verifyDetail.html', dictionary)
    return render(request,'401.html',dictionary,status=401)

def verified(request, user_id):
    dictionary = {"is_active": request.session.has_key('admin')}
    if request.session.has_key('admin'):
        query = ''' UPDATE user SET verified = %s WHERE id = %s;'''
        cur = connection.cursor()
        cur.execute(query,["",user_id])
        cur.close()
        return redirect('/admin/verify')

def check(request):
    dictionary = {"is_active": request.session.has_key('admin')}
    if request.session.has_key('admin'):
        query = '''select u.nickname, u.email 
            from user as u
            where u.verified is null and u.role="";'''
        cur = connection.cursor()
        cur.execute(query)
        records = cur.fetchall()
        unverified_lawyers = []
        for i in records:
            unverified_lawyers.append({
                'nick': i[0],
                'email': i[1]
            })
        dictionary['unverified_lawyers'] = unverified_lawyers

        query = '''select u.nickname, u.email 
            from user as u
            where u.verified="" and u.role="";'''
        cur.execute(query)
        records = cur.fetchall()
        verified_lawyers = []
        for i in records:
            verified_lawyers.append({
                'nick': i[0],
                'email': i[1]
            })
        dictionary['verified_lawyers'] = verified_lawyers

        query = '''select u.nickname, u.email 
            from user as u
            where u.verified is null and u.role is null;'''
        cur.execute(query)
        records = cur.fetchall()
        unverified_users = []
        for i in records:
            unverified_users.append({
                'nick': i[0],
                'email': i[1]
            })
        dictionary['unverified_users'] = unverified_users

        query = '''select u.nickname, u.email 
            from user as u
            where u.verified="" and u.role is null;'''
        cur.execute(query)
        records = cur.fetchall()
        verified_users = []
        for i in records:
            verified_users.append({
                'nick': i[0],
                'email': i[1]
            })
        dictionary['verified_users'] = verified_users
        cur.close()
        return render(request,"admin/check.html",dictionary)
    return render(request,'401.html',dictionary,status=401)