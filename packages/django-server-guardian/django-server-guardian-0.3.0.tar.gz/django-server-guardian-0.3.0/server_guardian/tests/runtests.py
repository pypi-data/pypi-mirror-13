#!/usr/bin/env python
"""
This script is a trick to setup a fake Django environment, since this reusable
app will be developed and tested outside any specific Django project.

Via ``settings.configure`` you will be able to set all necessary settings
for your app and run the tests as if you were calling ``./manage.py test``.

"""
import re

import django
from django.conf import settings

from fabric.api import abort, lcd, local
from fabric.colors import green, red

import test_settings

if not settings.configured:
    settings.configure(**test_settings.__dict__)

if __name__ == '__main__':
    if django.VERSION >= (1, 7):
        django.setup()
    local('coverage run testrunner.py')
    local('coverage html -d "{0}"'.format(
        settings.COVERAGE_REPORT_HTML_OUTPUT_DIR))

    local(
        'flake8 --ignore=E126 --ignore=W391 --statistics'
        ' --exclude=submodules,migrations,build .')

    with lcd(settings.COVERAGE_REPORT_HTML_OUTPUT_DIR):
        total_line = local('grep -n pc_cov index.html', capture=True)
        percentage = float(re.findall(r'(\d+)%', total_line)[-1])
    if percentage < 100:
        abort(red('Coverage is {0}%'.format(percentage)))
    print(green('Coverage is {0}%'.format(percentage)))
