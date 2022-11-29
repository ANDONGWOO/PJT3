from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from .forms import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
import json
from django.http import JsonResponse

# 깃로그인
import os
from dotenv import load_dotenv
import requests
from .exception import *
from .models import *
from django.contrib import messages
from django.core.files.base import ContentFile
from django.db.models import *


# Create your views here.
def signup(request):
    # 이미 로그인 → 회원가입 X
    if request.user.is_authenticated:
        return redirect("articles:index")

    if request.method == "POST":
        signup_form = CustomUserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)

        if signup_form.is_valid() and profile_form.is_valid():
            user = signup_form.save()

            profile = profile_form.save(commit=False)
            Profile.objects.create(user=user, nickname=profile.nickname, github_id=profile.github_id, boj_id=profile.boj_id)

            # 현재 날짜를 기준으로 닉네임 자동 생성
            # nickname = str(user.pk) + str(user.date_joined.strftime("%f"))
            # Profile.objects.create(user=user, nickname=nickname)
            Guestbook.objects.create(user=user) # 방명록 생성
            return redirect("articles:index")
    else:
        signup_form = CustomUserCreationForm()
        profile_form = ProfileForm()

    context = {
        "signup_form": signup_form,
        "profile_form": profile_form,
    }

    return render(request, "accounts/signup.html", context)

# 유효한 ID(username)인지 검사
def is_valid_id(request):
    username = json.loads(request.body).get('username')
    # print(username)
    if  len(username) > 0:
        if get_user_model().objects.filter(username=username).exists() :
            is_valid = False
        else:
            is_valid = True

        data = {
            'is_valid': is_valid,
        }

        return JsonResponse(data)
    is_valid = 'null'
    data = {
        'is_valid': is_valid,
    }

    return JsonResponse(data)


def login(request):

    status = 1
    # 이미 로그인 → 로그인 X
    if request.user.is_authenticated:
        return redirect('articles:index')

    if request.method == 'POST':
        
        login_form = AuthenticationForm(request, data=request.POST)
        if login_form.is_valid():
            auth_login(request, login_form.get_user())
            return redirect(request.GET.get('next') or 'articles:index')
        else:
            status = 0
            login_form = AuthenticationForm()
            context = {
                'status':status,
                'login_form': login_form,
            }

            return render(request, 'accounts/login.html', context)


    else:
        login_form = AuthenticationForm()

    context = {
        'status':status,
        'login_form': login_form,
    }

    return render(request, 'accounts/login.html', context)


def logout(request):
    auth_logout(request)
    return redirect("articles:index")


def profile(request, user_pk):
    user = get_object_or_404(get_user_model(), pk=user_pk)

    context = {
        "user": user,
    }

    return render(request, "accounts/profile.html", context)


# 회원 정보 수정
@login_required
def profile_update(request, user_pk):
    if request.user.pk != user_pk:
        return redirect("accounts:profile", user_pk)

    user = get_object_or_404(get_user_model(), pk=user_pk)

    if request.method == "POST":
        profile_form = ProfileForm(request.POST, request.FILES, instance=user.profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect("accounts:profile", user_pk)
    else:
        profile_form = ProfileForm(instance=user.profile)

    context = {
        "user": user,
        "profile_form": profile_form,
    }

    return render(request, "accounts/profile_update.html", context)


# 깃 로그인용
load_dotenv()
GITHUB_CLIENT_ID = os.getenv("GIT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GIT_CLIENT_SECRET")

# git 로그인 클릭시 git으로 정보를 보냄
def github_login(request):
    client_id = GITHUB_CLIENT_ID
    redirect_uri = "http://127.0.0.1:8000/accounts/login/github/callback/"
    scope = "read:user"
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"
    )

