import requests, random


def clean_phone_number(phone_number):
    """
    This function is used to convert an incomplete phone number to a complete one.
    For example, it converts 09123456789 to 098123456789.

    :param phone_number:
    :return: clean_phone_number
    """
    if phone_number.startswith("+98"):
        phone_number = phone_number[3:]
    elif phone_number.startswith("098"):
        phone_number = phone_number[3:]
    elif phone_number.startswith("0"):
        phone_number = phone_number[1:]
    return ("098" + phone_number)


def send_verification_code(phone_number):
    """
    This function sends a code to the user's phone number to verify that phone number and returns the code to you.

    :param phone_number:
    :return: code
    """
    code = random.randint(1000, 9999)
    text = "شماره تلفن:" + "\n" + phone_number + "\n\n" + "کد تایید:" + "\n" + str(code) + "‌"
    requests.request("GET",
                     "https://eitaayar.ir/api/bot246962:27a808b0-fde7-4679-8957-7f9b642ec27d/sendMessage?chat_id=test_bot_bigdeli&text=" + text)
    return str(code)
