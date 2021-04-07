from taxbot import TaxBot

bot = TaxBot('R07112-007-008-000', '37129', local=True)
print(bot.process_form())