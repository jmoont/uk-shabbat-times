#!/bin/python

from bs4 import BeautifulSoup
from flask import Flask
from datetime import datetime, timedelta
from slugify import slugify
import requests
import json

app = Flask(__name__)
shabbattimespage = 'https://www.theus.org.uk/shabbattimes'
festivaltimespage = 'https://www.theus.org.uk/article/festival-fast-times'


@app.route('/')
def hello():
    return 'Shabbat Times Service'


@app.route('/shabbat_times')
def shabbattimes():
    return get_data_shabbat(shabbattimespage)

@app.route('/festival_times')
def festivaltimes():
    return get_data_festivals(festivaltimespage)

def get_post_dates(english_date, num):

    if english_date == "":
        return ["", ""]
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
    for row in table.find_all('tr'):
        var = row.get_text()
        var = var.split('\n')
        tab_row = {}
        if var[1].strip() != "" and var[1].strip() != "Parasha": 
            hebrew_date = get_hebrew_date(var[2].strip())
            post_dates = get_post_dates(var[2].strip(), 6)
            tab_row["Parasha"] = var[1].strip()
            tab_row["PostDate"] = post_dates[0]
            tab_row["ExpiryDate"] = post_dates[1]
            tab_row["StartDate"] = var[2].strip()
            tab_row["StartTime"] = var[3].strip()
            tab_row["EndDate"] = var[4].strip()
            tab_row["EndTime"] = var[5].strip()
            tab_row["Title"] = "Shabbat " + var[2].strip()
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

    # tab = []
    # for row in table[2:]:
    #     for col in row:
    #         var = col.text_content()
    #         var = var.strip()
    #         var = var.split('\n')
    #         if len(var) > 3:
    #             tab_row = {}
    #             hebrew_date = get_hebrew_date(var[3].strip())
    #             post_dates = get_post_dates(var[3].strip(), 3)
    #             tab_row["Festival"] = var[0].strip()
    #             tab_row["PostDate"] = post_dates[0]
    #             tab_row["ExpiryDate"] = post_dates[1]
    #             tab_row["StartDate"] = var[1].strip()
    #             tab_row["StartTime"] = var[2].strip()
    #             tab_row["EndDate"] = var[3].strip()
    #             tab_row["EndTime"] = var[4].strip()
    #             tab_row["Title"] = "Shabbat " + var[1].strip()
    #             tab_row["Slug"] = slugify("Shabbat " + var[1].strip())
    #             tab_row["HebrewDate_EN"] = hebrew_date[0]
    #             tab_row["HebrewDate"] = hebrew_date[1]
    #             tab_row["EnglishDate"] = get_english_date(
    #                 var[1].strip(), var[3].strip())
    #             tab.append(tab_row)

    # json_data = json.dumps(tab)
    # return json_data


if __name__ == "__main__":
    app.run(debug=True)
