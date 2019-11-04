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

def test_game_and_wizard():
    from random import randint
    tg = Game()
    wiz = randint(256, 2**64)
    tw = tg.wizard(sub = wiz, username="wizard%d" % wiz).persist()
    return (tg, tw)

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

    def lookup_new(self):
        tg = Game()
        wiz = tg.lookup(sub=9, username="gandalf")

    def test_add_spell(self):
        "Add a spell to a wizard. Test that a repeat add will return False but not raise an exception" 
        (tg, tw) = test_game_and_wizard()
        ts = tg.spell(name="test_add_spell").persist()
        self.assertFalse(tw.has_spell(ts))
        self.assertTrue(tw.add_spell(ts))
        self.assertFalse(tw.add_spell(ts))
        self.assertTrue(tw.has_spell(ts))

    def test_remove_spell(self):
        "Remove a spell from a wizard."
        (tg, tw) = test_game_and_wizard()
        ts = tg.spell(name="test_remove_spell").persist()
        self.assertFalse(tw.has_spell(ts))
        self.assertFalse(tw.remove_spell(ts))
        self.assertTrue(tw.add_spell(ts))
        self.assertTrue(tw.has_spell(ts))
        self.assertTrue(tw.remove_spell(ts))
        self.assertFalse(tw.has_spell(ts))

    def test_level(self):
        (tg, tw) = test_game_and_wizard()
        self.assertEqual(1, tw.level)
        tw.xp += 120
        self.assertEqual(2, tw.level)
        tw.xp += 10000 
        self.assertEqual(3, tw.level)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    demo_db = Game(start_demo_db=True)
    unittest.main(failfast=True)
    demo_db.stop_demo_db()

# vim: autoindent textwidth=100 tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
