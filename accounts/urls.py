from django.urls import path, include
from .views import upgrade_me
from .views import IndexView

urlpatterns = [

    path('account/', IndexView.as_view()),
    path('', include('allauth.urls')),
    path('upgrade/', upgrade_me, name='upgrade'),
]