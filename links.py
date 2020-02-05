import requests
import headless_driver

xpath = '//*[@id="priceCol"]/span/span[3]'

cpu = 'https://www.mindfactory.de/product_info.php/AMD-Ryzen-5-2600-6x-3-40GHz-So-AM4-BOX_1233732.html'
mainboard = 'https://www.mindfactory.de/product_info.php/ASRock-B450M-Pro4-AMD-B450-So-AM4-Dual-Channel-DDR4-mATX-Retail_1267179.html'

cooler = 'https://www.mindfactory.de/product_info.php/EKL-Alpenfoehn-Brocken-3-Tower-Kuehler_1188580.html'
ssd = 'https://www.mindfactory.de/product_info.php/1000GB-Crucial-P1-NVMe-M-2-2280-PCIe-3-0-x4-32Gb-s-3D-NAND-QLC--CT1000P_1280845.html'
tower = 'https://www.mindfactory.de/product_info.php/be-quiet--Pure-Base-600-gedaemmt-Midi-Tower-ohne-Netzteil-schwarz_1137067.html'

power_supply = 'https://www.mindfactory.de/product_info.php/400-Watt-be-quiet--Pure-Power-11-Non-Modular-80--Gold_1281114.html'
gpu = 'https://www.mindfactory.de/product_info.php/4GB-Gigabyte-GeForce-GTX-1650-Windforce-OC-4G-Aktiv-PCIe-3-0-x16--Retai_1306218.html'

all_links = {
    'cpu': cpu,
    'mainboard': mainboard,
    'cooler': cooler,
    'ssd': ssd,
    'tower': tower,
    'power_supply': power_supply,
    'gpu': gpu
}

groups = {
  'CPU and Mainboard': {
    'links': [cpu, mainboard],
    'threshold': 200
  },
  'GPU and Powersupply': {
    'links': [gpu, power_supply],
    'threshold': 220
  }
}

def get_price(link):
  text = headless_driver.get(link)
  elem = headless_driver.get_element(text, xpath)
  return float(headless_driver.get_attribute(elem, 'content'))


def get_all_prices():
  for name, link in all_links.items():
    print(name, get_price(link))
  # requests.get('https://maker.ifttt.com/trigger/price_alert/with/key/QqsEN4DAuAPNDhPwNgVbG')

def get_group_price():
  for name, group in groups.items():
    sum = 0
    for link in group['links']:
      sum += get_price(link)
    if sum <= group['threshold']:
      requests.post('https://maker.ifttt.com/trigger/price_alert/with/key/QqsEN4DAuAPNDhPwNgVbG',
          {'value1': name, 'value2': sum})


if __name__ == '__main__':
  get_group_price()