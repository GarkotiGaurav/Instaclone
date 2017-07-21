from django.shortcuts import render, redirect
from forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm
from models import UserModel, SessionToken, PostModel, LikeModel, CommentModel
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
from django.utils import timezone
from intrest.settings import BASE_DIR
import sendgrid
from sendgrid.helpers.mail import *
import ctypes
import datetime
import re



from imgurpython import ImgurClient


ci = "601a283fd32edcf"
cs = "d9d2692a079a69f2b2f1a04dee7703fa61a30e62"
key="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"





def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if not re.match("[a-zA-Z]*$", username):
                ctypes.windll.user32.MessageBoxW(0, u"Kindly Enter valid details", u"Error", 0)
            name = form.cleaned_data['name']
            if not re.match("[a-zA-Z]*$", name):
                ctypes.windll.user32.MessageBoxW(0, u"Kindly Enter valid details", u"Error", 0)
            email = form.cleaned_data['email']
            if not re.match("[a-z0-9@.]*$", email):
                ctypes.windll.user32.MessageBoxW(0, u"Kindly Enter valid details", u"Error", 0)
            password = form.cleaned_data['password']
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





def login_view(request):
    response_data = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            if not re.match("[a-zA-Z]*$", username):
                ctypes.windll.user32.MessageBoxW(0, u"Kindly Enter valid details", u"Error", 0)
            password = form.cleaned_data.get('password')
            user = UserModel.objects.filter(username=username).first()

            if user:
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    ctypes.windll.user32.MessageBoxW(0,u"Sucessufully "u"loged in\nMail has been sent\nClick for further process",u"congrulation", 0)
                    response = redirect('feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
            else:
                ctypes.windll.user32.MessageBoxW(0,u"Invalid User",u"Error", 0)


    elif request.method == 'GET':
        form = LoginForm()

    response_data['form'] = form
    return render(request, 'login.html', response_data)





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






def like_view(request):
        user = check_validation(request)
        if user and request.method == 'POST':
            form = LikeForm(request.POST)
            if form.is_valid():
                post_id = form.cleaned_data.get('post').id
                existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
                if not existing_like:
                    LikeModel.objects.create(post_id=post_id, user=user)

                else:
                    existing_like.delete()
                    sg = sendgrid.SendGridAPIClient(apikey=key)
                    from_email = Email("gaurav74175@gmail.com")
                    to_email = Email.get(user)
                    subject = "Confiramation Mail"
                    content = Content("text/plain", "to verify provided email address")
                    mail = Mail(from_email, subject, to_email, content)
                    response = sg.client.mail.send.post(request_body=mail.get())
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)

                return redirect('/feed/')

        else:
            return redirect('/login/')




def comment_view(request):
        user = check_validation(request)
        if user and request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                post_id = form.cleaned_data.get('post').id
                comment_text = form.cleaned_data.get('comment_text')
                comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
                comment.save()
                subject = "Comment!"
                message = "You have a comment on your post!"
                from_email = settings.EMAIL_HOST_USER
                to_list = [comment.user.email,settings.EMAIL_HOST_USER]
                send_mail(subject,message,from_email,to_list,fail_silently=True)
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



