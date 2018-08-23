#from django.forms import formset_factory, modelformset_factory
from django.shortcuts import render, Http404 
from django.utils import timezone
from django.db.models import Q
#from django.forms import inlineformset_factory
from .models import Post
from .forms import PostModelForm, CommentForm
from django.contrib.auth import login, get_user_model, logout
from django.shortcuts import render, redirect
#from django.forms import formset_factory, modelformset_factory
#from . models import Profile
#from django.forms.models import inlineformset_factory
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .models import MyUser
from django import template
from django.contrib.auth import login, get_user_model, logout
from .forms import UserCreationForm, UserLoginForm
from django.http import HttpResponseRedirect
#from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import TemplateView , ContextMixin, TemplateResponseMixin
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from. import models
from django.contrib.messages.views import SuccessMessageMixin


User = get_user_model()


def register(request, *args, **kwargs):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        print("user created ")
        return HttpResponseRedirect("/login")

    return render(request, "register.html", {"form":form})


def user_login(request, *args, **kwargs):

    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        user_obj = form.cleaned_data.get("user_obj")
        login(request, user_obj)
        print(user_obj.username)
        context = {
            "username" : user_obj.username
        }
        return redirect('blog:dashboard')
    return render(request, "login.html", {"form":form})


def dashboard(request):
    try:    
        if request.user.is_authenticated:
            qs = Post.objects.filter(user=request.user)
            obj = request.user.username
            query = request.GET.get("q", None)
            if query is not None:
                qs = qs.filter(
                        Q(title__icontains=query) |
                        Q(content__icontains=query) 
                    )
            context = {
                    "object_list":qs,
                    "object" : obj,
                }
        else:
            return redirect('/logout/')
    except :
        raise Http404("ERROR PAGE 404")

    return render(request, "dashboard.html", context)
  

def user_blogs(request):
    query = request.GET.get("q", None)

    qs = MyUser.objects.all()
    #print(qs.slug)
    if query is not None:
        qs = qs.filter(
                Q(username__icontains=query) 
            ) 
    context = {
            "qs" : qs
    }
    return render(request, 'user_blogs.html', context)


def list_view(request, username):
    #try:

    qs = Post.objects.filter(slug  = username) 
    print(qs) 
    #get_object_or_404(Post, name=username) 
    template = "list.html"
    context = {
        "object_list": qs,
        "user": username
    }
    print(qs)
    return render(request, template, context)
    # except:
    #     return Http404("page not found")

def blog_detail(request, blog_id):
    qs = get_object_or_404(Post, pk=blog_id) 
    print(qs) 
    template = "blog_detail.html"
    context = {
        "obj":qs
    }
    print(qs)
    return render(request, template, context)

def detail_view(request, user_id):
    obj = get_object_or_404(Post, id=user_id)
    template = "detail-view.html"
    context = {
        "object" : obj,
    }
    return render(request, template, context)


def post_model_delete_view(request, user_id):
    if request.user.is_authenticated:
        obj = get_object_or_404(Post, id=user_id)
        if request.method == "POST":
            obj.delete()
            messages.success(request, "Post Delete")
            return HttpResponseRedirect("/dashboard/")
        template = "blog_confirm_delete.html"
        context = {
            "object" : obj,
        }
    else:
        return redirect('/logout/')
    return render(request, template, context)


def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/login")

def index(request):
    return render(request, "index.html", {})


class BlogDeleteView(DeleteView):
    model = Post

    def get_success_url(self):
        return reverse("A1:list")


def post_model_create_view(request):

    if request.user.is_authenticated:
        form = PostModelForm(request.POST or None,request.user)
        context = {
            "form":form
        }
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            print(obj.title)
            obj.save()
            messages.success(request, "New blog created")
            context={
              "form":PostModelForm()
            }
            return HttpResponseRedirect("/dashboard")
        template = "create-view.html"

    else:
        return redirect('/logout/')
    
    return render(request, template, context)



def post_model_update_view(request, user_id):
    if request.user.is_authenticated:    
        obj = get_object_or_404(Post, id=user_id)
        form = PostModelForm(request.POST or None, instance=obj)
        context = {
            "form":form
            }
        if form.is_valid():
            obj = form.save(commit=False)
            print(obj.title)
            obj.save()
            messages.success(request, "Blog updated")
            context={
                "form":PostModelForm()#request.POST or None
            }
            return HttpResponseRedirect("/dashboard")

        template = "update-view.html"
    else:
        return redirect('/logout/')

    return render(request, template, context)



class BlogList(SuccessMessageMixin, ListView):
    model = Post


#Comments
def add_comment(request, blog_id):
    if request.user.is_authenticated:    
        post = get_object_or_404(Post, pk=blog_id)
        usr = get_object_or_404(MyUser, username=request.user.username)
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid:
                comment = form.save(commit=False)
                comment.post = post
                comment.user = usr
                comment.save()
                return redirect('blog:blog_detail', blog_id=post.id)
        else:
            form = CommentForm()

        return render(request, 'add_comment.html', {'form': form})                    

    else:
        return redirect('/logout/')    