# git에서 로그인 유저 정보 
def github_login_callback(request):
    if request.user.is_authenticated:
        raise SocialLoginException("User already logged in")
        
    code = request.GET.get("code", None)
    if code is None:
        raise GithubException("Can't get code")

    client_id = GITHUB_CLIENT_ID
    client_secret = GITHUB_CLIENT_SECRET

    token_request = requests.post(
        f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
        headers={"Accept": "application/json"},
    )
    token_json = token_request.json()
    print(token_json)
    error = token_json.get("error", None)

    if error is not None:
        raise GithubException("Can't get access token")

    access_token = token_json.get("access_token")

    profile_request = requests.get(
        "https://api.github.com/user",
        headers={
            "Authorization": f"token {access_token}",
            "Accept": "application/json",
        },
    )
    print(profile_request)

    profile_json = profile_request.json()

    # username = profile_json.get("login", None)
    # avatar_url = profile_json.get("avatar_url", None)
    # name = profile_json.get("name", None)
    # email = profile_json.get("email", None)
    # print(f"{username}, {avatar_url}, {name}, {email}")
    # 여기까지 확인

    service_name = "github"
    profile_json = profile_request.json()

    login_data = {
        "github": {
            "social_id": profile_json["id"],
            "username": profile_json["login"],
            "social_profile_picture": profile_json["avatar_url"],
            "nickname": profile_json["bio"],
            "email": profile_json["email"],
            ### 깃허브에서만 가져오는 항목 ###
            "git_id": profile_json["login"],
            ### 깃허브에서만 가져오는 항목 ###
        },
    }

    # DB에 깃허브 정보 저장
    user_info = login_data[service_name]

    print(user_info["social_id"])   # 62585191
    print(user_info["username"])    # jupiter6676

    # 이미 연동된 유저는 로그인
    if get_user_model().objects.filter(social_id=user_info["social_id"]).exists():
        user = get_user_model().objects.get(social_id=user_info["social_id"])
        auth_login(request, user)
        return redirect(request.GET.get("next") or "reviews:index")
    # 연동이 처음이면 회원가입 (DB에 저장)
    else:
        data = {
            # 일반 정보
            "name": (profile_json["name"]),
            "username": (profile_json["login"]),
            "git_id": (profile_json["login"]),
        }

        signup_form = CustomUserCreationForm(initial=data)
        context = {
            "signup_form": signup_form,
        }
        return render(request, "accounts/signup.html", context)

# 유저 팔로우/언팔로우
def follow(request, user_pk):
    if not request.user.is_authenticated:
        return redirect('accounts:profile', user.pk)
    
    user = get_object_or_404(get_user_model(), pk=user_pk)
    
    # 나와 다른 유저만 (언)팔로우 가능
    if request.user != user and request.method == 'POST':
        if user.followers.filter(pk=request.user.pk).exists():
            user.followers.remove(request.user)
            is_following = False    # 팔로잉 취소
        else:
            user.followers.add(request.user)
            is_following = True    # 팔로잉

    data = {
        'is_following': is_following,
        'followers_count': user.followers.count(),
    }

    return JsonResponse(data)


# 방명록
def guestbook(request, user_pk):
    user = get_object_or_404(get_user_model(), pk=user_pk)
    gb_articles = user.guestbook.guestbookarticle_set.all().order_by("-pk")
    gb_comments = user.guestbook.guestbookcomment_set.all()

    context = {
        'user': user,
        'gb_articles': gb_articles,
        'gb_comments': gb_comments,
    }

    return render(request, 'accounts/guestbook.html', context)


# 방명록 글 작성
@login_required
def gb_article_create(request, user_pk):
    # if 'gb_article_create' in request.POST:
    if request.method == 'POST':
        gb_article_form = GuestbookArticleForm(request.POST)
        guestbook = get_object_or_404(Guestbook, user_id=user_pk)
        
        if gb_article_form.is_valid():
            gb_article = gb_article_form.save(commit=False)
            gb_article.guestbook = guestbook
            gb_article.user = request.user
            gb_article.save()

        data = {
            'article_pk': gb_article.pk,
            'article_user': gb_article.user.profile.nickname,   # username?
            'article_content': gb_article.content,
            'article_created_at': gb_article.created_at.strftime('%Y.%m.%d'),
        }

        return JsonResponse(data)


# 방명록 글 삭제
@login_required
def gb_article_delete(request, user_pk, gb_article_pk):
    gb_article = get_object_or_404(GuestbookArticle, pk=gb_article_pk)

    is_deleted = False

    if request.user == gb_article.user and request.method == 'POST':
        gb_article.delete()
        # has_comment = True/False
        is_deleted = True

    data = {
        'is_deleted': is_deleted,
    }

    return JsonResponse(data)


# 방명록 댓글 생성
@login_required
def gb_comment_create(request, user_pk, gb_article_pk):
    if request.method == 'POST':
        gb_comment_form = GuestbookCommentForm(request.POST)
        article = get_object_or_404(GuestbookArticle, pk=gb_article_pk)
        guestbook = get_object_or_404(Guestbook, user_id=user_pk)
        
        if gb_comment_form.is_valid():
            comment = gb_comment_form.save(commit=False)
            comment.guestbook = guestbook
            comment.article = article
            comment.user = request.user
            comment.save()

        data = {
            'comment_pk': comment.pk,
            'comment_user': comment.user.profile.nickname,   # username?
            'comment_content': comment.content,
            'comment_created_at': comment.created_at.strftime('%Y.%m.%d'),
        }

        return JsonResponse(data)

    return redirect('accounts:guestbook', user_pk)


# 방명록 댓글 삭제
@login_required
def gb_comment_delete(request, user_pk, gb_article_pk, gb_comment_pk):
    gb_comment = get_object_or_404(GuestbookComment, pk=gb_comment_pk)

    is_deleted = False

    if request.user == gb_comment.user and request.method == 'POST':
        gb_comment.delete()
        is_deleted = True

    data = {
        'is_deleted': is_deleted,
    }

    return JsonResponse(data)
