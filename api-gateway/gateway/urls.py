from django.urls import path, re_path
from .views import BookServiceView, UserServiceView, LoanServiceView, health_check

urlpatterns = [
    path('health/', health_check),
    re_path(r'^books(?P<path>.*)$', BookServiceView.as_view()),
    re_path(r'^users(?P<path>.*)$', UserServiceView.as_view()),
    re_path(r'^loans(?P<path>.*)$', LoanServiceView.as_view()),
]