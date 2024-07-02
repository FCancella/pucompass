from django import forms
from .models import Subject, Teacher, Feedback, Messages


class FeedbackForm(forms.ModelForm):
    """
    Form for creating and updating feedback.

    This form excludes the author and participants fields and makes the subject and teachers fields optional.
    """
    class Meta:
        model = Feedback
        exclude = ['author', 'participants']

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.fields['subject'].required = False
        self.fields['teachers'].required = False

    def clean(self):
        """
        Validates that at least one of subject or teachers is provided.

        Raises:
            forms.ValidationError: If neither subject nor teachers is provided.
        """
        cleaned_data = super().clean()
        subject = cleaned_data.get('subject')
        teachers = cleaned_data.get('teachers')

        # Check if both subject and teachers are not provided
        if not subject and not teachers:
            raise forms.ValidationError('At least one of Subject or Teachers is required.')

        return cleaned_data


class ForumFeedbackForm(forms.ModelForm):
    """
    Form for creating feedback in a forum context.

    This form includes only the title and body fields.
    """
    class Meta:
        model = Feedback
        fields = ['title', 'body']
        exclude = ['author', 'subject', 'teachers', 'stars']


class SubjectForm(forms.ModelForm):
    """
    Form for creating and updating a subject.

    This form includes all fields except average_stars.
    """
    class Meta:
        model = Subject
        fields = '__all__'
        exclude = ['average_stars']


class TeacherForm(forms.ModelForm):
    """
    Form for creating and updating a teacher.

    This form includes all fields except average_stars.
    """
    class Meta:
        model = Teacher
        fields = '__all__'
        exclude = ['average_stars']


class MessageForm(forms.ModelForm):
    """
    Form for creating and updating a message.

    This form includes all fields except author and feedback.
    """
    class Meta:
        model = Messages
        fields = '__all__'  # include all fields in the form
        exclude = ['author', 'feedback']
