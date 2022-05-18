from django.conf import settings
from django.conf.urls import include, url
from django.urls import path
from rest_framework import routers

import core.views as views

router = routers.DefaultRouter()

urlpatterns = [
    path('user/',
         views.UserListView.as_view(),
         name='user-list'
         ),
    path('user/<int:user_id>/',
         views.UserUpdateView.as_view(),
         name='user-update'
         ),
    path('user/header/',
         views.UserHeaderView.as_view(),
         name='user-header'
         )
]
urlpatterns += router.urls

if settings.DEVELOP:
     urlpatterns += path('develop/',
         views.DevelopView.as_view(),
         name='develops'
         ),
