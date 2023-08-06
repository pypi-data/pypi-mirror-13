# Copyright (c) 2013 Qubell Inc., http://qubell.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = "Vasyl Khomenko"
__email__ = "vkhomenko@qubell.com"
__copyright__ = "Copyright 2014, Qubell.com"
__license__ = "Apache"


import unittest


import types

import copy
from nose.loader import TestLoader
import sys


import sys
import unittest
from functools import wraps

def instance(byApplication):
    def wrapper(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            pass
        return wrapped_func
    return wrapper

values=workflow=instance


def _parameterize(source_case, cases, tests):
        '''This generates the classes (in the sense that it's a generator.)
        '''
        def clean(source):
            test_methods = [method.__name__ for _, method in source.__dict__.items()
                                if isinstance(method, types.FunctionType) and method.func_name.startswith("test")]
            setattr(source_case, '__name__', 'Source')
            setattr(source_case, 'className', 'Source')
            for test in test_methods:
                delattr(source_case, test)

        for test_name, test_method in tests.items():
            setattr(source_case, test_name, test_method)

        case_mod = sys.modules[source_case.__module__]
        case_name = source_case.__name__
        attrs = dict(source_case.__dict__)
        clean(source_case)
        for env_name, param_set in cases.items():
            updated_case = type('{0}_{1}'.format(case_name, env_name), (source_case,), attrs)
            setattr(updated_case, 'className', env_name)
            setattr(case_mod, updated_case.__name__, updated_case)
            updated_case.current_environment = env_name
            yield updated_case

def parameterize(source_case, cases={}, tests={}):
    return list(_parameterize(source_case, cases, tests))

def environment(params):
    def wraps_class(clazz):
        # Old style (cls.apps) application support hack
        if 'apps' in clazz.__dict__:
            applications(clazz.apps)(clazz)

        # Add test cases
        parameterize(source_case=clazz, cases=params)
        return clazz
    return wraps_class
environments = environment

def applications(appsdata):
    """
    Class decorator that allows to crete applications and start instances there.
    If used with environment decorator, instances would be started for every env.
    :param appdata: list
    """
    def wraps_class(clazz):

        for appdata in appsdata:
            if appdata.get('launch', True):
                app_name = appdata['name']
                if appdata.get('add_as_service'):
                    start_name='test00_launch_%s' % app_name
                    destroy_name='testzz_destroy_%s' % app_name
                else:
                    start_name='test01_launch_%s' % app_name
                    destroy_name='testzy_destroy_%s' % app_name
                parameters = appdata.get('parameters', {})
                settings = appdata.get('settings', {})

                # Prepare tests dict
                tests={}
                def launch_method(self):
                    self._launch_instance(app_name=app_name,  parameters=parameters, settings=settings)

                def destroy_method(self):
                    self._destroy_instance(app_name=app_name)

                tests[start_name] = launch_method
                tests[start_name].__name__ = start_name
                tests[start_name].__doc__ = 'Launch %s' % app_name # TODO: Pass env here somehow
                tests[destroy_name] = destroy_method
                tests[destroy_name].__name__ = destroy_name
                tests[destroy_name].__doc__ = 'Destroy %s' % app_name

                # Update class with new methods
                parameterize(clazz, tests=tests)
        return clazz
    return wraps_class



class BaseComponentTestCase(unittest.TestCase):
    ppp = 'ppp'

    setup_error = None

    @classmethod
    def setUpClass(cls):
        try:
            assert False, "Fail intentionally in setup"
        except BaseException as e:
            cls.setup_error = e

    def setUp(self):
        pass
        #if self.setup_error:
        #    raise self.setup_error

    def _launch_instance(self, app_name, parameters, settings):
        print "Launching %s" % app_name

    def _destroy_instance(self, app_name):
        pass
