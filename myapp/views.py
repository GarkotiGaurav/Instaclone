from django.shortcuts import render, redirect
from forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm
from models import UserModel, SessionToken, PostModel, LikeModel, CommentModel
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
from django.utils import timezone
from intrest.settings import BASE_DIR
#Library for sending emails using api.
import sendgrid
from sendgrid.helpers.mail import *
#Library for printin message box.
import ctypes
import datetime
#Library for rematching pass username etc.
import re
#Function for using clarifai api.
import clarifai
from clarifai.client import ClarifaiApi



from imgurpython import ImgurClient


ci = "601a283fd32edcf"
cs = "d9d2692a079a69f2b2f1a04dee7703fa61a30e62"
key= "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"
KEY = "dac538e2ff8640648ef8d78d0b51e5ce"




#Function Which make you to signup for the instaclone.
def signup_view(request):

    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']

            if not re.match("[a-zA-Z_.@]*$", username):
                if len(username) < 4:
                    ctypes.windll.user32.MessageBoxW(0, u"Kindly Enter valid details", u"Error", 0)
            name = form.cleaned_data['name']

            if not re.match("[a-zA-Z]*$", name):
                ctypes.windll.user32.MessageBoxW(0, u"Kindly Enter valid details", u"Error", 0)
            email = form.cleaned_data['email']

            if not re.match("[a-z0-9@.]*$", email):
                ctypes.windll.user32.MessageBoxW(0, u"Kindly Enter valid details", u"Error", 0)

            password = form.cleaned_data['password']
            if not re.match("[a-zA-Z@_]*$", password):
                if len(username) < 5:
                    ctypes.windll.user32.MessageBoxW(0, u"Kindly Enter valid details", u"Error", 0)

# saving data to DB
            user = UserModel(name=name, password=make_password(password), email=email, username=username)
            user.save()

            sg = sendgrid.SendGridAPIClient(apikey=key)
            from_email = Email("gauravgarkoti007@gmail.com")
            to_email = Email(email)
            subject = "Confiramation Mail"
            content = Content("text/plain", "to verify provided email address")
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            print(response.status_code)
            print(response.body)
            print(response.headers)
            # return redirect('login/')ctypes
            ctypes.windll.user32.MessageBoxW(0, u"Sucessufully signed up\n\nMail has been sent\n\nClick for log in ",u"congrulation", 0)

            return render(request, 'login.html')



    else:

        form = SignUpForm()
    return render(request, 'index.html', {'form': form})




#Function which make u login.
def login_view(request):
    response_data = {}

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')

            if not re.match("[a-zA-Z_.@]*$", username):
                #if len(username) < 4:
                    ctypes.windll.user32.MessageBoxW(0, u"Kindly Enter valid details", u"Error", 0)

            password = form.cleaned_data.get('password')
            #if not re.match("[a-zA-Z@_]*$", password):
                #if len(username) < 4:
                    #ctypes.windll.user32.MessageBoxW(0, u"Kindly Enter valid details", u"Error", 0)

            user = UserModel.objects.filter(username=username).first()

            if user:

                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    ctypes.windll.user32.MessageBoxW(0,u"Sucessufully "u"loged in\n\nMail has been sent\n\nClick for further process",u"congrulation", 0)
                    response = redirect('feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response

            else:
                ctypes.windll.user32.MessageBoxW(0,u"Invalid User",u"Error", 0)


    elif request.method == 'GET':
        form = LoginForm()

    response_data['form'] = form
    return render(request, 'login.html', response_data)




#Function which make you to post a post.
def post_view(request):
    user = check_validation(request)

    if user:

        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)

            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()
                ctypes.windll.user32.MessageBoxW(0,u"Post has been created.",u"congrulation", 0)

                path = str(BASE_DIR + post.image.url)

                client = ImgurClient(ci, cs)
                post.image_url = client.upload_from_path(path, anon=True)['link']
                post.save()
                return redirect('/feed/')
            else:
                ctypes.windll.user32.MessageBoxW(0, u"Invalid Post", u"Error", 0)
                form = PostForm()
            return render(request, 'post.html', {'form': form})

        else:
            return redirect('/login/')


"""
                app = ClarifaiApi(api_=KEY)
                model = app.models.get('logo')
                response = model.predict_by_url(url=post.image_url)
                if response["status"]["code"] == 10000:
                    if response["outputs"]:
                        if response["outputs"][0]["data"]:
                            if response["outputs"][0]["data"]["concepts"]:
                                for index in range(0, len(response["outputs"][0]["data"]["concepts"])):
                                    category = CategoryModel(post=post, category_text=response["outputs"][0]["data"]["concepts"][index]["name"])
                                    category.save()
                else:
                    ctypes.windll.user32.MessageBoxW(0, u"Invalid Post", u"Error", 0)"""









#Function which make you to redirect you to the newsfeed page.
def feed_view(request):
        user = check_validation(request)

        if user:

            posts = PostModel.objects.all().order_by('-created_on')

            for post in posts:
                existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
                if existing_like:
                    post.has_liked = True

            return render(request, 'feed.html', {'posts': posts})

        else:
            return redirect('/login/')





#This function will make u to like a post
def like_view(request):
        user = check_validation(request)

        if user and request.method == 'POST':
            form = LikeForm(request.POST)

            if form.is_valid():
                post_id = form.cleaned_data.get('post').id
                existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()

                if not existing_like:
                    like = LikeModel.objects.create(post_id=post_id, user=user)
                    sg = sendgrid.SendGridAPIClient(apikey=key)
                    from_email = Email("gaurav74175@gmail.com")
                    to_email = Email(like.post.user.email)
                    subject = "Confiramation Mail"
                    content = Content("text/plain", "to verify provided email address")
                    mail = Mail(from_email, subject, to_email, content)
                    response = sg.client.mail.send.post(request_body=mail.get())
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)

                else:
                    existing_like.delete()

                return redirect('/feed/')

        else:
            return redirect('/login/')



#This function will make you to comment on a post.
def comment_view(request):
        user = check_validation(request)

        if user and request.method == 'POST':
            form = CommentForm(request.POST)

            if form.is_valid():
                post_id = form.cleaned_data.get('post').id
                comment_text = form.cleaned_data.get('comment_text')
                comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
                comment.save()
                sg = sendgrid.SendGridAPIClient(apikey=key)
                from_email = Email("gauravgarkoti007@gmail.com")
                to_email = Email(comment.post.user.email)
                subject = "Knock Knock"
                content = Content("text/plain", "Hey! Someone just commented on your post.")
                mail = Mail(from_email, subject, to_email, content)
                response = sg.client.mail.send.post(request_body=mail.get())
                print(response.status_code)
                print(response.body)
                print(response.headers)

                return redirect('/feed/')

            else:
                return redirect('/feed/')

        else:
            return redirect('/login')





# For validating the session
def check_validation(request):

    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()

        if session:
            time_to_live = session.created_on + timedelta(days=1)

            if time_to_live > timezone.now():
                return session.user

    else:
        return None




#Function for make you logout.
def logout_view(request):
    request.session.modified = True

    response = redirect('/login/')
    response.delete_cookie(key='session_token')

    return response



