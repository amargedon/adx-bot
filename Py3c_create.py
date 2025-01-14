import ccxt
import time
import math
import config
import os
from time import gmtime, strftime
from py3cw.request import Py3CW
from pathlib import Path

p3cw = Py3CW(
    key=config.TC_API_KEY,
    secret=config.TC_API_SECRET,
    request_options={
        'request_timeout': 20,
        'nr_of_retries': 10,
        'retry_status_codes': [500, 502, 503, 504]
    }
)

if config.EXCHANGE == 'FTX':
    exchange = ccxt.ftx({
        'apiKey': config.API_KEY,
        'secret': config.SECRET_KEY,
        'headers': {'FTX-SUBACCOUNT': config.SUB_ACCOUNT}
    })
elif config.EXCHANGE == 'BINANCE':
    exchange = ccxt.binance({
        'apiKey': config.API_KEY,
        'secret': config.SECRET_KEY
    })

def get_markets():
    all_markets = exchange.load_markets(True)
    return all_markets


## Works on 3.9.5 - Use versions below for 3.9.2
##def build_tc_pairs_list(pairs):
##    tc_pairs = {}
##    for key in markets:
##        print(key)
##        if "PERP" in key and not any(perp in key for perp in config.PAIRS_BLACKLIST):
##            tc_pairs[key] = ""
##    return tc_pairs
##
##def get_min_order_price(markets):
##    limits = {}
##    for key in markets:
##        if "PERP" in key and not any(perp in key for perp in config.PAIRS_BLACKLIST):
##            if "minProvideSize" in markets[key]["info"]:
##                limits[key] = math.ceil(float(markets[key]["info"]["minProvideSize"]) * float(markets[key]["info"]["price"]))
##    return limits


def build_tc_pairs_list(pairs):
    tc_pairs = {}
    for key in markets:
	if config.LEVERAGE_CUSTOM_VALUE:
		if "PERP" in markets[key]["id"] and not any(perp in markets[key]["id"] for perp in config.PAIRS_BLACKLIST):
		    tc_pairs[markets[key]["id"]] = ""
	else:
		if not any(x in markets[key]["id"] for x in ["BULL", "BEAR", "HALF", "HEDGE"]) and markets[key]["type"] == "spot" and markets[key]["quote"] == config.QUOTE:
		     if markets[key]["base"] in config.SPOT_COINS:
		          tc_pairs[markets[key]["id"]] = f'{markets[key]["quote"]}_{markets[key]["base"]}'
    return tc_pairs


def get_min_order_price(markets):
    limits = {}
    for key in markets:
	if config.LEVERAGE_CUSTOM_VALUE:
		if "PERP" in markets[key]["id"] and not any(perp in markets[key]["id"] for perp in config.PAIRS_BLACKLIST):
		    if "minProvideSize" in markets[key]["info"]:
		        limits[markets[key]["id"]] = math.ceil(float(markets[key]["info"]["minProvideSize"]) * float(markets[key]["info"]["price"]))
	else:
		if not any(x in markets[key]["id"] for x in ["BULL", "BEAR", "HALF", "HEDGE"]) and markets[key]["type"] == "spot" and markets[key]["quote"] == config.QUOTE:
		    if "minProvideSize" in markets[key]["info"]:
		        limits[markets[key]["id"]] = math.ceil(float(markets[key]["info"]["minProvideSize"]) * float(markets[key]["info"]["price"]))
    return limits

