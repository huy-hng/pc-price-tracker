import time
import json

import requests
from flask import Flask, request, jsonify, render_template, redirect
from concurrent.futures import ThreadPoolExecutor
from threading import Thread


import headless_driver


app = Flask(__name__)
periodic_checker_running = False

@app.route('/')
def home():
  if not periodic_checker_running:
    start_periodic_checker()
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


def get_price(link):
  text = headless_driver.get(link)
  elem = headless_driver.get_element(text, '//*[@id="priceCol"]/span/span[3]')
  num = headless_driver.get_attribute(elem, 'content')
  return prettify_price(num)


def get_all_prices():
  """ 
  prices = {
    CPU: {
      price: 100,
      threshold: 90
    },
    ...
  }
  """
  products = get_json('products')
  links = products['links']
  single_products = products['single_products']

  prices = {}
  total_price = 0
  total_threshold = 0

  for product in single_products:
    link = links[product['name']]
    name = product['name']

    price = get_price(link)
    product_detail = {}
    product_detail['price'] = price
    product_detail['threshold'] = prettify_price(product['threshold'])
    prices[name] = product_detail


    total_price += float(price[:-1])
    total_threshold += product['threshold']

  total = {
    'price': prettify_price(total_price),
    'threshold': prettify_price(total_threshold)
  }

  return prices, total


def get_group_price(prices):
  group_prices = {}
  products = get_json('products')
  groups = products['groups']
  for group in groups:
    price = 0
    threshold = 0

    for product in group['products']:
      price += float(prices[product]['price'][:-1])
      threshold += float(prices[product]['threshold'][:-1])

    group_detail = {}
    group_detail['price'] = prettify_price(round(price, 2))
    group_detail['threshold'] = prettify_price(int(round(threshold)))

    group_prices[group['name']] = group_detail
  return group_prices
#endregion


#region ################ notifications ################
def start_periodic_checker():
  thread = Thread(target=periodic_checker)
  thread.daemon = True
  thread.start()

def periodic_checker():
  periodic_checker_running = True
  while get_json('settings')['notifications']:

    prices, total = get_all_prices()
    group_prices = get_group_price(prices)

    for name, group in group_prices.items():
      if group['price'] < group['threshold']:
        send_notification(name, group['price'], group['threshold'])
        pass
  
    time.sleep(600)
  periodic_checker_running = False
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

  if settings['notifications'] and not periodic_checker_running:
    start_periodic_checker()

  return redirect('/settings')
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