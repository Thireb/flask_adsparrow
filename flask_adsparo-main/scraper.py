#!/usr/bin/env python3
from rich import print as rp
from pprint import pprint as pp
from flask import Flask, flash, render_template, render_template_string, request, redirect, jsonify, Response, url_for, send_file
import os
# import flask_rich
import random
import requests
import json
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
from flask_cors import CORS
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.headless = True

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret-key"
cors = CORS(app)

## Log EXP

# rl = flask_rich.RichApplication()
# rl.init_app(app)
# app.logger.setLevel(7)

## Original Comments

# app.config['CORS_HEADERS'] = 'Content-Type'
# If it doesn't Work For you, Uncomment the Line above

@app.route('/status')
def app_home():
    return Response("server running"), 200

@app.route('/', methods=["GET"])
def run_display():
    return render_template('dist/index.html')

@app.route('/echo_logo.png', methods=["GET"])
def just_logo_getter():
    return send_file("static/logo.png")

@app.route('/sw.png', methods=["GET"])
def sw_just_logo_getter():
    return send_file("static/sw.png")

@app.route('/sf.png', methods=["GET"])
def sf_just_logo_getter():
    return send_file("static/sf.png")

@app.route('/search', methods=["GET", "POST"])
def app_search():
    if request.method == "POST":
        country_code = request.form.get("country_drop")
        search_term = request.form.get("search")
        if search_term == '':
            search_term = 'shirts'
        limit = request.form.get("rangeC")
        flash("Results Found")
        return redirect(url_for("results", country_code=country_code, search_term=search_term, limit=limit))
    return render_template(
        "form.html", 
        state="Search",
    )

@app.route("/results/<limit>/<country_code>/<search_term>", methods=["GET", "POST"])
def results(country_code, search_term, limit):
    # return render_template(
    #     "results.html",
    #     data=scrape(country_code=country_code, search_term=search_term,limit=limit),
    # )
    return jsonify(scrape(country_code=country_code, search_term=search_term,limit=limit))

def scrape(
    country_code = "US",
    search_term = "",
    url = "",
    limit = 5,
    field = "",
    token = "EAAGiekD1DjYBAP8nONd9LgyGZBHHMW0KUZCOIwZCZA4p4ncPADynZAylhG7PFZBPrhZAJd3eFA8vefy9SoabSfO3VvM4KFkcD6nxYABrRKjpLvy00kYHkXxWbMgPdaqLByM4cKVG57FW6jLYY4LO0hIHGsl0ScZBkRlFJFLvZBpvJpkAZCu6PB70Q66S9uDtb7INUZD",
    # token = "EAAJAmUq9svABAPF4Ds42zExohu2BvUH7ZCMZCZAe4IzUe7BnZC7UZACryGMvn0d5DaGZCYWxWUsGxlGztquyU32UdUElZCOOaq564eQH3IStQCLtamGSCa2OpWwCUclZB0jypgRjQpnpiJMKIQUdidXP1feqxP6jOT9pEfoYjIyPBQZDZD",
):
    # pattern = 'https://graph.facebook.com/{}/ads_archive?access_token={}&fields={}&search_terms={}&ad_reached_countries={}&search_page_ids={}&ad_active_status={}&limit={}'
    if url == "":
        url_pattern = f"https://graph.facebook.com/v15.0/ads_archive?access_token={token}&ad_active_status=ACTIVE&fields={field}&search_terms={search_term}&ad_reached_countries={country_code}&ad_active_status=ALL&limit={limit}"
    else:
        url_pattern = url+f"access_token={token}"
    data = requests.get(url_pattern)
    # print(data.status_code)
    # f = open("ret.json", 'w')
    # f.write(json.dumps(data.json()))
    # f.close()
    return data_format(data)

def data_format(data):
    links = [item["ad_snapshot_url"] for item in data.json()['data']]
    data_to_flatten = list()
    driver = webdriver.Chrome(options=chrome_options)
    for link in links:
        try:
            driver.get(link)
            soup = bs(driver.page_source, 'html.parser')
            # requesting = requests.get(link)
            # soup = bs(requesting.text, 'html.parser')
            class_finder = soup.find('div', {"class": "_8n9h"})
            url = urlparse(link).query
            idx = url.split('&')[0].lstrip('id=')
            html = str(class_finder)
            temp = {"html":html,"id":idx}
            data_to_flatten.append(temp)

            ## another log for customer

            app.logger.info('Selenium Output:')
            pp(data_to_flatten)
        except:
            pass
    return data_cleaner(data_to_flatten)

def data_cleaner(data):
    data_to_return = list()
    for item in data:
        parser = bs(item['html'], 'html.parser')
        # TEXT
        usable_spans = list()
        usable_spans.append(parser.find_all('span')[0].getText()) # Profile
        usable_spans.append(parser.find_all('span')[3].getText()) # Paid By
        usable_spans.append(parser.find_all('div', class_="_4ik4 _4ik5")[1].getText())
        usable_spans.append(f"https://web.facebook.com/ads/library/?active_status=active&ad_type=all&country=ALL&q={parser.find_all('span')[0].getText()}&search_type=keyword_exact_phrase&media_type=all") # Exp main_text Get
        # try:
        #     if parser.find_all('span')[9].getText().lower() == 'learn more' or parser.find_all('span')[9].getText().lower() == 'send message' or parser.find_all('span')[9].getText().lower() == 'watch more':
        #         usable_spans.append(parser.find_all('span')[8].getText()) # main_text
        #     else:
        #         usable_spans.append(parser.find_all('span')[9].getText()) # main_text
        # except:
        #     usable_spans.append("")
        
        for i in range(len(usable_spans)):
            if usable_spans[i].__contains__('\n'):
                usable_spans[i] = usable_spans[i].replace("\n", " ")
        # IMAGES
        all_images = parser.find_all("img")
        image_links = [img.get('src') for img in all_images]
        # VIDEOS
        all_videos = parser.find_all("video")
        video_links = [video.get('src') for video in all_videos]
        video_posters = [video.get('poster') for video in all_videos]
        # LINKS
        if len(video_links)!=0:
            video_link = video_links[0]
        else:
            video_link = ''
        if len(video_posters)!=0:
            video_poster = video_posters[0]
        else:
            video_poster = ''
        
        rand = random.randrange(1,30)
        all_links = parser.find_all('a')
        links = [link.get('href') for link in all_links]
        temp_dict = {
            "rand":rand,
            "id":item['id'],
            "text": usable_spans, 
            "imgs": image_links, 
            "videos": [video_link, video_poster],
            "links": links,
        }
        data_to_return.append(temp_dict)
        
        # Log for customers
        app.logger.info('Final Data:')
        pp(temp_dict)

    return data_to_return

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
