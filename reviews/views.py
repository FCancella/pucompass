from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models.entities import Subject, Teacher
from .models.feedback import Feedback, Vote, Messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from .forms import FeedbackForm, SubjectForm, TeacherForm, MessageForm, ForumFeedbackForm


def home(request):
    """
    Renders the home page of the application with filtered search results.

    This function handles GET requests to the home page. It processes an
    optional search query parameter 'q' and uses it to filter various
    database models: Feedback, Subject, Teacher, and Messages. The filtered
    results are then passed to the context and rendered in the 'reviews/home.html'
    template.

    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        HttpResponse: Rendered home page with context data.
    """

    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    feedbacks = Feedback.objects.filter(
        Q(title__icontains=q) |
        Q(teachers__name__icontains=q) |
        Q(subject__name__icontains=q) |
        Q(body__icontains=q)
    )
    context = {
        'subjects': Subject.objects.filter(name__icontains=q),
        'teachers': Teacher.objects.filter(name__icontains=q),
        'feedbacks': feedbacks,
        'messages': Messages.objects.filter(feedback__title__icontains=q)
    }
    return render(request, 'reviews/home.html', context)


def feedback(request, pk):
    """
    Renders the feedback page for a specific feedback object.

    This function handles requests for a feedback object identified by its
    primary key (pk). For GET requests, it fetches the feedback, associated
    messages, and participants, and renders them in the template. For POST
    requests, it handles the creation of new messages and updates the
    participants of the feedback.

    Args:
        request: HttpRequest object containing metadata about the request.
        pk: int, primary key of the Feedback object.

    Returns:
        HttpResponse: Rendered feedback page with context data or a redirect
        to the same page after processing a POST request.
    """

    feedback = get_object_or_404(Feedback, id=pk)
    feedback_messages = feedback.messages_set.all()
    participants = feedback.participants.all()

    if request.method == 'POST':
        message_content = request.POST.get('message')
        if not message_content:
            return HttpResponse("Message cannot be empty", status=400)
        Messages.objects.create(
            author=request.user,
            feedback=feedback,
            message=message_content,
        )
        feedback.participants.add(request.user)
        return redirect('feedback', pk=feedback.id)

    context = {
        'feedback': feedback,
        'feedback_messages': feedback_messages,
        'participants': participants,
    }
    return render(request, 'reviews/forum_form.html', context)


# Login, Logout and Register
def loginPage(request):
    """
    Handles user login functionality.

    This function manages the login process for users. If the user is
    already authenticated, they are redirected to the home page. For POST
    requests, it attempts to authenticate the user with the provided username
    and password. If successful, the user is logged in and redirected to the
    home page. If not, an error message is displayed.

    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        HttpResponse: Rendered login page with context data or a redirect to
        the home page.
    """
    page = 'login'
    if request.user.is_authenticated:  # if tries to login being logged in
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User does not exist")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or password does not exist")

    context = {'page': page}
    return render(request, 'reviews/login_register.html', context)


def logoutUser(request):
    """
    Handles user logout functionality. Redirects the user to the home page
    after logging out.
    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        HttpResponse: Redirect to the home page.
    """

    logout(request)
    return redirect('home')


def registerPage(request):
    """
    Handles user registration functionality. If the form is valid, the user is
    registered and logged in.
    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        HttpResponse: Rendered registration page with context data or a
        redirect to the home page.
    """

    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'reviews/login_register.html', {'form': form})


def chooseRoom(request):
    """
    Renders the room selection page.
    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        HttpResponse: Rendered room selection page.
    """
    return render(request, 'reviews/choices.html')


# Wrapper
@login_required(login_url='login')
def createFeedback(request):
    """
    Handles the creation of feedback messages.

    This function is responsible for displaying a form to create new feedback
    messages. It requires the user to be logged in. For POST requests, it
    processes the form data to create a new feedback entry. If the form is
    valid, the feedback is saved and the user is redirected to the home page.
    For GET requests, it displays an empty form.

    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        HttpResponse: Rendered feedback form page with context data or a
        redirect to the home page.
    """
    if request.method == 'POST':
        form = FeedbackForm(request.POST)

        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.author = request.user
            feedback.save()
            return redirect('home')
    else:
        form = FeedbackForm()

    context = {'form': form}
    return render(request, 'reviews/feedback_form.html', context)


