#!/usr/bin/env python3

import logging
import unittest

try:
    import psycopg2
except:
    print("This should be run on the server or container with Python dependencies installed.")
    print("To start the container and run tests, use test.sh")
    sys.exit(0)

from game import Game


class WizardTestCase(unittest.TestCase):

    def test_db_time(self):
        '''
        Sanity test: is the time on the database close to the time in the application?
        '''
        tg = Game()
        from datetime import datetime
        self.assertAlmostEqual(tg.now().timestamp(), datetime.now().timestamp(), delta = 0.2)

    def test_persist_and_lookup_account(self):
        "We can persist an account to the database and get the same account back."
        tg = Game()
        testuser = tg.wizard(sub='31337', username="jrdobbs")
        testuser = testuser.persist()
        wiz1 = tg.wizard.lookup(sub='31337')
        self.assertEqual(testuser, wiz1)
        wiz2 = tg.wizard.lookup(wid=testuser.id)
        self.assertEqual(testuser, wiz2)
        nosuchwiz = tg.wizard.lookup(sub='42')
        self.assertIsNone(nosuchwiz)

    def test_name_change(self):
        tg = Game()
        alice = tg.wizard(sub="1", username="alice").persist()
        bob = tg.wizard(sub="2", username="bob").persist()
        bob.username = 'jrdobbs'
        bob.persist()
        alice2 = tg.wizard.lookup(wid=alice.id)
        bob2 = tg.wizard.lookup(wid=bob.id)
        self.assertEqual(alice, alice2)
        self.assertEqual(bob, bob2)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    demo_db = Game(start_demo_db=True)
    unittest.main(failfast=True)
    demo_db.stop_demo_db()

# vim: autoindent textwidth=100 tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
