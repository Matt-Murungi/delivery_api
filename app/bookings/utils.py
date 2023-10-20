import random
import string


def random_string_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def generate_booking_id(instance):
    """
    generate unique uppercase and numbers strings
    """
    new_booking_id = random_string_generator().upper()
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(booking_id=new_booking_id).exists()
    if qs_exists:
        return generate_order_id(instance)
    return new_booking_id
