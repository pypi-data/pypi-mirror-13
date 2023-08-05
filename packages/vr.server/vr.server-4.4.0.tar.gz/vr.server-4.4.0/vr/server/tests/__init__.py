import os
import shlex
import subprocess

from vr.common.utils import randchars


here = os.path.dirname(os.path.abspath(__file__))
os.environ['APP_SETTINGS_YAML'] = os.path.join(here, 'testconfig.yaml')


from django.contrib.auth.models import User
from django.core.management import call_command


def sh(cmd):
    subprocess.call(shlex.split(cmd), stderr=subprocess.STDOUT)


def dbsetup(port=None):
    os.chdir(here)
    sql = os.path.join(here, 'dbsetup.sql')
    port = ' -p {port} -h localhost'.format(**locals()) if port else ''
    cmd = 'psql -f %s -U postgres' % sql + port
    sh(cmd)

    # Now create tables
    call_command('syncdb', '--noinput')


def randurl():
    return 'http://%s/%s' % (randchars(), randchars())


def get_user():
    u = User(username=randchars())
    u.set_password('password123')
    u.is_admin = True
    u.is_staff = True
    u.save()
    return u
