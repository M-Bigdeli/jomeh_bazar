from django.core.handlers.wsgi import WSGIRequest


def create_message(request: WSGIRequest, message_text: str, message_status=2, message_icon="bxs-error-circle"):
    """
    This function creates a message for show in templates.
    It can be used anywhere in the project.

    message_status will be a number between 1 and 3.
    In templates, the number 1 displays a red warning message,
    the number 2 displays a yellow message matching the template style,
    and the number 3 displays a green success message.

    message_icon determines what icon to display next to this message.
    The value it receives is the class name of the icons available at https://boxicons.com because the project template uses it.
    (You don't need to include the "bx" at the beginning.)

    :param request:
    :param message_text:
    :param message_status:
    :param message_icon:
    """
    request.session["message_text"] = message_text
    if message_status == 1:
        request.session ["message_class"] = "btn-bg-two"
    elif message_status == 2:
        request.session["message_class"] = "btn-bg-three"
    else:
        request.session["message_class"] = "btn-bg-four"

    request.session["message_icon"] = message_icon
