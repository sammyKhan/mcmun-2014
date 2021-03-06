import random


def is_spam(data):
    address = data.get('address', '')
    phone_number = data.get('phone_number', '')
    school_name = data.get('school_name', '')
    first_name = data.get('first_name', '')
    return (address.startswith('http://') or phone_number == '123456' or
            school_name == first_name)


def generate_random_password(length=12, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
        """
        Returns a random string of length characters from the set of a-z, A-Z, 0-9.

        From http://www.bloggerpolis.com/2011/09/how-to-generate-a-django-password/
        """
        return unicode(''.join(random.choice(allowed_chars) for i in xrange(length)))
