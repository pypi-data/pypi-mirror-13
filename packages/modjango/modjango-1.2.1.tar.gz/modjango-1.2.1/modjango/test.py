#!/usr/bin/env python

import django
import unittest
import modjango
import mongoengine
from mongoengine.connection import get_connection, ConnectionError
from django.conf import settings
from django.apps.registry import Apps


class TestAppReady(unittest.TestCase):

    def setUp(self):
        setattr(settings, 'MONGO', {
            'MAIN': {
                'HOST': 'mongodb',
                'NAME': 'main'
                }
        })
        self.tearDown()

    def tearDown(self):
        try:
            connection = get_connection('MAIN')
            connection.drop_database('main')
            connection.drop_database('test_main')
            modjango.databases = {}
        except ConnectionError as err:
            pass
        setattr(settings, 'TEST_MODE', False)

    def test_setup_with_single_database(self):
        Apps(['modjango'])
        expected_result = {'MAIN': 'main'}
        self.assertEqual(modjango.databases, expected_result)

    def test_setup_in_testing_mode(self):
        setattr(settings, 'TEST_MODE', True)
        Apps(['modjango'])
        expected_result = {'MAIN': 'test_main'}
        self.assertEqual(modjango.databases, expected_result)

    def test_setup_with_insufficient_settings(self):
        delattr(settings, 'MONGO')
        Apps(['modjango'])
        expected_result = {}
        self.assertEqual(modjango.databases, expected_result)


class TestModjangoTest(unittest.TestCase):

    def setUp(self):
        setattr(settings, 'MONGO', {
            'MAIN': {
                'HOST': 'mongodb',
                'NAME': 'main'
                }
        })
        setattr(settings, 'DATABASES', {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
                }
        })
        Apps(['modjango'])

    def test_the_test_class(self):
        modjango.ModjangoTestCase.setUpClass()
        testcase = modjango.ModjangoTestCase()
        testcase.setUp()
        testcase.tearDown()


class User(mongoengine.Document):
    name = mongoengine.StringField()
    password = mongoengine.StringField()


if __name__ == '__main__':
    settings.configure()
    unittest.main(exit=False)

    # the reason why I created the following two unit tests was to ensure that
    # we could create multiple subclasses of ModjangoTestCase and it would
    # properly do the database dropping on each subclass.  I ran into a bug
    # where it would drop the databases after the first class's teardown but
    # not after the setup of the method
    print('now running tests manually')

    setattr(settings, 'MONGO', {
        'default': {
            'HOST': 'mongodb',
            'NAME': 'main'
            }
    })
    setattr(settings, 'DATABASES', {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
            }
    })
    Apps(['modjango'])

    class ModjangoTestExample(modjango.ModjangoTestCase):

        def test_count(self):
            user = User('a', 'b')
            user.save()
            user2 = User('b', 'c')
            user2.save()
            self.assertEqual(2, User.objects.count())

    class ModjangoTestExampleWithThree(modjango.ModjangoTestCase):

        def test_count(self):
            user = User('d', 'e')
            user.save()
            user2 = User('e', 'f')
            user2.save()
            user3 = User('f', 'g')
            user3.save()
            self.assertEqual(3, User.objects.count())

    class ModjangoTestExampleWithFour(modjango.ModjangoTestCase):

        def test_count(self):
            user = User('d', 'e')
            user.save()
            user2 = User('e', 'f')
            user2.save()
            user3 = User('f', 'g')
            user3.save()
            User('g', 'h').save()
            self.assertEqual(4, User.objects.count())

    suite = unittest.TestSuite()
    suite.addTest(ModjangoTestExample('test_count'))
    suite.addTest(ModjangoTestExampleWithThree('test_count'))
    suite.addTest(ModjangoTestExampleWithFour('test_count'))
    runner = unittest.TextTestRunner()
    runner.run(suite)
    print('done running tests manually')
