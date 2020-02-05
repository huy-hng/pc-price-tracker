import requests
from lxml import html




def get(url=None):
  text = get_text(url)
  return parse_from_string(text)

def get_element(page, xpath: str):
  return page.xpath(xpath)[0]

def get_elements(page, xpath: str):
  return page.xpath(xpath)

def get_attribute(elem, attrib: str):
  return elem.attrib.get(attrib)

def get_attributes(elements, attrib: str):
  attributes = [elem.attrib.get(attrib) for elem in elements]
  return attributes


def parse_from_string(html_content):
  return html.fromstring(html_content)

def get_text(url):
  response = requests.get(url)
  return response.text