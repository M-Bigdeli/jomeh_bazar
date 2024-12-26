from django.core.handlers.wsgi import WSGIRequest


def create_message(request: WSGIRequest, message_text: str, message_status=2, message_icon="bxs-error-circle"):
    request.session["message_text"] = message_text

    if message_status == 1:
        request.session["message_class"] = "btn-bg-two"
    elif message_status == 2:
        request.session["message_class"] = "btn-bg-three"
    else:
        request.session["message_class"] = "btn-bg-four"

    request.session["message_icon"] = message_icon

