from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from urllib3 import request
from core.settings import EMAIL_HOST_USER
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.dateparse import parse_datetime
from django.forms.models import model_to_dict
from django.utils.timezone import make_aware
from django.core.mail import send_mail
from django.utils.text import slugify
from django.core import serializers
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from urllib.parse import unquote
from django.db.models import Sum
from django.urls import reverse
from datetime import timedelta
from datetime import datetime

from .models import *
import random
import stripe
import json
import re


def generate_verification_code(length=8):
    """Generate a random 4-digit numeric code"""
    return str(random.randint(1000, 9999))

# Create your views here.
def dashboard(request):    
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        due_date = request.POST.get("due_date")
        status = request.POST.get("status")
        priority = request.POST.get("priority")
        category = request.POST.get("category")
        image = request.FILES.get("image")

        # Only require title, other fields can be optional based on your model
        if not title:
            return JsonResponse({"success": False, "message": "Title is required."})
        
        # Create the task with available data
        task = Task(
            title=title,
            description=description,
            status=status or 'Pending',
            priority=priority or 'Medium',
            category=category or 'Other',
        )
        
        # Set optional fields if provided
        if due_date:
            task.due_date = due_date
        if image:
            task.image = image
            
        task.save()

        # Prepare task data for response
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description or "",
            "due_date": task.due_date.strftime("%Y-%m-%d") if task.due_date else "",
            "status": task.status,
            "priority": task.priority,
            "category": task.category,
            "created_at": task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": task.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "image_url": task.image.url if task.image else ""
        }

        return JsonResponse({
            "success": True, 
            "message": "Task added successfully.", 
            "task": task_dict
        })
    
    tasks = Task.objects.all().order_by('-created_at')
    return render(request, "dashboard.html", {'tasks': tasks})
