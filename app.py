import time

import requests

import headless_driver
from links import links, groups


from flask import Flask, request, jsonify, render_template
from links import groups

app = Flask(__name__)


#region ################ routes ################
@app.route('/')
def home():
  prices, total = get_all_prices()
  group_prices = get_group_price(prices)
  return render_template('home.html',
                          prices=prettify_prices(prices),
                          prices_total=total,
                          group_prices=prettify_prices(group_prices))


#endregion

#region ################ prices ################
def get_all_prices():
  prices = {}
  total = 0
  for name, link in links.items():
    price = get_price(link)
    prices[name] = price
    total += price

  return prices, total


def get_price(link):
  text = headless_driver.get(link)
  elem = headless_driver.get_element(text, '//*[@id="priceCol"]/span/span[3]')
  return float(headless_driver.get_attribute(elem, 'content'))


def get_group_price(prices):
  group_prices = {}
  for group in groups:
    total = 0

    for product in group['products']:
      total += prices[product]

    # if total <= group['threshold']:
    #   send_notification(group['name'], prettify_price(total))

    group_prices[group['name']] = total

  return group_prices
#endregion


#region ################ helper ################
def prettify_price(price):
  price = str(price).split('.')   
  price = f'{price[0]}.{price[1].ljust(2, "0")}€'
  return price


def prettify_prices(prices):
  for name, price in prices.items():
    price = str(price).split('.')   
    price = f'{price[0]}.{price[1].ljust(2, "0")}€'
    prices[name] = price
  return prices


def send_notification(name, price):
  requests.post('https://maker.ifttt.com/trigger/price_alert/with/key/QqsEN4DAuAPNDhPwNgVbG',
      {'value1': name, 'value2': price})
#endregion



if __name__ == '__main__':
  app.run(debug=True, port=80)