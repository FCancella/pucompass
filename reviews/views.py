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

        user = authenticate(request, username=username, password=password)  # will return error, or if match, return a user object
        if user:
            login(request, user)  # add a user in the session, and logs it in
            return redirect('home')
        else:
            messages.error(request, "Username or password does not exist")

    context = {'page': page}
    return render(request, 'reviews/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # we save the form to access the user
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'reviews/login_register.html', {'form': form})


def chooseRoom(request):
    return render(request, 'reviews/choices.html')


@login_required(login_url='login')
def createFeedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)

        # Set the host field to the current user
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
    if request.method == 'POST':
        form = ForumFeedbackForm(request.POST)

        # Set the host field to the current user
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
    message = get_object_or_404(Messages, id=pk)
    feedback = message.feedback

    if request.user != message.author and not request.user.is_staff:
        return HttpResponse('You are not allowed to delete this message')

    if request.method == 'POST':
        message.delete()

        # Check if the user has any remaining messages in the feedback
        remaining_messages = Messages.objects.filter(feedback=feedback, author=request.user).exists()

        if not remaining_messages:
            feedback.participants.remove(request.user)

        return redirect('feedback', pk=feedback.id)

    return render(request, 'reviews/delete.html', {'obj': message})


@login_required(login_url='login')
def deleteFeedback(request, pk):
    feedback = get_object_or_404(Feedback, id=pk)

    if request.user != feedback.author and not request.user.is_staff:
        return HttpResponse('Your are not allowed to delete this feedback')

    if request.method == 'POST':
        feedback.delete()
        return redirect('home')

    return render(request, 'reviews/delete.html', {'obj': feedback})


@login_required(login_url='login')
def updateMessage(request, pk):
    message = get_object_or_404(Messages, id=pk)
    form = MessageForm(instance=message)  # we prefill with the value of the room

    if request.user != message.author and not request.user.is_staff:
        return HttpResponse('Your are not allowed to update this message')

    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        # it initializes a new MessageForm instance with the data from the submitted form (request.POST) and associates it with the existing message instance

        if form.is_valid():
            form.save()
            return redirect('feedback', pk=message.feedback.id)

    context = {'form': form}
    return render(request, 'reviews/feedback_form.html', context)


def createSubject(request):
    form = SubjectForm()

    if request.method == 'POST':
        form = SubjectForm(request.POST)

        if form.is_valid():
            subject = form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'reviews/subject_form.html', context)


def createTeacher(request):
    form = TeacherForm()

    if request.method == 'POST':
        form = TeacherForm(request.POST)

        if form.is_valid():
            teacher = form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'reviews/subject_form.html', context)


def calculate_average_stars(feedbacks):
    stars = [feedback.stars for feedback in feedbacks if feedback.stars is not None]
    if stars:
        return round(sum(stars) / len(stars), 2)
    return None


def teacherProfile(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    feedbacks = Feedback.objects.filter(teachers=teacher)
    average_stars = calculate_average_stars(feedbacks)
    related_disciplines = list(set(feedback.subject.name for feedback in feedbacks if feedback.subject is not None))
    if not related_disciplines:
        related_disciplines = ["Nenhuma matéria relacionada"]  # Essa foi a mudança principal do commit do front teacher profile
    context = {
        'teacher': teacher,
        'feedbacks': feedbacks,
        'related_disciplines': related_disciplines,  # Essa foi a mudança principal do commit do front teacher profile
        'average_stars': average_stars
    }
    return render(request, 'reviews/teacher_profile.html', context)


def subjectProfile(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    feedbacks = Feedback.objects.filter(subject=subject)
    average_stars = calculate_average_stars(feedbacks)
    related_teachers = list(set(feedback.teachers.name for feedback in feedbacks if feedback.teachers is not None))
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
    user = User.objects.get(id=pk)
    feedbacks = Feedback.objects.filter(author=user)
    context = {
        'user': user,
        'feedbacks': feedbacks
    }
    return render(request, 'reviews/user_profile.html', context)


@login_required
def upvote(request, message_id):
    message = get_object_or_404(Messages, id=message_id)
    feedback = message.feedback
    user = request.user

    # Check if the user has already upvoted the message
    existing_vote = Vote.objects.filter(user=user, message=message, vote_type='up').first()

    if existing_vote:
        # If an upvote already exists, remove it (toggle behavior)
        existing_vote.delete()
    else:
        # Otherwise, add an upvote
        Vote.objects.update_or_create(user=user, message=message, defaults={'vote_type': 'up'})

    return redirect('feedback', pk=feedback.id)


@login_required
def downvote(request, message_id):
    message = get_object_or_404(Messages, id=message_id)
    feedback = message.feedback
    user = request.user

    # Check if the user has already downvoted the message
    existing_vote = Vote.objects.filter(user=user, message=message, vote_type='down').first()

    if existing_vote:
        # If a downvote already exists, remove it (toggle behavior)
        existing_vote.delete()
    else:
        # Otherwise, add a downvote
        Vote.objects.update_or_create(user=user, message=message, defaults={'vote_type': 'down'})

    return redirect('feedback', pk=feedback.id)
