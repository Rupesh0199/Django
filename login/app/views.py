from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
import requests, random, string, os, collections
import pandas as pd
from datetime import datetime
from .models import Security, Userinfo
from . middleware import secureRequest, secureRequestmenu
from passlib.hash import pbkdf2_sha256

# Create your views here.


def generateUSID():
    rand = ''.join(random.choices(string.ascii_letters, k=50))
    return "u"+str(int(datetime.now().timestamp()))+rand

def home(request):
    return redirect('login')

@csrf_protect
def login(request):

    if 'uid' not in request.session:
        if request.method == "POST":

            user_name = request.POST['username']
            password = request.POST['password']

            if user_name == '' or password == '':
                return render(request, 'home.html', {'error' : "Invalid Credentials. Please try again."})

            p = Userinfo.objects.raw(f"SELECT * FROM userinfo WHERE user_name = '{user_name}'")

            if not p:
                return render(request, 'home.html', {"error" : 'Incorrect Username/Password'})

            else:

                info = p[0]
                
                response = pbkdf2_sha256.verify(password, info.password)

                if not response:
                    return render(request, 'home.html', {"error" : 'Incorrect Username/Password'})

                else:

                    if info.role_type == 1:

                        uid=generateUSID()
                        request.session['uid'] = uid
                        request.session['user_name'] = user_name
                        request.session['password'] = password
                        request.session['role_type'] = info.role_type

                        #Token Insert to Database
                        sess = Security()
                        sess.user_name = request.session['user_name']
                        sess.auth_key = request.session['uid']
                        sess.role_type = request.session['role_type']
                        sess.save()

                        return redirect("menu")
                    else:

                        uid=generateUSID()
                        request.session['uid'] = uid
                        request.session['user_name'] = user_name
                        request.session['password'] = password
                        request.session['role_type'] = info.role_type

                        #Token Insert to Database
                        sess = Security()
                        sess.user_name = request.session['user_name']
                        sess.auth_key = request.session['uid']
                        sess.role_type = request.session['role_type']
                        sess.save() 

                        return redirect("search")

        return render(request, "home.html")
    
    else:

        users = Security.objects.raw(f"SELECT * FROM security WHERE auth_key = '{request.session['uid']}'")

        if not users:
            return HttpResponse("Unauthorized Access!!")

        else:

            for i in users:
                role_type = i.role_type

            if role_type == 1:
                return redirect('menu')
            else:
                 return redirect('search')

@secureRequestmenu
def menu(request):
    #return HttpResponse(request.COOKIES[settings.SESSION_COOKIE_NAME])
    return render(request, "menu.html", {"name" : request.session['user_name']})

@csrf_protect
@secureRequest
def search(request):

    error = None

    if request.method == "POST":

        url ='http://35.169.240.207/chatbot/api/v1/intents'
        response = requests.get(url, params=request.GET)
        val= response.json()
        searchElement = request.POST['search']

        if searchElement == '':
            return render(request, 'search.html', {"error" : error, "name" : request.session['user_name']})

        for i in val['response']['data']:

            if searchElement == '':
                return render(request, 'search.html', {"error" : error, "name" : request.session['user_name']})

            elif int(searchElement) == i['intent_id']:
                return render(request, 'search.html',{"search_element" : i, "name" : request.session['user_name']})

            else:
                error = "Element not Found"

    return render(request, "search.html", {"error" : error, "name" : request.session['user_name']})

@secureRequestmenu
def userInfo(request):

    users = Userinfo.objects.raw("SELECT * FROM userinfo ")

    list = []
    
    for i in users:
        obj={}
        obj['user_name']=i.user_name
        obj['password']=i.password

        if i.role_type == 1:
            obj['role']='Admin'
        elif i.role_type == 2:
            obj['role']='Live Agent'

        list.append(obj)
    return render(request, 'userinfo.html', {"list" : list, "name" : request.session['user_name']})

@csrf_protect
@secureRequestmenu
def adduser(request):

    error = None

    if request.method == 'POST':
        
        user_name = request.POST['username']
        password = request.POST['password']
        cnfpassword = request.POST['cnfpassword']
        role = request.POST['role']

        if user_name == '' or password == '' or cnfpassword == '':
            return render(request, 'adduser.html', {"error" : 'Invalid Credentials. Please try again.', "name" : request.session['user_name']})

        if password != cnfpassword:
            return render(request, 'adduser.html', {"error" : 'Confirm Password Not Matched', "name" : request.session['user_name']})

        users = Userinfo.objects.raw(f"SELECT * FROM userinfo WHERE user_name = '{user_name}'")

        if users:
            return render(request, 'adduser.html', {"error" : 'User Already Exist', "name" : request.session['user_name']})

        role_type = 0
        encrypassword = pbkdf2_sha256.hash(password)

        if role == 'l':
            role_type = 2
        elif role =='a':
            role_type = 1

        #Add User to Database
        user = Userinfo()
        user.user_name = user_name
        user.password = encrypassword
        user.role_type = role_type
        user.save()
        
        return redirect("menu")
    return render(request, 'adduser.html', {"error" : error, "name" : request.session['user_name']})

