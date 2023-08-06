#!/usr/bin/env python

import sys
import mongoengine
import logging
from mongoengine.connection import get_connection
from django.test import TestCase
from django.apps import AppConfig
from django.conf import settings

__all__ = [
    'app',
    'ModjangoTestCase',
    'databases'
]

databases = {}

logger = logging.getLogger('modjango')


class ModjangoTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(ModjangoTestCase, cls).setUpClass()

        def setup_decorator(method):
            def decorated(*args, **kwargs):
                for key, value in databases.items():
                    logger.info('dropping', value, 'in setUp')
                    connection = get_connection(key)
                    connection.drop_database(value)
                return method(*args, **kwargs)
            return decorated

        def teardown_decorator(method):
            def decorated(*args, **kwargs):
                result = method(*args, **kwargs)
                for key, value in databases.items():
                    logger.info('dropping', value, 'in tearDown')
                    connection = get_connection(key)
                    connection.drop_database(value)
                return result
            return decorated
        cls.setUp = setup_decorator(cls.setUp)
        cls.tearDown = teardown_decorator(cls.tearDown)


class app(AppConfig):
    name = 'modjango'
    verbose_name = 'modjango'

    def ready(self):
        mongo_settings = self._validate_settings()

    def _validate_settings(self):
        mongo_settings = getattr(settings, 'MONGO', {})
        if len(mongo_settings):
            for key, value in mongo_settings.items():
                if self._is_testing():
                    message = "Creating test mongodb database for alias '%s'"
                    logger.info(message % key)
                connection = mongoengine.register_connection(
                    alias=key,
                    name=self._get_database_name(value),
                    host=value.get('HOST', 'localhost'),
                    port=value.get('PORT', 27017),
                    username=value.get('USER', None),
                    password=value.get('PASS', None),
                    authentication_source=value.get('AUTH_SOURCE', None),
                    **value.get('OPTIONS', {})
                )
                databases[key] = self._get_database_name(value)
            logger.info('the modjango app is ready')
        else:
            logger.warning('insufficient settings to connect to mongodb')

    def _get_database_name(self, value):
        prefix = ''
        if self._is_testing():
            prefix = 'test_'
        return prefix + value.get('NAME', 'default_database')

    def _is_testing(self):
        test_mode = getattr(settings, 'TEST_MODE', False)
        TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'
        return test_mode or TESTING


default_app_config = 'modjango.app'
