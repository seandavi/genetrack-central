"""
Main web application
"""
# create a a custom decorator here
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test, login_required

def private_login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that a non-public user is logged in, 
    redirecting to the log-in page if necessary.
    """
    def validator (user):
        return user.is_authenticated() and user.username != 'public'

    actual_decorator = user_passes_test(
        validator, redirect_field_name=redirect_field_name
    )
    
    if function:
        return actual_decorator(function)
    return actual_decorator
