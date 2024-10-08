"""
URL configuration for restapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from APP.views import ObtainAuthTokenView, CreateAccountView, EditProfileView, CreatePostView, GetUsersView, GetMeView, GetUserView, GetPostsView, DeletePostView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', ObtainAuthTokenView.as_view(), name='token'),
    path('api/create-account/', CreateAccountView.as_view(), name='create-account'),
    path('api/edit-profile/', EditProfileView.as_view(), name='edit-profile'),
    path('api/create-post/', CreatePostView.as_view(), name='create-post'),
    path('api/get-users/', GetUsersView.as_view(), name='get-users'),
    path('api/get-me/', GetMeView.as_view(), name='get-me'),
    path('api/get-user/<int:user_id>/', GetUserView.as_view(), name='get-user'),
    path('api/get-posts/', GetPostsView.as_view(), name='get-posts'),
    path('api/delete-post/', DeletePostView.as_view(), name='delete-post'),
]
