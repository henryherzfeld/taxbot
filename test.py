from taxbot import TaxBot
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--pid', type=str, help="the pid you are using")
parser.add_argument('-f', '--fips', type=str, help="the county fips code you are using")

args = parser.parse_args()

pid = args.pid
fips = args.fips

if not pid:
    pid = str(input("enter pid: "))

if not fips:
    fips = str(input("enter fips: "))

bot = TaxBot(pid, fips, local=True, verbosity=1)
print(bot.process_form())
