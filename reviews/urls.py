from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Login/Sign Up/Logout
    path('login/',
         views.loginPage,
         name="login"),

    path('logout/',
         views.logoutUser,
         name="logout"),

    path('register/',
         views.registerPage,
         name="register"),

    # CRUD
    path('choose-room-type/',
         views.chooseRoom,
         name="choose-room-type"),

    path('feedback-form/',
         views.createFeedback,
         name="feedback-form"),

    path('forum-feedback-form/',
         views.createForumFeedback,
         name="forum-feedback-form"),

    path('subject-form/',
         views.createSubject,
         name="subject-form"),

    path('teacher-form/',
         views.createTeacher,
         name="teacher-form"),

    # Forum CRUD
    path('delete-message/<int:pk>/',
         views.deleteMessage,
         name="delete-message"),
    path('delete-feedback/<int:pk>/',
         views.deleteFeedback,
         name="delete-feedback"),
    path('update-message/<str:pk>/',
         views.updateMessage,
         name="update-message"),

    # Profile and feedback views
    path('teacher/<int:pk>/',
         views.teacherProfile,
         name="teacher-profile"),

    path('subject/<str:pk>/',
         views.subjectProfile,
         name="subject-profile"),

    path('user/<str:pk>/',
         views.userProfile,
         name="user-profile"),

    path('feedback/<int:pk>/',
         views.feedback,
         name="feedback"),

    # Voting system
    path('upvote/<int:message_id>/',
         views.upvote,
         name='upvote'),

    path('downvote/<int:message_id>/',
         views.downvote,
         name='downvote'),
]
