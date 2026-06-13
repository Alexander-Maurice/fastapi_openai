import requests
from lxml import etree
from bs4 import BeautifulSoup

url = 'https://muzlider.ru/bitrix/catalog_export/image_checker.php'
data = requests.get(url)

tree = etree.fromstring(data.content)

guitars_data = ''

for elem in tree:
    title = elem.xpath('Title')[0].text
    guitars_data += f'Название: {title}'
    guitars_data += '\n'

    typ = elem.xpath('GoodsType')[0].text
    guitars_data += f'Тип: {typ}'
    guitars_data += '\n'

    description = elem.xpath('Description')[0].text
    guitars_data += f'Описание: {description}'
    guitars_data += '\n'

    price = elem.xpath('Price')[0].text
    guitars_data += f'Цена: {price}'
    guitars_data += '\n' * 3

    # between_data = dict()
    # between_data['Название'] =
    # between_data['Тип'] = elem.xpath('GoodsType')[0].text
    # between_data['Описание'] = elem.xpath('Description')[0].text
    # between_data['Цена'] = elem.xpath('Price')[0].text
    # guitars_data += str(between_data)
    # guitars_data += '\n' * 3


with open('data/guitars_data.txt', 'a') as f:
    f.write(guitars_data)


