#!/usr/bin/env python3

import logging
from random import randint
import unittest

try:
    import psycopg2
except:
    print("This should be run on the server or container with Python dependencies installed.")
    print("To start the container and run tests, use test.sh")
    sys.exit(0)

from game import Game

def random_wizard(game):
    wiz = randint(256, 2**64)
    tw = game.wizard(sub = wiz, username="wizard%d" % wiz).persist()
    return tw

def test_game_and_wizard():
    tg = Game()
    tw = random_wizard(tg)
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

    def test_edit_spell(self):
        "Modify an existing spell"
        tg = Game()
        ts = tg.spell(name="test_edit_spell", url="http://example.com/test_edit_spell").persist()
        ts.url = "http://example.com/test_edit_spell_2"
        ts.persist()
        ts2 = tg.spell.lookup(name="test_edit_spell")
        self.assertEqual(ts, ts2)

    def test_add_spell(self):
        "Add a spell to a wizard. Test that a repeat add will return False but not raise an exception" 
        (tg, tw) = test_game_and_wizard()
        ts = tg.spell(name="test_add_spell", url="http://example.com/test_add_spell").persist()
        self.assertFalse(tw.has_spell(ts))
        self.assertTrue(tw.add_spell(ts))
        self.assertFalse(tw.add_spell(ts))
        self.assertTrue(tw.has_spell(ts))

    def test_remove_spell(self):
        "Remove a spell from a wizard."
        (tg, tw) = test_game_and_wizard()
        ts = tg.spell(name="test_remove_spell", url="http://example.com/test_remove_spell").persist()
        self.assertFalse(tw.has_spell(ts))
        self.assertFalse(tw.remove_spell(ts))
        self.assertTrue(tw.add_spell(ts))
        self.assertTrue(tw.has_spell(ts))
        self.assertTrue(tw.remove_spell(ts))
        self.assertFalse(tw.has_spell(ts))

    def test_list_spells(self):
        "List the spells owned by a wizard"
        (tg, tw) = test_game_and_wizard()
        tw.persist()
        ts1 = tg.spell(name="test_list_spells_1", url="http://example.com/test_list_spells_1").persist()
        ts2 = tg.spell(name="test_list_spells_2", url="http://example.com/test_list_spells_2").persist()
        self.assertEqual([], tw.spells)
        tw.add_spell(ts1)
        tw.add_spell(ts2)
        tw = tw.refresh()
        self.assertEqual([ts1, ts2], tw.spells)

    def test_level(self):
        (tg, tw) = test_game_and_wizard()
        self.assertEqual(1, tw.level)
        tw.xp += 120
        self.assertEqual(2, tw.level)
        tw.xp += 10000 
        self.assertEqual(3, tw.level)

    def test_challenge(self):
        (tg, tw) = test_game_and_wizard()
        ow = random_wizard(tg)
        ts = tg.spell(name="test_challenge", url="http://example.com/test_challenge").persist()
        tw.add_spell(ts)
        tw.challenge(ow, ts)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    demo_db = Game(start_demo_db=True)
    unittest.main(failfast=True)
    demo_db.stop_demo_db()

# vim: autoindent textwidth=100 tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
