import urllib.request
import os


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def checkurl(url):
    try:
        urllib.request.urlopen(url)
        return True
    except Exception as e:
        return False


def check_exists(file):
    if os.path.exists(file):
        return True
    else:
        return False

#  pyuic5 messenger.ui -o clientui.py
