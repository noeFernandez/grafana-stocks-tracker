from time import sleep
import yfinance as yf  
import yaml
import graphyte

config_path = '/config/.stocktracker.yml'

def get_portfolio_currency():
    return get_config()['portfolio_currency']

def get_config():
    with open(config_path) as f:#fix path to home
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config

def get_exchange_rate(asset_currency):
    portfolio_currency = get_config()['portfolio_currency']
    if (portfolio_currency == asset_currency):
        return 1
    else:
        return yf.Ticker(f'{asset_currency}{portfolio_currency}=X').info['regularMarketPrice']

def get_exchange_rate_at_date(date, asset_currency):
    if (asset_currency != get_portfolio_currency()):
        return yf.Ticker(f"{asset_currency}{get_portfolio_currency()}=X").history('1d', start=date, end=date)['Open'][0]
    else:
        return 1

def send_metric(asset_name, buy_date, property, value):
    graphyte.init(get_config()['graphite_host'], prefix=f'portfolio.stock.{asset_name}.{buy_date.replace("-", "")}')
    graphyte.send(property, value)
    print(f"[{asset_name}] Sent {property}: {value}")

def get_asset_price(asset_type, asset_info):
    if (asset_type == "stock"):
        return asset_info["ask"]
    else:
        return asset_info['regularMarketPrice']

while(True):
    config = get_config()
    for ticker in config['holds']:
        for purchase in ticker['buys']:
            amount_stock = purchase['amount']
            buy_date = purchase['date']
            
            company_info = yf.Ticker(ticker['ticker']).info
            currency = company_info["currency"]
            exchange_rate = get_exchange_rate(currency)
            ask = get_asset_price(ticker['type'], company_info)           

            value_at_day_bought = (purchase['price'] * amount_stock) * get_exchange_rate_at_date(buy_date, currency)
            value_now = (ask * exchange_rate) * amount_stock

            send_metric(ticker['name'], buy_date, 'current_price', ask * exchange_rate)
            send_metric(ticker['name'], buy_date, 'amount', amount_stock)
            send_metric(ticker['name'], buy_date, 'asset_valuation', value_now)
            send_metric(ticker['name'], buy_date, 'buy_price', value_at_day_bought)
            send_metric(ticker['name'], buy_date, 'gain_loss', (value_now - value_at_day_bought))
    sleep(config['frequency'])