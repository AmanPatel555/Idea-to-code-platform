from django.contrib import admin
from .models import Profile, Project, JoinRequest

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "github_link", "skills")

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "created_at")
    search_fields = ("title", "creator__username")

@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "project", "status", "created_at")
    list_filter = ("status",)