def createForumFeedback(request):
    """
    Handles the creation of forum feedback messages.

    This function is responsible for displaying a form to create new forum
    feedback messages. It processes the form data submitted via POST requests
    to create a new forum feedback entry. If the form is valid, the feedback
    is saved, and the user is redirected to the home page. For GET requests,
    it displays an empty form.

    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        HttpResponse: Rendered forum feedback form page with context data or
        a redirect to the home page.
    """
    if request.method == 'POST':
        form = ForumFeedbackForm(request.POST)

        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.author = request.user
            feedback.save()
            return redirect('home')
    else:
        form = ForumFeedbackForm()

    context = {'form': form}
    return render(request, 'reviews/feedback_forum_form.html', context)


@login_required(login_url='login')
def deleteMessage(request, pk):
    """
    Handles the deletion of a message.

    This function allows users to delete their own messages or allows staff
    members to delete any message. If the user is not the author of the
    message and not a staff member, an error message is returned. For POST
    requests, it deletes the message and checks if the user has any remaining
    messages for the feedback. If no messages remain, the user is removed from
    the feedback participants. The user is then redirected to the feedback
    page. For GET requests, it renders a confirmation page.

    Args:
        request: HttpRequest object containing metadata about the request.
        pk: int, primary key of the Messages object to be deleted.

    Returns:
        HttpResponse: Rendered confirmation page or a redirect to the feedback
        page.
    """
    message = get_object_or_404(Messages, id=pk)
    feedback = message.feedback

    if request.user != message.author and not request.user.is_staff:
        return HttpResponse('You are not allowed to delete this message')

    if request.method == 'POST':
        message.delete()
        remaining_messages = Messages.objects.filter(feedback=feedback,
                                                     author=request.user).exists()
        if not remaining_messages:
            feedback.participants.remove(request.user)
        return redirect('feedback', pk=feedback.id)

    return render(request, 'reviews/delete.html', {'obj': message})


@login_required(login_url='login')
def deleteFeedback(request, pk):
    """
    Handles the deletion of a feedback message.

    This function allows users to delete their own feedback messages or
    allows staff members to delete any feedback message. If the user is not
    the author of the feedback and not a staff member, an error message is
    returned. For POST requests, it deletes the feedback message and redirects
    the user to the home page. For GET requests, it renders a confirmation
    page.

    Args:
        request: HttpRequest object containing metadata about the request.
        pk: int, primary key of the Feedback object to be deleted.

    Returns:
        HttpResponse: Rendered confirmation page or a redirect to the home
        page.
    """
    feedback = get_object_or_404(Feedback, id=pk)

    if request.user != feedback.author and not request.user.is_staff:
        return HttpResponse('Your are not allowed to delete this feedback')

    if request.method == 'POST':
        feedback.delete()
        return redirect('home')

    return render(request, 'reviews/delete.html', {'obj': feedback})


@login_required(login_url='login')
def updateMessage(request, pk):
    """
    Handles the updating of a message.

    This function allows users to update their own messages or allows staff
    members to update any message. If the user is not the author of the
    message and not a staff member, an error message is returned. For POST
    requests, it updates the message with the provided data if the form is
    valid. For GET requests, it renders a form pre-filled with the message
    data.

    Args:
        request: HttpRequest object containing metadata about the request.
        pk: int, primary key of the Messages object to be updated.

    Returns:
        HttpResponse: Rendered message update form page with context data or
        a redirect to the feedback page.
    """
    message = get_object_or_404(Messages, id=pk)
    form = MessageForm(instance=message)

    if request.user != message.author and not request.user.is_staff:
        return HttpResponse('Your are not allowed to update this message')

    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('feedback', pk=message.feedback.id)

    context = {'form': form}
    return render(request, 'reviews/feedback_form.html', context)


def createSubject(request):
    """
    Handles the creation of a new subject.

    This function displays a form to create a new subject and processes the
    form data submitted via POST requests. If the form is valid, the new
    subject is saved to the database and the user is redirected to the home
    page. For GET requests, it displays an empty form.

    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        HttpResponse: Rendered subject form page with context data or a
        redirect to the home page.
    """

    form = SubjectForm()

    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'reviews/subject_form.html', context)


def createTeacher(request):
    """
    Handles the creation of a new teacher.

    This function displays a form to create a new teacher and processes the
    form data submitted via POST requests. If the form is valid, the new
    teacher is saved to the database and the user is redirected to the home
    page. For GET requests, it displays an empty form.

    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        HttpResponse: Rendered teacher form page with context data or a
        redirect to the home page.
    """

    form = TeacherForm()

    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'reviews/subject_form.html', context)


def calculate_average_stars(feedbacks):
    """
    Calculate the average star rating from a list of feedbacks.
    Args:
        feedbacks:

    Returns:

    """
    stars = [feedback.stars for feedback in feedbacks if feedback.stars is not None]
    if stars:
        return round(sum(stars) / len(stars), 2)
    return None


