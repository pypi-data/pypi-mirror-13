import re


def is_email(username):
    err_msg = ("No override user supplied, please enter a user to override "
               "as in the format of an email address")
    if len(username) > 0:
        match = re.match('[^@]+@[^@]+\.[^@]+', username)
        if not match:
            err_msg = "Override user must be an email address.  You entered: "
        else:
            err_msg = None
    return err_msg
