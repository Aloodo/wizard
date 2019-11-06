import logging
import tweepy

from game import Game

logging.basicConfig(level=logging.DEBUG)
logging.info("Bot started.")
logging.debug("Logging at DEBUG level.")

start_demo_db = False

game = Game(start_demo_db=start_demo_db)
logging.debug("Game connected.")
game.stop_demo_db()

# vim: autoindent textwidth=100 tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python

