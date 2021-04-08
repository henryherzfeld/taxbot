from taxbot import TaxBot

pid = str(input("enter pid: "))

bot = TaxBot(pid, '37129', local=True, verbosity=1)
print(bot.process_form())