@csrf_protect
@secureRequestmenu
def uploadfile(request):

    if request.method == "POST":

        if not request.FILES:
            return render(request, 'uploadfile.html', {"error" :"Choose File", "name" : request.session['user_name']})

        file = request.FILES['filename']

        filename = file.name
        
        if len(file.name) == 0:
            return render(request, 'uploadfile.html', {"error" :"Choose File", "name" : request.session['user_name']})
        else:

            if file.name.endswith('.xlsx'):

                data_xls = pd.read_excel(file)

                for row_name in data_xls:

                    if row_name in ['Intents', 'Contexts', 'Questions', 'Answers']:
                        continue
                    else:
                        return render(request, 'uploadfile.html', {"error" : "Invalid Field in Excel", "name" : request.session['user_name']})

                intentStatic = ['General', 'Nutrition', 'Support', 'Subscription', 'Delivery']
                
                for intent in data_xls['Intents']:

                    if type(intent) != float:

                        if intent.strip() != '':

                            if intent in intentStatic:
                                continue
                            else:
                                return render(request, 'uploadfile.html', {"error" : "Invalid " + intent, "name" : request.session['user_name']})

                        else:
                            return render(request, 'uploadfile.html', {"error" : "Intent Field is Empty", "name" : request.session['user_name']})
                    else:
                        return render(request, 'uploadfile.html', {"error" : "Intent Field is Empty", "name" : request.session['user_name']})

                for context in data_xls['Contexts']:

                    if type(context) != float:

                        if context.strip() == '':
                            return render(request, 'uploadfile.html', {"error" : "Contexts Field is Empty ", "name" : request.session['user_name']})
                        else:
                            continue
                    else:
                        return render(request, 'uploadfile.html', {"error" : "Contexts Field is Empty ", "name" : request.session['user_name']})
                
                for answer in data_xls['Answers']:

                    if type(answer) != float:

                        if answer.strip() == '':
                            return render(request, 'uploadfile.html', {"error" : "Answers Field is Empty ", "name" : request.session['user_name']})
                        else:
                            continue
                    else:
                        return render(request, 'uploadfile.html', {"error" : "Answers Field is Empty ", "name" : request.session['user_name']})

                for question in data_xls['Questions']:

                    if type(question) != float:

                        if question.strip() == '':
                            return render(request, 'uploadfile.html', {"error" : "Questions Field is Empty ", "name" : request.session['user_name']})
                        else:
                            continue
                    else:
                        return render(request, 'uploadfile.html', {"error" : "Questions Field is Empty ", "name" : request.session['user_name']})

                questionList = data_xls['Questions'].tolist()

                tempQuestionList = []

                for i in questionList:
                    i = i.strip()
                    tempQuestionList.append(i.lower())

                duplicateValue = [item for item, count in collections.Counter(tempQuestionList).items() if count > 1]

                if len(duplicateValue) != 0:
                    return render(request, 'uploadfile.html', {"error" : "Duplicate Questions " + str(duplicateValue), "name" : request.session['user_name']})
                
                if not os.path.exists(os.path.join(os.path.dirname(__file__), "uploads/")):
                    os.makedirs(os.path.join(os.path.dirname(__file__), "uploads/"))

                path1 = os.path.join(os.path.dirname(__file__), "uploads/")

                completeName = os.path.join(path1, filename) 
                data_xls.to_excel(completeName, index=False)

                return redirect('menu')
            else:
                return render(request, 'uploadfile.html', {"error" : "Only .xlsx File Accepted", "name" : request.session['user_name']})

    return render(request, 'uploadfile.html', {"name" : request.session['user_name']})


@secureRequestmenu
def deleteuser(request, id):

    user_name = id

    #Delete User from Database
    user = Userinfo.objects.get(user_name = user_name)
    user.delete()

    return redirect("menu")

def logout(request):

    if 'uid' in request.session:
        request.session.clear()
        return redirect("login")
    else:
        return redirect("login")


