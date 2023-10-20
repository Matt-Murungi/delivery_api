import random


def generate_otp():
    key = random.randint(10001, 99999)
    return key
