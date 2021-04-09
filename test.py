from taxbot import TaxBot

pid = str(input("enter pid: "))
fips = str(input("enter fips: "))

bot = TaxBot(pid, fips, local=True, verbosity=1)
print(bot.process_form())
