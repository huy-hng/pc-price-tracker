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
  return render_template('layout.html')

@app.route('/products_json')
def get_products_json():
  with open(f'products.json') as f:
    return f.read()


#region ################ prices ################
@app.route('/prices')
def prices():
  prices, total = get_all_prices()
  groups = get_group_price()
  pretty_prices = prettify_prices(prices)
  pretty_groups = prettify_prices(groups)

  return render_template('prices.html', prices=pretty_prices, 
      prices_total=total, groups=pretty_groups)


def get_price(link):
  text = headless_driver.get(link)
  try:
    elem = headless_driver.get_element(text, '//*[@id="priceCol"]/span/span[3]')
    num = headless_driver.get_attribute(elem, 'content')
    return round(float(num), 2)
  except Exception as e:
    print(link)
    print(e)

  return -1
    


def get_all_prices():
  """ 
  prices = {
    CPU: {
      price: 100,
      threshold: 90,
      lowest: 99
    },
    ...
  }
  """
  products = get_json('products')

  total_price = 0
  total_threshold = 0
  total_lowest = 0

  for product in products['single_products']:
    link = products['links'][product['name']]
    name = product['name']

    price = get_price(link)
    # if name == 'CPU': price = round(product['lowest'] * 0.99, 2)
    if price == -1:
      price = product['price']
    else:
      product['price'] = price
      if price < product['lowest']:
        product['lowest'] = price

    total_price += price
    total_threshold += product['threshold']
    total_lowest += product['lowest']

  set_json('products', products)

  total = {
    'price': prettify_price(total_price),
    'threshold': prettify_price(total_threshold),
    'lowest': prettify_price(total_lowest)
  }

  return products['single_products'], total


def get_group_price():
  products = get_json('products')
  groups = products['groups']
  single_products = products['single_products']
  for group in groups:
    group_price = 0
    threshold = 0
    lowest = 0

    for product in group['products']:

      single_product = None
      for prod in single_products:
        if prod['name'] == product:
          single_product = prod

      group_price += single_product['price']
      threshold += single_product['threshold']
      lowest += single_product['lowest']

    if group_price < group['lowest']:
      send_notification('price_drop', group['name'], prettify_price(group['lowest']), prettify_price(group_price))

    if group_price < threshold:
      send_notification('price_alert', group['name'], prettify_price(group['price']), prettify_price(group['threshold']))

    group['price'] = round(group_price, 2)
    group['threshold'] = round(threshold, 2)
    group['lowest'] = round(lowest, 2)

  set_json('products', products)

  return groups
#endregion


#region ################ notifications ################
def start_periodic_checker():
  thread = Thread(target=periodic_checker)
  thread.daemon = True
  thread.start()


def periodic_checker():
  global periodic_checker_running
  if periodic_checker_running: return

  periodic_checker_running = True
  while get_json('settings')['notifications']:

    get_all_prices()
    get_group_price()
    time.sleep(3600)

  periodic_checker_running = False


def send_notification(endpoint, val1, val2, val3):
  requests.post(f'https://maker.ifttt.com/trigger/{endpoint}/with/key/QqsEN4DAuAPNDhPwNgVbG',
      {'value1': val1, 'value2': val2, 'value3': val3})
  print('Notification sent!', endpoint, val1, val2, val3)
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
  set_json('settings', settings)
  print('Notifications:', settings['notifications'])

  if settings['notifications'] and not periodic_checker_running:
    start_periodic_checker()

  return redirect('/settings')
#endregion


#region ################ helper ################
def prettify_price(price: float):
  price = round(price, 2)
  price = str(price).split('.')
  if len(price) > 1:
    price = f'{price[0]}.{price[1].ljust(2, "0")}€'
  else:
    price = f'{price[0]}€'
    
  return price

def prettify_prices(price_list):
  for item in price_list:
    item['threshold'] = prettify_price(item['threshold'])
    item['lowest'] = prettify_price(item['lowest'])
    item['price'] = prettify_price(item['price'])

  return price_list
#endregion


#region ################ json ################
def get_json(name) -> dict:
  with open(f'{name}.json') as f:
    return json.load(f)

def set_json(name, dictionary):
  with open(f'{name}.json', 'w') as f:
    f.write(json.dumps(dictionary))
#endregion
