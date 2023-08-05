import codecs
import json
import os
import platform
import subprocess
import time


def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True).strip()
    except subprocess.CalledProcessError as e:
        return ''

def wait_for(limit, seconds, func, *args, **kwargs):
    c = 0
    while c < limit and func(*args, **kwargs):
        c += 1
        time.sleep(seconds)
    return func(*args, **kwargs)

def read_config_file(filename):
    """
    Example of the file localhost.json:
    {
        "ami": "123",
        "hosts": ["a.com", "b.com"]
    }
    """
    if os.path.exists(filename):
        with codecs.open(filename, 'r', 'utf-8') as f:
           return json.loads(f.read())

def str2bool(string):
    "It returns True, False or None"
    if not string:
        return None
    if isinstance(string, (str,)):
        string = string.lower()
        options = ['none', 'null', 'nil']
        if string in options:
            return None
        options = ['false', 'f', 'no', '0']
        return not (string in options)
    return string

def is_mac():
    return platform.system().lower() == 'darwin'

def is_linux():
    return platform.system().lower() == 'linux'
