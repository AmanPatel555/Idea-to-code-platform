from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import JoinRequest
from django.shortcuts import get_object_or_404


def home(request):
    return render(request, 'home.html')


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, "Login successful")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('home')

from .models import Project
from django.contrib.auth.decorators import login_required


@login_required
def create_project(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        tech_stack = request.POST.get("tech_stack")

        project = Project.objects.create(
            title=title,
            description=description,
            tech_stack=tech_stack,
            creator=request.user
        )

        project.members.add(request.user)

        messages.success(request, "Project created successfully!")
        return redirect('project_detail', pk=project.id)

    return render(request, "create_project.html")


def project_list(request):
    projects = Project.objects.all().order_by("-created_at")
    return render(request, "projects.html", {"projects": projects})


from django.shortcuts import get_object_or_404
from django.contrib import messages

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, id=pk)

    join_request = None
    if request.user != project.creator and request.user not in project.members.all():
        join_request = project.join_requests.filter(user=request.user).first()

    tech_list = []

    if project.tech_stack:
        tech_list = [tech.strip() for tech in project.tech_stack.split(",")]

    context = {
        "project": project,
        "join_request": join_request,
        "tech_list": tech_list,
    }

    return render(request, "project_detail.html", context)


@login_required
def request_join(request, pk):
    project = Project.objects.get(id=pk)

    if request.user == project.creator:
        messages.error(request, "You are the creator of this project.")
        return redirect('project_detail', pk=pk)

    if JoinRequest.objects.filter(user=request.user, project=project).exists():
        messages.warning(request, "You have already requested to join.")
        return redirect('project_detail', pk=pk)

    JoinRequest.objects.create(
        user=request.user,
        project=project,
        status='pending'
    )

    messages.success(request, "Join request sent successfully!")
    return redirect('project_detail', pk=pk)


@login_required
def approve_request(request, pk):
    join_request = get_object_or_404(JoinRequest, id=pk)

    if request.user != join_request.project.creator:
        messages.error(request, "Not authorized")
        return redirect('project_detail', pk=join_request.project.id)

    join_request.status = "approved"
    join_request.save()

    messages.success(request, "Request approved!")
    return redirect('project_detail', pk=join_request.project.id)


@login_required
def reject_request(request, pk):
    join_request = get_object_or_404(JoinRequest, id=pk)

    if request.user != join_request.project.creator:
        messages.error(request, "Not authorized")
        return redirect('project_detail', pk=join_request.project.id)

    join_request.status = "rejected"
    join_request.save()

    messages.warning(request, "Request rejected.")
    return redirect('project_detail', pk=join_request.project.id)

@login_required
def dashboard(request):
    created_projects = request.user.created_projects.all()
    joined_projects = request.user.joined_projects.all()
    pending_requests = JoinRequest.objects.filter(user=request.user, status='pending')

    context = {
        "created_projects": created_projects,
        "joined_projects": joined_projects,
        "pending_requests": pending_requests,
    }

    return render(request, "dashboard.html", context)

@login_required
def profile_view(request):
    profile = request.user.profile
    created_projects = request.user.created_projects.all()
    joined_projects = request.user.joined_projects.all()

    context = {
        "profile": profile,
        "created_projects": created_projects,
        "joined_projects": joined_projects,
    }

    return render(request, "profile.html", context)

@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        profile.skills = request.POST.get("skills")
        profile.github_link = request.POST.get("github_link")
        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return render(request, "edit_profile.html", {"profile": profile})