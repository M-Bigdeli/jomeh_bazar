from django.shortcuts import render
from django.http import HttpResponse


def delete_message(request):
    """
     This view deletes message`s sessions.
     Call this in javascript after show message to user.
    """
    del request.session['message_text']
    del request.session['message_class']
    del request.session['message_icon']
    return HttpResponse("ok")
