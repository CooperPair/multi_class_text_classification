# to integrate the code with the crawler site and then work as proceed.
# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from scrapy.http import Request
import re
import pymysql
import mysql.connector
import sys
import hashlib
from datetime import *
import urllib.request
# import time
from scrapy.linkextractors import LinkExtractor
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
import csv
import os
import requests
from scrapy.exporters import XmlItemExporter
from scrapy.selector import Selector
import json
from pprint import pprint
# import xml.etree.ElementTree
# import scrapy_proxies
# from PIL import Image
import mysqlx

# Open database connection
mydb = mysql.connector.connect(host="localhost", user="root", password="saibhagwan", db="meraevents")
# prepare cursor object using cursor() method , gives us the ability to have multiple seperate
# working environments through the same connection to the database
cursor = mydb.cursor()

json_in_list = []
start_urls = []

class MeraEventsSpider(scrapy.Spider):
    name = "meraevents" # name of the spider

    sql1 = """SELECT * FROM about_countries WHERE event_listing = 1"""
    # execute SQL query using execute() method.
    cursor.execute(sql1)
    # Fetch all row using fetchall() method.
    abt_country = cursor.fetchall()
    #print("abt country = ", abt_country)
    for j in abt_country:
        country_name = j[1]
        country_code = j[2]
        #print("country code = ", country_code)

        sql2 = """SELECT * FROM cities_list WHERE country = '%s'""" % (country_name)
        #print(sql2)
        cursor.execute(sql2)
        cities_list = cursor.fetchall()
        for city in cities_list:
            city_name = city[1]
            state_name = city[2]
            #print("city name = ",city_name)
            json = {"countrycode":country_code,"countryname":country_name, "statename":state_name, "original_city_name":city_name,
                                        "duplicate_city_name": city_name}
            json_in_list.append(json)
            #print(json_in_list)
        # print(type(json_in_list))
        # a = json_in_list[0][0]['countrycode']
        # print(a)

        sql3 = """select cities_list.city, cities_list.state, cities_list.country, city_duplicacy.duplicate from cities_list inner join city_duplicacy on cities_list.city=city_duplicacy.original WHERE country = '%s'""" %(country_name)
        #print(sql3)
        cursor.execute(sql3)
        org_dupli_city = cursor.fetchall()
        for orgdup_city in org_dupli_city:
            original_city = orgdup_city[0]
            duplicate_city = orgdup_city[3]
            state = orgdup_city[1]
            json = {"countrycode": country_code, "countryname": country_name, "statename": state_name,
                     "original_city_name": original_city,"duplicate_city_name": duplicate_city}
            json_in_list.append(json)
            #print(json_in_list)
        #print(type(json_in_list))
        #b = json_in_list[0][0]['countrycode']
        #print(b)

        sql = """SELECT * FROM sites_to_crawl WHERE active = 1"""
        cursor.execute(sql)
        site = cursor.fetchall()
        # print("site = ", site)
        for i in site:
            url = i[1]
            link_structure = i[3]
            city_space_alt = i[4]
            state_space_alt = i[5]
            country_space_alt = i[6]
            #print("link str = ", link_structure)

            for city in json_in_list:
                city_name_alt = city['duplicate_city_name'].replace(' ', city_space_alt)
                #print("cna = ",city_name_alt)
                state_name_alt = city['statename'].replace(' ', state_space_alt)
                country_name_alt = city['countryname'].replace(' ', country_space_alt)
                country_code_rec = city['countrycode']

                city_replace = link_structure.replace('cityname',city_name_alt)
                state_replace = city_replace.replace('statename', state_name_alt)
                country_replace = state_replace.replace('countryname', country_name_alt)
                final_url = country_replace.replace('countrycode',country_code_rec)
                #print("cc= ",final_url)

                allowed_domains = [url]
                #print("ad = ",allowed_domains)
                # start_urls = start_url
                start_url = final_url
                start_urls.append(start_url)

                #print(type(start_url))
                #print("Start URL= ",start_url)
                start_urls = start_urls
    #print("starts urls = ", start_urls)
    # to maintain the order of fields in the CSV


    custom_settings = {# specifies exported fields and order
                        'FEED_EXPORT_FIELDS': ['country', 'event_name', 'md5', 'date_added', 'profile_image', 'banner', 'sDate',
                                                'eDate', 'address_line1', 'address_line2', 'pincode', 'state', 'city', 'locality',
                                                'full_address', 'latitude', 'longitude', 'start_time', 'end_time', 'description',
                                                'website', 'fb_page', 'fb_event_page', 'event_hashtag', 'source_name', 'source_url',
                                                'email_id_organizer', 'ticket_url', 'creative_thumb', 'creative_banner']}

    def parse(self, response):
        src = response.url
        #print("src=",src)

        events = response.xpath('//a/@href').extract()
        #print("events = ",events)

        for event in events:
            #print("event = ",event)
            absolute_url = response.urljoin(event)
           #print("asolute url = ", absolute_url)
            yield Request(absolute_url, callback=self.parse_event)

    def parse_event(self, response):
        def replace(string, substitutions):
            substrings = sorted(substitutions, key=len, reverse=True)
            regex = re.compile('|'.join(map(re.escape, substrings)))
            return regex.sub(lambda match: substitutions[match.group(0)], string)

        substitutions = {'\n': ' ', '\r': ' ', '\xa0': ' ', '&amp':'', '&nbsp':''}

        script = json.loads(response.xpath('/html/body/script/text()').extract_first())
        #print(type(script))
        event_name = script[0]['name']
        #print(type(event_name))
        md5_encryption = hashlib.md5(event_name.encode('utf-8')).hexdigest()

        banner = script[0]['image']
        if banner == None:
            banner = "https://ercess.com/live/images/not-found.png"

        banner_name =  banner
        urllib.request.urlretrieve(banner)

        source_url = script[0]['url']

        # geo_found = script[0]['location']
        #
        # if len(geo_found) == None:
        #     pass
        # else:
        #     latitude = script[0]['location']['geo']['latitude']
        #     longitude = script[0]['location']['geo']['longitude']

        #start date and time
        start_date = script[0]['startDate']
        st1 = start_date.find('T')
        st2 = start_date.find('+')
        sdate = start_date[:st1]
        stime = start_date[st1+1:st2]

        #end date and time
        end_date = script[0]['endDate']
        st3 = end_date.find('T')
        st4 = end_date.find('+')
        edate = end_date[:st3]
        etime = end_date[st3+1:st4]

        locality = script[0]['location']['name']
        full_address = script[0]['location']['address']

        date_added = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        description = script[0]['description']
        description1 = ''.join(description)
        # in order to remove the tags with the help of regex
        remove_tags = re.compile('<.*?>')
        description2 = re.sub(remove_tags, '', description1)
        description3 = replace(description2, substitutions)

        pin = re.search("\s[0-9]{6}", full_address)
        if (pin == None):
            pin2 = 000000
        else:
            pin2 = pin.group(0)

        eid = re.findall('\S+@\S+', description3)
        email_id = eid

        cityn = locality.find(': ')
        cityname=locality[cityn+2:]

        selection_dict = next(item for item in json_in_list if item['original_city_name'] == cityname)
        print(selection_dict)

        webinr = event_name.find('Webinar')
        if webinr >= 0 :
            cityname = "Online"
        elif cityname == None:
            cityname = "city_not_found"
        else:
            cityname = cityname

        statename = selection_dict['statename']
        countryname = selection_dict['countryname']

        yield {
            'country': countryname,
            'event_name': event_name,
            'md5': md5_encryption,
            'date_added': date_added,
            'profile_image':  '',
            'banner': banner,
            'sDate': sdate,
            'eDate': edate,
            'address_line1': '',
            'address_line2': '',
            'pincode': pin2,
            'state': statename,
            'city': cityname,
            'locality': locality,
            'full_address': full_address,
            'latitude': '',
            'longitude': '',
            'start_time': stime,
            'end_time': etime,
            'description': description3,
            'website': '',
            'fb_page': '',
            'fb_event_page': '',
            'event_hashtag': '',
            'source_name': '',
            'source_url': source_url,
            'email_id_organizer':email_id,
            'ticket_url': '',
            'creative_thumb': '',
            'creative_banner': ''
        }
        # Prepare SQL query to INSERT a record into the database.
        sql6 ="""INSERT INTO articles2 (country, event_name, md5, date_added, profile_image, banner, sDate, eDate, address_line1,
                  address_line2, pincode, state, city, locality, full_address, latitude, longitude, start_time, end_time, description, 
                  website, fb_page, fb_event_page, event_hashtag, source_name, source_url, email_id_organizer, ticket_url) VALUES
                  VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"""
        val = (countryname, event_name, md5_encryption, date_added, '', banner, sdate, edate, '', '', pin2, statename, cityname,
               locality, full_address, '', '', stime, etime, description3, '', '', '', '', '', source_url, email_id, '', '', '')
        cursor.execute(sql6, val)
        # it is imporrtant to call this method after every transaction is being done so that it can be save.
        mydb.commit()
        abc = cursor.fetchall()
        print("abc = ", abc)
        print(cursor.rowcount, "record inserted.")

        #cursor.execute("""INSERT INTO articles2 VALUES(country, title, md5_encryption, date_added, ?, banner, start_date, end_date, ?, ?, pin2, state, city, locality, full_address, latitude, longitude, start_time, ?, description3, ?, ?, ?, ?)""")
        #mydb.commit()
