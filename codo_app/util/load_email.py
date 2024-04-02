from codo_app import models

""" Function to get all emails who send emails
    """
    
def get_emails() -> list[dict[str:str]]:
    """Return a list of dict with email and password, from email host.
    To send all emails

    Returns:
        list{str:str}: List of dict with email and password
    """
    emails = models.EmailBase.objects.all()
    list_emails = []

    for email in emails:
        list_emails.append({"email": email.email, "pwd": email.password})

    return list_emails


def get_reply_to():
    """Just return all emails

    Returns:
        list: emails to reply to
    """
    emails = models.EmailBase.objects.all()
    list_emails = []

    for email in emails:
        list_emails.append(email.email)

    return list_emails
