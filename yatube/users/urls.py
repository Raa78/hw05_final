from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordResetDoneView,
    PasswordResetView
)
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    # Страница регистрации
    path('signup/', views.SignUp.as_view(), name='signup'),
    # Страница авторизации
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    # Выход из аккаунта
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    # Смена пороля: задать новый пароль
    path(
        'password_change/',
        PasswordChangeView.as_view(
            template_name="users/password_change_form.html"),
        name="password_change",
    ),
    # Смена пороля: уведомление об удачной смене пароля
    path(
        "password_change/done/",
        PasswordChangeDoneView.as_view(
            template_name="users/password_change_done.html"
        ),
        name="password_change_done",
    ),
    # Форма для сброса/восстановления пароля через email
    path(
        'password_reset/',
        PasswordResetView.as_view(
            template_name="users/password_reset_form.html"),
        name="password_reset",
    ),
    # Уведомление об отправки ссылки для воставноления пароля на email
    path(
        "password_reset/done/",
        PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    # Восстановления пароля: сброс пороля по ссылке из email
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    # Восстановления пароля: уведомление пароль изменен
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="reset_done_complete",
    ),
]
