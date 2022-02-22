from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),
    # Страница сообществ
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    # Профайл пользователя
    path('profile/<str:username>/', views.profile, name='profile'),
    # Просмотр отдельного поста
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    # Создание нового поста
    path('create/', views.post_create, name='post_create'),
    # Редактирование созданного поста
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    # Добовляем комментарий для поста
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
    # Информация о подписках
    path('follow/', views.follow_index, name='follow_index'),
    # Подписаться на автора
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    # Отписаться от автора
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
]
