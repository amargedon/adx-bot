import time
import config
from py3cw.request import Py3CW
from pathlib import Path

p3cw = Py3CW(
    key=config.TC_API_KEY,
    secret=config.TC_API_SECRET,
    request_options={
        'request_timeout': 30,
        'nr_of_retries': 1,
        'retry_status_codes': [502]
    }
)


def update_bots(pairs, strategy):
    if strategy == "long":
        pre_name = "LongPy_"
    elif strategy == "short":
        pre_name = "ShortPy_"
    for key in pairs:
        bot_id = pairs[key]
        error, data = p3cw.request(
            entity='bots',
            action='update',
            action_id = bot_id,
            payload={
            "name": pre_name+key,
            #"account_id": config.TC_ACCOUNT_ID,
            "pairs": "USD_"+key,
            "base_order_volume": config.BASE_ORDER_VOLUME,
            "base_order_volume_type": "quote_currency",
            "take_profit": config.TAKE_PROFIT,
            "safety_order_volume": config.SAFETY_ORDER_VOLUME,
            "safety_order_volume_type": "quote_currency",
            "martingale_volume_coefficient": config.MARTINGALE_VOLUME_COEFFICIENT,
            "martingale_step_coefficient": config.MARTINGALE_STEP_COEFFICIENT,
            "max_safety_orders": config.MAX_SAFETY_ORERS,
            "active_safety_orders_count": config.ACTIVE_SAFETY_ORDERS_COUNT,
            "safety_order_step_percentage": config.SAFETY_ORDER_STEP_PERCENTAGE,
            "take_profit_type": "total",
            "strategy_list": [{"strategy":"nonstop"}],
            "leverage_type": "cross",
            "leverage_custom_value": config.LEVERAGE_CUSTOM_VALUE,
            "start_order_type": config.START_ORDER_TYPE,
            "stop_loss_percentage": config.STOP_LOSS_PERCENTAGE,
            "stop_loss_type": config.STOP_LOSS_TYPE,
            "stop_loss_timeout_enabled": config.STOP_LOSS_TIMEOUT_ENABLED,
            "stop_loss_timeout_in_seconds": config.STOP_LOSS_TIMEOUT_IN_SECONDS,
            #"strategy": "long"
            "bot_id": bot_id
            }
        )
        if len(error) > 0:
            print(f'{key} Error: {error}')
            continue
        #bot_list[key] = data["id"]
        print(f'{pre_name+key} > updated')
        time.sleep(0.1)

def enable_bots(pairs):
    for key in pairs:
        bot_id = pairs[key]
        error, data = p3cw.request(
            entity='bots',
            action='enable',
            action_id = bot_id,
        )
        print(f'Error: {error}')
        #bot_list[key] = data["id"]
        print(f'LongPy_{key} > enabled')
        time.sleep(0.5)

def disable_bots(pairs):
    for key in pairs:
        bot_id = pairs[key]
        error, data = p3cw.request(
            entity='bots',
            action='enable',
            action_id = bot_id,
        )
        print(f'Error: {error}')
        #bot_list[key] = data["id"]
        print(f'ShortPy_{key} > disabled')
        time.sleep(0.5)

def delete_bots(pairs):
    for key in pairs:
        bot_id = pairs[key]
        print(f'Delete: {key} - {bot_id}')
        error, data = p3cw.request(
            entity='bots',
            action='delete',
            action_id = bot_id,
        )
        if len(error) > 0:
            print(f'Error: {error}')
        time.sleep(0.5)

def load_bot_ids(filename):
    d = {}
    with open(filename) as f:
        for line in f:
            (key, val) = line.split(':')
            d[key] = val.rstrip('\n')
    return d

long_bot_ids = {}
short_bot_ids = {}

longbots_file = Path("lbotid_list.txt")
shortbots_file = Path("sbotid_list.txt")
if longbots_file.is_file() or shortbots_file.is_file():
    print("Loading bot ID files...")
    long_bot_ids = load_bot_ids("lbotid_list.txt")
    short_bot_ids = load_bot_ids("sbotid_list.txt")
    print("Done.")
    print("----")
    print("Choose your option:")
    print("1 - Update bot parameters")
    print("2 - Enable all bots - disabled")
    print("3 - Disable all bots - disabled")
    print("4 - Check for new pairs and add to list - does nothing, yet!")
    print("9 - Delete all bots !!")
    x = input()
    if x == "1":
        print("Updating bots....")
        update_bots(long_bot_ids, "long")
        update_bots(short_bot_ids, "short")
    elif x == "2":
        print("Enabling all bots...")
        #enable_bots(long_bot_ids)
        #enable_bots(short_bot_ids)
        pass
    elif x == "3":
        print("Disabling all bots...")
        #disable_bots(long_bot_ids)
        #disable_bots(short_bot_ids)
        pass
    elif x == "4":
        print("Looking for new pairs...")
        #  need to write a function to do this
        #  Load existing bot lists into memory.  Prolly only need longs since they are mirrored.
        #  Use "load_bot_ids" function from triggers
        #  Use get_markets function to load existing markets, less blacklists
        #  Look through each key in bot id list, and pop those that match
        #  Check remaining list for > 0 length.
        #  Run generate_long_bots (and short) to create bots - still check min price - and add to bot_id files
        #  Run bot update to make sure new bots have same settings.
        pass
    elif x == "9":
        print("Delete all bots...")
        delete_bots(long_bot_ids)
        delete_bots(short_bot_ids)
        longbots_file.unlink()
        shortbots_file.unlink()
    else:
        print("Choose only the numbers 1, 2, 3, 4, or 9. Try harder next time!")
        
else:
    print("No existing bot ID files found, can't perform this task. Create some bots first.")

print("All done, have a nice day!")
