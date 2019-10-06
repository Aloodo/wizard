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
        return self

    @classmethod
    def lookup(cls, wid=None, sub=None):
        (all_wids, all_subs) = (False, False)
        if not wid:
            all_wids = True
        if not sub:
            all_subs = True
        with cls.game.conn.cursor() as curs:
            curs.execute('''SELECT id, sub, xp, username FROM wizard WHERE
                            (id = %s OR %s) AND
                            (sub = %s OR %s)
                            ''', (wid, all_wids, sub, all_subs))
            try:
                return cls(*curs.fetchone())
            except TypeError:
                return None


# vim: autoindent textwidth=100 tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
