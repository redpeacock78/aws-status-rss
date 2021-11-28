import requests
import xml.dom.minidom
from bs4 import BeautifulSoup
from bs4.element import CData
from flask import Flask, Response
from datetime import datetime, timezone, timedelta

rss_template = ('<?xml version="1.0" encoding="UTF-8"?>'
                '<rss version="2.0">'
                '  <channel>'
                '    <title><![CDATA[AWS Service Status]]></title>'
                '    <link>http://status.aws.amazon.com/</link>'
                '    <description><![CDATA[AWS Service Status]]></description>'
                '  </channel>'
                '</rss>'
                )

item_template = ('<item>'
                 '    <title></title>'
                 '    <link>http://status.aws.amazon.com/</link>'
                 '    <pubDate></pubDate>'
                 '    <guid isPermaLink="false"></guid>'
                 '    <description></description>'
                 '    <category></category>'
                 '</item>')

def main():
    soup = BeautifulSoup(rss_template, 'xml')

    r = requests.get('https://status.aws.amazon.com/data.json')
    json = r.json()

    JST = timezone(timedelta(hours=+9), 'JST')

    for item in json['archive']:
        title = item['summary']
        pubDate = item['date']
        pubDate = datetime.fromtimestamp(int(item['date']),JST).strftime('%a, %d %b %Y %H:%M:%S %Z')
        guid = item['service'] + item['date']
        description = item['description']
        category = item['service_name']

        item = BeautifulSoup(item_template, 'xml')
        item.title.append(title)
        item.pubDate.append(pubDate)
        item.guid.append(guid)
        item.description.append(CData(description))
        item.category.append(category)

        soup.find('channel').append(item)

    return str(soup)


app = Flask(__name__)

@app.route('/')
def index():
  dom = xml.dom.minidom.parseString(main())
  response = Response('\n'.join(filter(lambda x: x.strip(), dom.toprettyxml(indent="  ").split('\n'))))
  response.headers['Content-Type'] = "application/xml; charset=utf-8"
  return response

app.run(host='0.0.0.0', port=8080)
