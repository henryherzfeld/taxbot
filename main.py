import pandas as pd
from taxbot import TaxBot
import json
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='taxbot.log', level=logging.DEBUG)

with open("test.json") as f:
    pids = json.loads(f.read())

results = {}
for entry in pids:
    pid = entry['pid']
    fips = entry['fips']

    bot = TaxBot(pid, fips, verbosity=1)

    results[pid] = bot.process_form()

    # if bot.success:
    #     # send home cookies
    # else:
    #     don't take results, report it'

json_str = json.dumps(results)
with open('out.json', 'w') as f:
    f.write(json_str)
