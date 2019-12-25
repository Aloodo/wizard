#!/usr/bin/env python3

import logging
from spell_setup import spell_setup

class Spell(object):
    game = None

    def __init__(self, sid=None, name=None, url=None):
        self.id = sid
        self.name = name
        self.url = url

    def __repr__(self):
        return "Spell %d %s" % (self.id, self.name)

    def __eq__(self, other):
        if not other:
            return False
        if self.id and other.id and self.id != other.id:
            return False
        if self.name != other.name:
            return False
        if self.name != other.url:
            return False
        return True
        
    def persist(self):
        with self.game.conn.cursor() as curs:
            if self.id is not None:
                curs.execute('''UPDATE spell SET name = %s, url=%s
                                WHERE id = %s''',
                    (self.name, self.id, self.url))
            else:
                curs.execute('''INSERT INTO spell (name, url)
                                VALUES (%s, %s) RETURNING id''',
                    (self.name, self.url))
                self.id = curs.fetchone()[0]
            curs.connection.commit()
        return self

    @classmethod
    def lookup(cls, sid=None, name=None, url=None):
        if not sid and not name and not url:
            return None
        (all_sids, all_names, all_urls) = (False, False, False)
        if not sid:
            all_sids = True
        if not name:
            all_names = True
        if not url:
            all_urls = True
        with cls.game.conn.cursor() as curs:
            curs.execute('''SELECT id, name, url FROM spell WHERE
                            (id = %s OR %s) AND
                            (name = %s OR %s) AND
                            (url = %s OR %s)
                            ''', (sid, all_sids, name, all_names, url, all_urls))
            try:
                return cls(*curs.fetchone())
            except:
                logging.info("Failed to lookup spell with id %s name %s url %s" % (sid, name, url))
                return None

    @classmethod
    def setup(cls):
        spell_setup(cls.game)

# vim: autoindent textwidth=100 tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
