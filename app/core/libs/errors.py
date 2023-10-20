user_non_existant = "User does not exist in the system"
email_not_existant = "Email does not exist"
invalid_email = "Please specify a valid email address"
invalid_user = "Unable to authenticate user, please check your email and password again"
partner_non_existant = "User is not a partner"
incorrect_password = "Incorrect Password. Please provide correct password"
not_a_partner = "User does not belong to partner"
unconfirmed_account = "Your account has not yet been confirmed.\
     Contact bdeliv Secure Administration to confirm your account"


def generate_error_for_empty(string):
    msg = f"{string} can not be empty"
    return msg


def generate_error_for_not_existant(string):
    msg = f"{string} does not exist"
    return msg


def generate_error_for_already_exists(string):
    msg = f"{string} already exist"
    return msg


def generate_internal_server_error(error):
    return {"detail": error}