def generate_long_bots(pairs, minprice):
    bot_list = {}
    order_too_low = []
    for key in pairs:
        if config.BASE_ORDER_VOLUME > minprice[key]:
            #print(key)
            error, data = p3cw.request(
                entity='bots',
                action='create_bot',
                additional_headers={"Forced-Mode": config.TC_MODE},
                payload={
                "name": config.LONG_PREFIX + key,
                "account_id": config.TC_ACCOUNT_ID,
                "pairs": pairs[key],
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
                "leverage_type": "cross" if config.LEVERAGE_CUSTOM_VALUE > 0 else "not_specified",
                "leverage_custom_value": config.LEVERAGE_CUSTOM_VALUE,
                "start_order_type": config.START_ORDER_TYPE,
                "stop_loss_type": "stop_loss",
                "strategy": "long",
                "min_volume_btc_24h": config.MIN_VOLUME,
                "trailing_enabled": "yes" if config.TRAILING else "no",
                "trailing_deviation": config.TRAILING_DEVIATION
                }
            )
            if len(error) > 0:
                print(f'{key} Error: {error}')
                continue
            bot_list[key] = data["id"]
            print(f'{key}  > {bot_list[key]}')
            time.sleep(0.1)
            f = open("lbotid_list.txt", "a")
            f.write(f'{key}:{bot_list[key]}\n')
            f.close()
        else:
            print(f'Order volume too low for {key}, bot not created')
            order_too_low.append(key)
    print(f'The following long pairs were ignored, order volume too low: {order_too_low}')
    file = open("ignored_longs.txt", "w")
    for element in order_too_low:
        file.write(element + "\n")
    file.close()
    return bot_list, order_too_low

def generate_short_bots(pairs, minprice):
    bot_list = {}
    order_too_low = []
    for key in pairs:
        if config.BASE_ORDER_VOLUME > minprice[key]:
            error, data = p3cw.request(
                entity='bots',
                action='create_bot',
                additional_headers={"Forced-Mode": config.TC_MODE},
                payload={
                "name": config.SHORT_PREFIX + key,
                "account_id": config.TC_ACCOUNT_ID,
                "pairs": pairs[key],
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
                "leverage_type": "cross" if config.LEVERAGE_CUSTOM_VALUE > 0 else "not_specified",,
                "leverage_custom_value": config.LEVERAGE_CUSTOM_VALUE,
                "start_order_type": config.START_ORDER_TYPE,
                "stop_loss_type": "stop_loss",
                "strategy": "short",
                "min_volume_btc_24h": config.MIN_VOLUME,
                "trailing_enabled": "yes" if config.TRAILING else "no",
                "trailing_deviation": config.TRAILING_DEVIATION
                }
            )
            if len(error) > 0:
                print(f'{key} Error: {error}')
                continue
            bot_list[key] = data["id"]
            print(f'{key}  > {bot_list[key]}')
            time.sleep(0.1)
            f = open("sbotid_list.txt", "a")
            f.write(f'{key}:{bot_list[key]}\n')
            f.close()
        else:
            print(f'Order volume too low for {key}, bot not created')
            order_too_low.append(key)
    print(f'The following short pairs were ignored, order volume too low: {order_too_low}')
    file = open("ignored_shorts.txt", "w")
    for element in order_too_low:
        file.write(element + "\n")
    file.close()
    return bot_list, order_too_low

def build_bots():
    global markets
    markets = get_markets()
    pairs_list = build_tc_pairs_list(markets)
    min_price = get_min_order_price(markets)
    longbot_list, no_long_bots = generate_long_bots(pairs_list, min_price)
    shortbot_list, no_short_bots = generate_short_bots(pairs_list, min_price)
    #add list of too low order value pairs to a file.
    print(f'{len(longbot_list)} long bots created.')
    print(f'{len(no_long_bots)} pairs ignored, order amount to low')
    print(f'{len(shortbot_list)} short bots created.')
    print(f'{len(no_short_bots)} pairs ignored, order amount to low')
    print("Ignored pairs can be found in ignored_longs.txt and ignored_shorts.txt")


longbots_file = Path("lbotid_list.txt")
shortbots_file = Path("sbotid_list.txt")
if longbots_file.is_file() or shortbots_file.is_file():
    print("An existing bot ID list was found. Using this option will over-write this list. Are you sure? y/n")
    x = input()
    if x != "y":
        print("Bye!")
    else:
        print("over-writing in progress...")
        if longbots_file.is_file(): os.remove("lbotid_list.txt")
        if longbots_file.is_file(): os.remove("sbotid_list.txt")
        build_bots()

else:
    print("no existing bot ID files found, proceeding....")
    build_bots()

print("All done, have a nice day!")
