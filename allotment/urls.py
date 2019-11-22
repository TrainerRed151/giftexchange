from django.contrib.auth.views import LoginView
from django.urls import path

from allotment.views import (
    home,
    party_view,
    signup,
)


urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('party/', party_view, name='party_view'),
]
