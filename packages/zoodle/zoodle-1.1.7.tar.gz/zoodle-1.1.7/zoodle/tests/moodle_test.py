"""
Unit tests for Moodle
"""

from unittest import TestCase

from zoodle.command import load_configuration
from zoodle.moodle import Moodle, CredentialsError

class MoodleTest(TestCase):
    """
    unit tests for the Moodle class
    """

    def setUp(self):
        self.options = load_configuration('settings_local.ini', 'DEFAULT')

    def test_correct_login(self):
        """
        verifies a known-good set of login credentials can access Moodle
        """
        moodle = Moodle(self.options['baseurl'], self.options['username'], self.options['password'])
        self.assertIsNotNone(moodle)
        
    def test_incorrect_login(self):
        """
        verifies a known-bas set of login credentials can access Moodle
        """
        self.options['password'] = self.options['password'] + "1"
        self.assertRaises(CredentialsError,
                          Moodle,
                          self.options['baseurl'],
                          self.options['username'],
                          self.options['password'])
