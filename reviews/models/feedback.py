from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from .entities import Subject, Teacher


class Feedback(models.Model):
    """
    Model representing feedback for a subject or teacher.

    Attributes:
        subject (Subject): The subject related to the feedback.
        title (str): The title of the feedback.
        body (str): The body of the feedback.
        author (User): The author of the feedback.
        teachers (Teacher): The teacher related to the feedback.
        participants (ManyToManyField): Users who participated in the feedback.
        created (datetime): The date and time when the feedback was created.
        stars (float): The star rating for the feedback, between 1 and 5, allowing half numbers.
    """
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=40)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    teachers = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def validate_half_number(self):
        """
        Validator to check if the value is a whole number or a half number.

        Args:
            self (float): The value to validate.

        Raises:
            ValidationError: If the value is not a whole or half number.
        """

        if self * 2 % 1 != 0:
            raise ValidationError('Value must be a whole number or a half number.')

    stars = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5), validate_half_number],
                              default=None, null=True, blank=True)

    def __str__(self):
        return self.body[:20]


class Messages(models.Model):
    """
    Model representing a message within feedback.

    Attributes:
        message (str): The content of the message.
        author (User): The author of the message.
        feedback (Feedback): The feedback related to the message.
        created (datetime): The date and time when the message was created.
    """
    message = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message[:20]

    def total_upvotes(self):
        return self.votes.filter(vote_type='up').count()

    def total_downvotes(self):
        return self.votes.filter(vote_type='down').count()

    def score(self):
        return self.total_upvotes() - self.total_downvotes()


class Vote(models.Model):
    """
    Model representing a vote for a message.

    Attributes:
        user (User): The user who cast the vote.
        message (Message): The message that was voted on.
        vote_type (str): The type of vote, either 'up' or 'down'.
    """
    UPVOTE = 'up'
    DOWNVOTE = 'down'
    VOTE_TYPE_CHOICES = [
        (UPVOTE, 'Upvote'),
        (DOWNVOTE, 'Downvote'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Messages, related_name='votes', on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=4, choices=VOTE_TYPE_CHOICES)

    class Meta:
        unique_together = ('user', 'message')
