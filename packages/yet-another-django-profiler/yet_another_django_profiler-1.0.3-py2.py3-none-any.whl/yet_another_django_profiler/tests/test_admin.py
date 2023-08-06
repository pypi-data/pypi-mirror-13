# encoding: utf-8
# Created by Jeremy Bowman on Fri Feb 21 17:28:37 EST 2014
# Copyright (c) 2014, 2015 Safari Books Online. All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE file for details.
"""
Yet Another Django Profiler Django admin profiling tests
"""

from __future__ import unicode_literals

import platform
import sys

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.text import force_text

import pytest


class AdminCases(object):
    """Django admin page profiling tests to be run for each profiler backend"""

    def test_call_graph(self):
        """Using "profile" without a parameter should yield a PDF call graph even for admin changelists"""
        response = self._get_test_page('profile')
        assert response['Content-Type'] == 'application/pdf'

    def test_calls_by_time(self):
        """Using profile=time should show a table of function calls sorted by internal time even for admin changelists"""
        response = self._get_test_page('profile=time')
        self.assertContains(response, 'Ordered by: internal time')

    def test_pattern(self):
        """It should be possible to specify a regular expression filter pattern even for admin changelists"""
        response = self._get_test_page('profile=time&pattern=models')
        self.assertRegexpMatches(force_text(response.content, 'utf-8'), r"due to restriction <u?'models'>")

    def _get_test_page(self, params=''):
        url = reverse('admin:auth_user_changelist')
        if params:
            url += '?' + params
        return self.client.get(url)


@override_settings(YADP_ENABLED=True)
class CProfileTest(TestCase, AdminCases):
    """Profiling parameter tests using cProfile"""

    def setUp(self):
        User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.client.login(username='admin', password='password')

    def test_backend(self):
        """The cProfile profiling backend should be used"""
        from yet_another_django_profiler.conf import settings
        assert settings.YADP_PROFILER_BACKEND == 'cProfile'


@pytest.mark.skipif(platform.python_implementation() != 'CPython' or sys.version_info[:2] in ((3, 2), (3, 5)),
                    reason='yappi does not yet work in this Python implementation')
@override_settings(YADP_ENABLED=True, YADP_PROFILER_BACKEND='yappi')
class YappiTest(TestCase, AdminCases):
    """Profiling parameter tests using Yappi instead of cProfile"""

    def setUp(self):
        User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.client.login(username='admin', password='password')

    def test_backend(self):
        """The Yappi profiling backend should be used"""
        from yet_another_django_profiler.conf import settings
        assert settings.YADP_PROFILER_BACKEND == 'yappi'
