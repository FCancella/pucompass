from django.core.exceptions import ValidationError
from django.test import TestCase
from reviews.models import Subject, Teacher

class SubjectModelTests(TestCase):
    def test_create_valid_subject(self):
        subject = Subject.objects.create(code='INF1343', name='Informatics', average_stars=4.5)
        self.assertEqual(subject.code, 'INF1343')
        self.assertEqual(subject.name, 'Informatics')
        self.assertEqual(subject.average_stars, 4.5)
    
    def test_create_subject_invalid_code(self):
        with self.assertRaises(ValidationError):
            subject = Subject(code='invalid', name='Informatics')
            subject.full_clean()  # This method will call the validators and raise ValidationError
    
    def test_create_subject_code_uniqueness(self):
        Subject.objects.create(code='INF1343', name='Informatics', average_stars=4.5)
        with self.assertRaises(ValidationError):
            duplicate_subject = Subject(code='INF1343', name='Advanced Informatics')
            duplicate_subject.full_clean()
    
    def test_create_subject_invalid_average_stars(self):
        with self.assertRaises(ValidationError):
            subject = Subject(code='INF1343', name='Informatics', average_stars=6)
            subject.full_clean()
        
        with self.assertRaises(ValidationError):
            subject = Subject(code='INF1343', name='Informatics', average_stars=0)
            subject.full_clean()

class TeacherModelTests(TestCase):
    def test_create_valid_teacher(self):
        teacher = Teacher.objects.create(name='John Doe', email='john.doe@example.com', average_stars=4.2)
        self.assertEqual(teacher.name, 'John Doe')
        self.assertEqual(teacher.email, 'john.doe@example.com')
        self.assertEqual(teacher.average_stars, 4.2)
    
    def test_create_teacher_invalid_email(self):
        teacher = Teacher(name='John Doe', email='invalid-email')
        with self.assertRaises(ValidationError):
            teacher.full_clean()
    
    def test_create_teacher_email_uniqueness(self):
        Teacher.objects.create(name='John Doe', email='john.doe@example.com', average_stars=4.2)
        with self.assertRaises(ValidationError):
            duplicate_teacher = Teacher(name='Jane Smith', email='john.doe@example.com')
            duplicate_teacher.full_clean()
    
    def test_create_teacher_invalid_average_stars(self):
        with self.assertRaises(ValidationError):
            teacher = Teacher(name='John Doe', email='john.doe@example.com', average_stars=6)
            teacher.full_clean()
        
        with self.assertRaises(ValidationError):
            teacher = Teacher(name='John Doe', email='john.doe@example.com', average_stars=0)
            teacher.full_clean()
