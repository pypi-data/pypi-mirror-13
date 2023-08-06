#!/usr/bin/env python
"""
This script sets up the test runner, that is called within runtests.py.

"""
import sys


import django
from django.conf import settings

import test_settings

if not settings.configured:
    settings.configure(**test_settings.__dict__)


from django_nose import NoseTestSuiteRunner


def runtests(*test_args):
    if django.VERSION >= (1, 7):
        django.setup()

    failures = NoseTestSuiteRunner(verbosity=2, interactive=True).run_tests(
        test_args)

    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
