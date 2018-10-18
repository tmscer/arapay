#!/usr/bin/env python3

# Run this script in your django shell a file formatted the following way:
# <username>,<email>
# ...

import random
import string
import sys

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from social_django.models import UserSocialAuth

filename = "/home/tmscer/tmp/arapay/names"
rand = random.SystemRandom()


def user_supplier(fname):
    with open(fname, mode='r') as f:
        for user in f:
            yield user.replace('\n', '').split(',')


def password(l, arr=string.printable[:-5]):
    global rand
    return "".join(rand.choice(arr) for _ in range(l))


for name, email in user_supplier(filename):
    try:
        user = User.objects.get_by_natural_key(name)
        print("o {}".format(user))
    except ObjectDoesNotExist:
        user = User.objects.create_user(username=name, email=email, password=password(30))
        user.save()
        print("+ {}".format(user))
    try:
        auth = UserSocialAuth.objects.get_social_auth(provider='google-oauth2', uid=user.email)
        if not auth:
            raise ObjectDoesNotExist()
        print("o AUTH for {}".format(user))
    except ObjectDoesNotExist:
        auth = UserSocialAuth(user=user, provider='google-oauth2', uid=user.email)
        auth.save()
        print("+ AUTH for {}".format(user))
