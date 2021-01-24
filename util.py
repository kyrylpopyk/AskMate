"""Helper functions which can be called from any other layer. (but mainly from the business logic layer)"""
from typing import List
import os
from datetime import datetime

def get_actual_time() -> str:
     return str(datetime.now())[:-7]
