from taxbot import TaxBot

bot = TaxBot('R05707-002-031-000', '37129', local=True)
print(bot.process_form())