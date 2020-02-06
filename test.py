import json 

def get_json(name):
  with open(f'{name}.json') as f:
    return json.load(f)

products = get_json('products')
for product in products['single_products']:
  product['lowest'] = 5
  
print(products)