# from django.db import models
# from django.core.validators import RegexValidator
# from django.core.exceptions import ValidationError
# from django.core.validators import MinValueValidator, MaxValueValidator
# from django.conf import settings
# from django.contrib.auth.models import User

# class Subject(models.Model):
#     name_validator = RegexValidator(
#         regex=r'^[A-Z]{3}\d{4}$',
#         message="Subject code must be 3 uppercase letters followed by 4 digits. E.g., 'INF1343'."
#     )
#     code = models.CharField(
#         max_length=7,
#         unique=True,
#         validators=[name_validator],
#         primary_key=True,
#         default='XXX0000',
#     )
#     name = models.CharField(max_length=100)
#     #teachers = models.ManyToManyField('Teacher', null=True, blank=True)
#     average_stars = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=None, null=True, blank=True)

#     def __str__(self):
#         return self.name


# class Teacher(models.Model):
#     name = models.CharField(max_length=100)
#     email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
#     #disciplines = models.ManyToManyField(Subject, blank=True, null=True)
#     average_stars = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=None, null=True, blank=True)

#     def __str__(self):
#         return self.name



# class Feedback(models.Model):
#     subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
#     title = models.CharField(max_length=40)
#     body = models.TextField()
#     author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     teachers = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
#     participants = models.ManyToManyField(User, related_name='participants', blank=True) # we already have user, so we need a related name
#     created = models.DateTimeField(auto_now_add=True)
    
#     def validate_half_number(value):
#         if value * 2 % 1 != 0:
#             raise ValidationError('Value must be a whole number or a half number.')
        
#     stars = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5), validate_half_number], default=None, null=True, blank=True)
    
  
#     def __str__(self):
#         return self.body[:20]

# class Messages(models.Model):
#     message = models.TextField()
#     author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE)
#     created = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.message[:20]

#     def total_upvotes(self):
#         return self.votes.filter(vote_type='up').count()

#     def total_downvotes(self):
#         return self.votes.filter(vote_type='down').count()

#     def score(self):
#         return self.total_upvotes() - self.total_downvotes()

# class Vote(models.Model):
#     UPVOTE = 'up'
#     DOWNVOTE = 'down'
#     VOTE_TYPE_CHOICES = [
#         (UPVOTE, 'Upvote'),
#         (DOWNVOTE, 'Downvote'),
#     ]

#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     message = models.ForeignKey(Messages, related_name='votes', on_delete=models.CASCADE)
#     vote_type = models.CharField(max_length=4, choices=VOTE_TYPE_CHOICES)

#     class Meta:
#         unique_together = ('user', 'message')