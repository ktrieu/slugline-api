from django.urls import path

from user.views import *

urlpatterns = [
    path('login/', login_view),
    path('logout/', logout_view),
    path('auth/', auth_view),
    path('user/update', update_user_view),
    path('users/list', list_users_view),
    path('users/<str:username>', list_user_view),
    path('users/<str:username>/create', create_user_view),
    path('users/<str:username>/update', update_generic_user_view),
    path('users/<str:username>/delete', delete_user_view)
]
