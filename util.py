"""Helper functions which can be called from any other layer. (but mainly from the business logic layer)"""
from typing import List
import os
from datetime import datetime
import bcrypt


def get_actual_time() -> str:
    return str(datetime.now())[:-7]


def hash_password(plain_password):
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def check_password(plain_password, hashed):
    hashed_password = hashed.encode('utf-8')
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