def teacherProfile(request, pk):
    """
    Renders the profile page for a specific teacher.

    This function retrieves the teacher by their primary key (pk), gathers
    feedback related to the teacher, calculates the average star rating, and
    finds related disciplines (subjects). It then passes this data to the
    template for rendering the teacher's profile page.

    Args:
        request: HttpRequest object containing metadata about the request.
        pk: int, primary key of the Teacher object.

    Returns:
        HttpResponse: Rendered teacher profile page with context data.
    """

    teacher = get_object_or_404(Teacher, pk=pk)
    feedbacks = Feedback.objects.filter(teachers=teacher)
    average_stars = calculate_average_stars(feedbacks)
    related_disciplines = list(set(
        feedback.subject.name for feedback in feedbacks if feedback.subject is
        not None
    ))
    if not related_disciplines:
        related_disciplines = ["Nenhuma matéria relacionada"]
    context = {
        'teacher': teacher,
        'feedbacks': feedbacks,
        'related_disciplines': related_disciplines,
        'average_stars': average_stars
    }
    return render(request, 'reviews/teacher_profile.html', context)


def subjectProfile(request, pk):
    """
    Renders the profile page for a specific subject.

    This function retrieves the subject by its primary key (pk), gathers
    feedback related to the subject, calculates the average star rating, and
    finds related teachers. It then passes this data to the template for
    rendering the subject's profile page.

    Args:
        request: HttpRequest object containing metadata about the request.
        pk: int, primary key of the Subject object.

    Returns:
        HttpResponse: Rendered subject profile page with context data.
    """
    subject = get_object_or_404(Subject, pk=pk)
    feedbacks = Feedback.objects.filter(subject=subject)
    average_stars = calculate_average_stars(feedbacks)
    related_teachers = list(set(
        feedback.teachers.name for feedback in feedbacks if feedback.teachers
        is not None
    ))
    if not related_teachers:
        related_teachers = ["Nenhum professor relacionado"]
    context = {
        'subject': subject,
        'feedbacks': feedbacks,
        'related_teachers': related_teachers,
        'average_stars': average_stars
    }
    return render(request, 'reviews/subject_profile.html', context)


def userProfile(request, pk):
    """
    Renders the profile page for a specific user.

    Args:
        request: HttpRequest object containing metadata about the request.
        pk: Primary key of the User object.

    Returns:
        HttpResponse: Rendered user profile page with context data.
    """
    user = User.objects.get(id=pk)
    feedbacks = Feedback.objects.filter(author=user)
    context = {
        'user': user,
        'feedbacks': feedbacks
    }
    return render(request, 'reviews/user_profile.html', context)


@login_required
def upvote(request, message_id):
    """
    Handles upvoting a message.

    This function allows a logged-in user to upvote a message. If the user
    has already upvoted the message, the existing upvote is removed. If the
    user has not upvoted the message, an upvote is added. The user is then
    redirected to the feedback page containing the message.

    Args:
        request: HttpRequest object containing metadata about the request.
        message_id: int, primary key of the Messages object to be upvoted.

    Returns:
        HttpResponse: Redirect to the feedback page containing the message.
    """

    message = get_object_or_404(Messages, id=message_id)
    feedback = message.feedback
    user = request.user

    existing_vote = Vote.objects.filter(
        user=user,
        message=message,
        vote_type='up'
    ).first()

    if existing_vote:
        existing_vote.delete()
    else:
        Vote.objects.update_or_create(
            user=user,
            message=message,
            defaults={'vote_type': 'up'}
        )

    return redirect('feedback', pk=feedback.id)


@login_required
def downvote(request, message_id):
    """
    Handles downvoting a message.

    This function allows a logged-in user to downvote a message. If the user
    has already downvoted the message, the existing downvote is removed. If
    the user has not downvoted the message, a downvote is added. The user is
    then redirected to the feedback page containing the message.

    Args:
        request: HttpRequest object containing metadata about the request.
        message_id: int, primary key of the Messages object to be downvoted.

    Returns:
        HttpResponse: Redirect to the feedback page containing the message.
    """
    message = get_object_or_404(Messages, id=message_id)
    feedback = message.feedback
    user = request.user

    existing_vote = Vote.objects.filter(
        user=user,
        message=message,
        vote_type='down'
    ).first()

    if existing_vote:
        existing_vote.delete()
    else:
        Vote.objects.update_or_create(
            user=user,
            message=message,
            defaults={'vote_type': 'down'}
        )

    return redirect('feedback', pk=feedback.id)
