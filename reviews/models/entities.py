from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator


# PEP-257
class Subject(models.Model):
    """
    Model representing a school subject.

    Attributes:
        code (str): A unique identifier for the subject,
                    consisting of 3 uppercase letters followed by 4 digits.
        name (str): The name of the subject.
        average_stars (float):  The average rating of the
                                subject, between 1 and 5 stars.
    """

    name_validator = RegexValidator(
        regex=r'^[A-Z]{3}\d{4}$',
        message="Subject code must be 3 uppercase \
        letters followed by 4 digits. E.g., 'INF1343'."
    )
    code = models.CharField(
        max_length=7,
        unique=True,
        validators=[name_validator],
        primary_key=True,
        default='XXX0000',
    )
    name = models.CharField(max_length=100)
    average_stars = models.FloatField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=None,
        null=True,
        blank=True)

    def __str__(self):
        return str(self.name)


class Teacher(models.Model):
    """
    Model representing a teacher.

    Attributes:
        name (str): The name of the teacher.
        email (str): The email of the teacher.
        average_stars (float): The average rating of the teacher, between 1 and 5 stars.
    """
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True,
                              null=True, blank=True)
    average_stars = models.FloatField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=None,
        null=True,
        blank=True)

    def __str__(self):
        return str(self.name)
