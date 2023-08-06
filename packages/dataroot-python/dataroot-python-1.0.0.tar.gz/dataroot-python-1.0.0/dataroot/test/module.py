import unittest

import dataroot


class TestModule(unittest.TestCase):

    def failed(self):
        self.failed = True

    def setUp(self):
        self.failed = False
        dataroot.write_key = 'testsecret'
        dataroot.on_error = self.failed

    def test_no_write_key(self):
        dataroot.write_key = None
        self.assertRaises(Exception, dataroot.track)

    def test_track(self):
        dataroot.track('userId', 'python module event')
        dataroot.flush()

    def test_identify(self):
        dataroot.identify('userId', { 'email': 'user@email.com' })
        dataroot.flush()

    def test_group(self):
        dataroot.group('userId', 'groupId')
        dataroot.flush()

    def test_alias(self):
        dataroot.alias('previousId', 'userId')
        dataroot.flush()

    def test_page(self):
        dataroot.page('userId')
        dataroot.flush()

    def test_screen(self):
        dataroot.screen('userId')
        dataroot.flush()

    def test_flush(self):
        dataroot.flush()
