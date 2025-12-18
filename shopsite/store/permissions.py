from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden

def staff_or_superuser_required(view_func):
    """
    Доступ: менеджер (is_staff) ИЛИ администратор (is_superuser).
    """
    return user_passes_test(
        lambda u: u.is_authenticated and (u.is_staff or u.is_superuser)
    )(view_func)

def superuser_required(view_func):
    """
    Доступ: только администратор (is_superuser).
    """
    return user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser
    )(view_func)
