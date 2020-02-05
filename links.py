cpu = 'https://www.mindfactory.de/product_info.php/AMD-Ryzen-5-2600-6x-3-40GHz-So-AM4-BOX_1233732.html'
mainboard = 'https://www.mindfactory.de/product_info.php/ASRock-B450M-Pro4-AMD-B450-So-AM4-Dual-Channel-DDR4-mATX-Retail_1267179.html'

cooler = 'https://www.mindfactory.de/product_info.php/EKL-Alpenfoehn-Brocken-3-Tower-Kuehler_1188580.html'
ssd = 'https://www.mindfactory.de/product_info.php/1000GB-Crucial-P1-NVMe-M-2-2280-PCIe-3-0-x4-32Gb-s-3D-NAND-QLC--CT1000P_1280845.html'
tower = 'https://www.mindfactory.de/product_info.php/be-quiet--Pure-Base-600-gedaemmt-Midi-Tower-ohne-Netzteil-schwarz_1137067.html'

power_supply = 'https://www.mindfactory.de/product_info.php/400-Watt-be-quiet--Pure-Power-11-Non-Modular-80--Gold_1281114.html'
gpu = 'https://www.mindfactory.de/product_info.php/4GB-Gigabyte-GeForce-GTX-1650-Windforce-OC-4G-Aktiv-PCIe-3-0-x16--Retai_1306218.html'

links = {
    'CPU': cpu,
    'Mainboard': mainboard,
    'CPU cooler': cooler,
    'SSD': ssd,
    'Tower': tower,
    'Power supply': power_supply,
    'GPU': gpu
}


groups = [
  {
    'name': 'CPU and Mainboard',
    'products': ['CPU', 'Mainboard'],
    'threshold': 200
  },
  { 
    'name': 'GPU and Powersupply',
    'products': ['GPU', 'Power supply'],
    'threshold': 220
  }
]