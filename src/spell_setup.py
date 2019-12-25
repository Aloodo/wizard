#!/usr/bin/env python3

import logging

# Add spells here. Needs to be in sync with manifest.json in "extension"

def spell_setup(game):
    game.spell(name="scry",
               url="https://blog.zgp.org/opt-out-success/").persist()

# vim: autoindent textwidth=100 tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python

