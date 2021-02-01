from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
from .models import Post
from .forms import PostForm
from .filters import PostFilter
def home(request):
	posts = Post.objects.filter(active =True,featured=True)[0:3]
	context={'posts':posts}
	return render(request,'base/index.html',context)

def posts(request):

	posts = Post.objects.filter(active =True)
	myFilter=PostFilter(request.GET,queryset=posts)
	posts=myFilter.qs

	page= request.GET.get('page')
	paginator=Paginator(posts,5)
	try:
			posts=paginator.page(page)

	except PageNotAnInteger:
			posts=paginator.page(1)
	except EmptyPage:
			posts=paginator.page(paginator.num_pages)

	context={'posts':posts,'myFilter':myFilter}
	return render(request,'base/posts.html',context)

def post(request,slug):
	post=Post.objects.get(slug=slug)
	context={'post':post}
	return render(request,'base/post.html',context)

def profile(request):
	return HttpResponse(request,'base/profile.html')

@login_required(login_url= "login")
def createPost(request,):
	
	form=PostForm()
	if request.method =='POST':
		form =PostForm(request.POST,request.FILES)
		if form.is_valid():
			form.save()
		return redirect('posts')
	context={'form':form}
	return render(request,'base/post_form.html',context)

@login_required(login_url= "login")
def updatePost(request,slug):
	post=Post.objects.get(slug=slug)
	form=PostForm(instance=post)
	if request.method =='POST':
		form =PostForm(request.POST,request.FILES,instance=post)
		if form.is_valid():
			form.save()
		return redirect('posts')
	context={'form':form}
	return render(request,'base/post_form.html',context)

@login_required(login_url= "login")
def deletePost(request,slug):
	post=Post.objects.get(slug=slug)
	if request.method =='POST':
		post.delete()
		return redirect('posts')
	
	context={'item':post}
	return render(request,'base/delete.html',context)
def loginPage(request):
	if request.user.is_authenticated:
		return redirect('home')
	

	if request.method == 'POST':
		email = request.POST.get('email')
		password =request.POST.get('password')

		#Little Hack to work around re-building the usermodel
		try:
			user = User.objects.get(email=email)
			user= authenticate(request, username=user.username, password=password)
		

		except:
			messages.error(request, 'User with this email does not exists')
			return redirect('login')
		next_url = request.GET.get('next')
		if next_url == '' or next_url == None:
			next_url = 'home'
				
		if user is not None:
			login(request, user)
			return redirect(next_url)
		else:
			messages.error(request, 'Email OR password is incorrect')

	context = {}
	return render(request, 'base/login.html', context)
def logoutUser(request):
	logout(request)
	return redirect('home')
def sendEmail(request):
	if request.method =='POST':

		template = render_to_string('base/email_template.html',{
					'name':request.POST['name'],
					'email':request.POST['email'],
					'message':request.POST['message'],

			})
		email=EmailMessage(
			request.POST['subject'],
			template,
			settings.EMAIL_HOST_USER,
			['sauravcse15@gmail.com']
			)
		email.fail_silently=False 
		email.send()
	return render(request,'base/email_sent.html')