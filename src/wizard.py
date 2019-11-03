#!/usr/bin/env python3

class Wizard(object):
    game = None

    def __init__(self, wid=None, sub=None, xp=0, username=None):
        self.id = wid
        self.sub = sub
        self.xp = xp
        self.username = username

    def __repr__(self):
        return "Wizard %d %s with XP %d" % (self.id, self.username, self.xp)

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

    def has_spell(self, spell):
        with self.game.conn.cursor() as curs:
            curs.execute('''SELECT COUNT(*) FROM wizard_spell
                            WHERE wizard = %s AND spell = %s''',
                            (self.id, spell.id))
            return curs.fetchone()[0] == 1

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
                return cls(*curs.fetchone())
            except TypeError:
                return cls(sub=sub, username=username).persist()


# vim: autoindent textwidth=100 tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
