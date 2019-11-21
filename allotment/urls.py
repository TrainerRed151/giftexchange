from django.urls import path

from allotment.views import (
    party_view,
    signup,
)


urlpatterns = [
    path('signup/', signup, name='signup'),
    path('party/', party_view, name='party_view'),
]
