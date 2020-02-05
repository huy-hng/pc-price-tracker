import time
import json

import requests
from flask import Flask, request, jsonify, render_template, redirect
from concurrent.futures import ThreadPoolExecutor

import headless_driver


app = Flask(__name__)


@app.route('/')
def home():
  return render_template('layout.html')

#region ################ prices ################
@app.route('/prices')
def prices():
  prices, total = get_all_prices()
  group_prices = get_group_price(prices)
  return render_template('prices.html',
                          prices=prices,
                          prices_total=total,
                          group_prices=group_prices)

def get_all_prices():
  products = get_json('products')
  links = products['links']
  thresholds = products['single_products']
  prices = {}
  total = 0
  for name, link in links.items():
    price = get_price(link)
    product_detail = {}
    product_detail['price'] = price
    product_detail['threshold'] = prettify_price(thresholds[name])

    prices[name] = product_detail
    total += float(price[:-1])

  return prices, prettify_price(total)


def get_price(link):
  text = headless_driver.get(link)
  elem = headless_driver.get_element(text, '//*[@id="priceCol"]/span/span[3]')
  num = headless_driver.get_attribute(elem, 'content')
  return prettify_price(num)


def get_group_price(prices):
  group_prices = {}
  products = get_json('products')
  groups = products['groups']
  for group in groups:
    total = 0

    for product in group['products']:
      total += float(prices[product]['price'][:-1])

    group_detail = {}
    group_detail['price'] = prettify_price(round(total, 2))
    group_detail['threshold'] = prettify_price(group['threshold'])

    group_prices[group['name']] = group_detail
  return group_prices
#endregion


#region ################ notifications ################
@app.route('/periodic_checker')
def periodic_checker():
  while True:

    prices, total = get_all_prices()
    group_prices = get_group_price(prices)

    for name, group in group_prices.items():
      if group['price'] < group['threshold']:
        # send_notification(name, group['price'], group['threshold'])
        pass
  
    time.sleep(0.2)

    settings = get_json('settings')
    if not settings['notifications']:
      break

    print('periodic_checker running')

  return render_template('settings.html', state=settings['notifications'])
#endregion


#region ################ settings ################
@app.route('/settings')
def notify():
  settings = get_json('settings')
  return render_template('settings.html', state=settings['notifications'])

@app.route('/toggle_notifications')
def toggle_notifications():
  settings = get_json('settings')
  settings['notifications'] = not settings['notifications']
  set_settings('settings', settings)
  print('Notifications:', settings['notifications'])

  if settings['notifications']:
    redirect('/periodic_checker', code=302)
  
  return render_template('settings.html', state=settings['notifications'])
#endregion


#region ################ helper ################
def prettify_price(price):
  price = str(price).split('.')
  if len(price) > 1:
    price = f'{price[0]}.{price[1].ljust(2, "0")}€'
  else:
    price = f'{price[0]}€'
    
  return price


def prettify_prices(prices):
  for name, price in prices.items():
    price = prettify_price(price)
    prices[name] = price
  return prices


def send_notification(name, price, threshold):
  requests.post('https://maker.ifttt.com/trigger/price_alert/with/key/QqsEN4DAuAPNDhPwNgVbG',
      {'value1': name, 'value2': price, 'value3': threshold})
#endregion


#region ################ json ################
def get_json(name):
  with open(f'{name}.json') as f:
    return json.load(f)

def set_settings(name, obj):
  with open(f'{name}.json', 'w') as f:
    f.write(json.dumps(obj))
#endregion

if __name__ == '__main__':
  app.run(debug=True, port=80)