"""Main entry point for Divination bot"""
from controllers.bot import BotController


if __name__ == "__main__":
    bot = BotController()
    bot.run()
