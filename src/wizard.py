#!/usr/bin/env python3

import logging

class BattleResult(object):

    def __init__(self, winner, loser, text=None):
        self.winner = winner
        self.loser = loser
        if text is None:
            if self.winner and self.loser:
                self.text = "%s defeats %s" % (winner.username, loser.username)
            else:
                self.text = "No winner or loser."
        else:
            self.text = text

    def __repr__(self):
        return self.text


class Wizard(object):
    game = None

    def __init__(self, wid=None, sub=None, xp=0, username=None, spells=None):
        self.id = wid
        self.sub = sub
        self.xp = xp
        self.username = username
        if spells == None:
            self.spells = []
        else:
            self.spells = spells

    def __repr__(self):
        return "Level %d wizard (%d) %s with XP %d" % (self.level, self.id, self.username, self.xp)

    @property
    def level(self):
        if self.xp >= 800:
            return 3
        if self.xp >= 100:
            return 2
        return 1

    def __eq__(self, other):
        if (not self) or (not other):
            return False
        if self.id and other.id and self.id != other.id:
            return False
        if self.sub != other.sub:
            return False
        return True
        
    def persist(self):
        with self.game.conn.cursor() as curs:
            if self.id is not None:
                curs.execute('''UPDATE wizard SET sub = %s, xp = %s, username = %s
                                WHERE id = %s''',
                    (self.sub, self.xp, self.username, self.id))
            else:
                curs.execute('''INSERT INTO wizard (sub, xp, username)
                                VALUES (%s, %s, %s) RETURNING id''',
                    (self.sub, self.xp, self.username))
                self.id = curs.fetchone()[0]
            curs.connection.commit()
        assert(self.id is not None)
        return self

    def add_spell(self, spell):
        with self.game.conn.cursor() as curs:
            curs.execute('''INSERT INTO wizard_spell (wizard, spell)
                            VALUES (%s, %s) ON CONFLICT DO NOTHING''',
                            (self.id, spell.id))
            curs.connection.commit()
            return curs.rowcount > 0

    def remove_spell(self, spell):
        with self.game.conn.cursor() as curs:
            curs.execute('''DELETE FROM wizard_spell
                            WHERE wizard = %s AND spell = %s''',
                            (self.id, spell.id))
            curs.connection.commit()
            return curs.rowcount > 0

    def has_spell(self, spell):
        with self.game.conn.cursor() as curs:
            curs.execute('''SELECT COUNT(*) FROM wizard_spell
                            WHERE wizard = %s AND spell = %s''',
                            (self.id, spell.id))
            return curs.fetchone()[0] == 1

    def challenge(self, opponent, spell):
        if not self.has_spell(spell):
            return BattleResult(opponent, self,
                                "%s attempted an attack with %s, a spell they don't have." % (spell.name, self.username))
        if opponent.has_spell(spell):
            return BattleResult(opponent, self,
                                "%s blocked the %s spell." % (opponent.username, spell.name))
        difference = opponent.level - self.level
        if difference > 1:
            gain = 80
        elif difference > 0:
            gain = 20
        elif difference > -1:
            gain = 10
        else:
            gain = 0
        self.xp += gain
        self.persist()
        return BattleResult(self, opponent,
                            "%s defeated %s (level %d) with a %s spell and gained %d XP!" %
                            (self.username, opponent.username, opponent.level, spell.name, gain))

    def refresh(self):
        if not self.id:
            self.persist()
        return self.__class__.lookup(wid=self.id)

    @classmethod
    def lookup(cls, wid=None, sub=None, username=None):
        if not wid and not sub:
            return None
        (all_wids, all_subs, all_usernames) = (False, False, False)
        if not wid:
            all_wids = True
        if not sub:
            all_subs = True
        if not username:
            all_usernames = True
        with cls.game.conn.cursor() as curs:
            curs.execute('''SELECT id, sub, xp, username FROM wizard WHERE
                            (id = %s OR %s) AND
                            (sub = %s OR %s) AND
                            (username = %s OR %s)
                            ''', (wid, all_wids, sub, all_subs, username, all_usernames))
            try:
                wizard = cls(*curs.fetchone())
                curs.execute('''SELECT spell.id, spell.name, spell.url FROM spell
                                JOIN wizard_spell ON spell.id = wizard_spell.spell
                                WHERE wizard_spell.wizard = %s
                                ''', (wizard.id,))
                for row in curs.fetchall():
                    wizard.spells.append(cls.game.spell(*row))
                return wizard
            except TypeError:
                return cls(sub=sub, username=username).persist()


# vim: autoindent textwidth=100 tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
