#!/usr/bin/env python3

class Spell(object):
    game = None

    def __init__(self, sid=None, name=None):
        self.id = sid
        self.name = name

    def __repr__(self):
        return "Spell %d %s" % (self.id, self.name)

    def __eq__(self, other):
        if (not self) or (not other):
            return False
        if self.id and other.id and self.id != other.id:
            return False
        if self.name != other.name:
            return False
        return True
        
    def persist(self):
        with self.game.conn.cursor() as curs:
            if self.id is not None:
                curs.execute('''UPDATE spell SET name = %s
                                WHERE id = %s''',
                    (self.name, self.id))
            else:
                curs.execute('''INSERT INTO spell (name)
                                VALUES (%s) RETURNING id''',
                    (self.name,))
                self.id = curs.fetchone()[0]
            curs.connection.commit()
        return self

    @classmethod
    def lookup(cls, sid=None, name=None):
        if not sid and not sub:
            return None
        (all_isids, all_names) = (False, False)
        if not sid:
            all_sids = True
        if not name:
            all_names = True
        with cls.game.conn.cursor() as curs:
            curs.execute('''SELECT id, name FROM spell WHERE
                            (id = %s OR %s) AND
                            (name = %s OR %s)
                            ''', (sid, all_sids, name, all_names))
            try:
                return cls(*curs.fetchone())
            except TypeError:
                return cls(name=name).persist()

# vim: autoindent textwidth=100 tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
