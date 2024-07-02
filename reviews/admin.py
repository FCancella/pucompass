# reviews/admin.py

from django.contrib import admin
from .models import Subject, Feedback, Messages, Teacher

admin.site.register(Subject)
admin.site.register(Feedback)
admin.site.register(Messages)
admin.site.register(Teacher)