from django.urls import path

from . import views
from .views import registration, create_poll_view
from .views import profile_view
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'polls'
urlpatterns = [
    path('', views.PollsListView.as_view(), name='index'),
    path('registration/', registration, name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('create_poll/', create_poll_view, name='create_poll'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
]