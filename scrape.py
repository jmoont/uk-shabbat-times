#!/bin/python

from bs4 import BeautifulSoup
from flask import Flask
from datetime import datetime, timedelta
from slugify import slugify
import requests
import json
import sys

app = Flask(__name__)
shabbattimespage = 'https://www.theus.org.uk/shabbattimes'
festivaltimespage = 'https://www.theus.org.uk/article/festival-fast-times'


@app.route('/')
def hello():
    return '<h2>UK Shabbat Times - theus.org.uk</h2><ul><li><a href="/shabbat_times">Shabbat Times JSON</a></li><li><a href="/festival_times">Festival Times JSON</a></li></ul>'

@app.route('/shabbat_times')
def shabbattimes():
    return get_data_shabbat(shabbattimespage)

@app.route('/festival_times')
def festivaltimes():
    return get_data_festivals(festivaltimespage)

def get_post_dates(english_date, num):

    date_obj = datetime.strptime(english_date, "%d %b %Y").date()
    post_date = date_obj - timedelta(days=num)
    expiry_date = date_obj

    return [post_date.strftime("%Y-%m-%d"), expiry_date.strftime("%Y-%m-%d")]

def get_english_date(start_date, end_date):

    start_date_obj = datetime.strptime(start_date, "%d %b %Y").date()
    end_date_obj = datetime.strptime(end_date, "%d %b %Y").date()

    output = start_date_obj.strftime("%d").lstrip("0")

    if start_date_obj.strftime("%m") == end_date_obj.strftime("%m"):
        output += '/' + end_date_obj.strftime("%d").lstrip(
            "0") + ' ' + start_date_obj.strftime("%b") + ' ' + start_date_obj.strftime("%Y")
    elif start_date_obj.strftime("%Y") == end_date_obj.strftime("%Y"):
        output += ' ' + start_date_obj.strftime("%b") + ' / ' + end_date_obj.strftime("%d").lstrip(
            "0") + ' ' + end_date_obj.strftime("%b") + ' ' + start_date_obj.strftime("%Y")
    else:
        output += ' ' + start_date_obj.strftime("%b") + ' ' + start_date_obj.strftime("%Y") + ' / ' + end_date_obj.strftime(
            "%d").lstrip("0") + ' ' + end_date_obj.strftime("%b") + ' ' + end_date_obj.strftime("%Y")

    return output

def get_hebrew_date(english_date):

    date_obj = datetime.strptime(english_date, "%d %b %Y").date()
    url = 'http://www.hebcal.com/converter/?cfg=json&gy=' + date_obj.strftime(
        "%Y") + '&gm=' + date_obj.strftime("%m") + '&gd=' + date_obj.strftime("%d") + '&g2h=1'
    page = requests.get(url)
    data = json.loads(page.content)

    return [str(data['hd']) + ' ' + data['hm'] + ' ' + str(data['hy']), data['hebrew']]

def get_data_shabbat(url):

    page = requests.get(url)
    tree = BeautifulSoup(page.content, 'html.parser')

    table = tree.find("table", class_="festival-and-fast-times").tbody

    tab = []
    for idx, row in enumerate(table.find_all('tr')):
        if idx > 20:
            break
        var = row.get_text()
        var = var.split('\n')
        tab_row = {}
        print(var)
        sys.stdout.flush()
        if var[0].strip() != "* Mevarachim Hachodesh (Blessing the New Moon)" and var[0].strip() != "" and var[2].strip() != "" and var[2].strip() != "&nbsp;" and var[0].strip() != "Parasha": 
            hebrew_date = get_hebrew_date(var[1].strip())
            post_dates = get_post_dates(var[1].strip(), 6)
            tab_row["Parasha"] = var[0].strip()
            tab_row["PostDate"] = post_dates[0]
            tab_row["ExpiryDate"] = post_dates[1]
            tab_row["StartDate"] = var[1].strip()
            tab_row["StartTime"] = var[2].strip()
            tab_row["EndDate"] = var[3].strip()
            tab_row["EndTime"] = var[4].strip()
            tab_row["Title"] = "Shabbat " + var[1].strip()
            tab_row["HebrewDate_EN"] = hebrew_date[0]
            tab_row["HebrewDate"] = hebrew_date[1]
            tab.append(tab_row)

    json_data = json.dumps(tab)
    return json_data

def get_data_festivals(url):

    page = requests.get(url)
    tree = BeautifulSoup(page.content, 'html.parser')

    table = tree.find("table", class_="festival-and-fast-times").tbody

    return table.get_text()

    tab = []
    for idx, row in enumerate(table.find_all('tr')):
        if idx > 20:
            break
        var = row.get_text()
        var = var.split('\n')
        tab_row = {}
        print(var)
        sys.stdout.flush()
        if var[0].strip() != "* Mevarachim Hachodesh (Blessing the New Moon)" and var[0].strip() != "" and var[1].strip() != "" and var[1].strip() != "&nbsp;" and var[0].strip() != "Parasha": 
            hebrew_date = get_hebrew_date(var[1].strip())
            post_dates = get_post_dates(var[1].strip(), 6)
            tab_row["Parasha"] = var[0].strip()
            tab_row["PostDate"] = post_dates[0]
            tab_row["ExpiryDate"] = post_dates[1]
            tab_row["StartDate"] = var[1].strip()
            tab_row["StartTime"] = var[2].strip()
            tab_row["EndDate"] = var[3].strip()
            tab_row["EndTime"] = var[4].strip()
            tab_row["Title"] = "Shabbat " + var[1].strip()
            tab_row["HebrewDate_EN"] = hebrew_date[0]
            tab_row["HebrewDate"] = hebrew_date[1]
            tab.append(tab_row)

    json_data = json.dumps(tab)
    return json_data


if __name__ == "__main__":
    app.run()
