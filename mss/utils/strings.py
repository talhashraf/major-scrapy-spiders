'''MSS: String utility functions'''
import re
from unidecode import unidecode


def process_string(input_string):
    '''Remove white space and unicode characters'''
    return unidecode(re.sub(r'\s+', ' ', input_string).strip())
