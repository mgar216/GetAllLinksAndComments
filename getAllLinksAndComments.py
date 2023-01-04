#!/bin/python

import requests, re
from bs4 import BeautifulSoup



def getURL(page):
    start_link = page.find("a href")
    if start_link == -1:
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1: end_quote]
    return url, end_quote

def getLinks(url):
    links = []
    response = requests.get(url)
    page = str(BeautifulSoup(response.content))
    while True:
        url, n = getURL(page)
        page = page[n:]
        if url:
            links.append(url)
        else:
            break
    return links

def recurseAllLinks(url, links):
    all_links = []
    for i in links:
        response = getLinks((url + i).replace('//', '/').replace(':/', '://'))
        all_links.append(response)
    return all_links

def cleanup(all_links):
    uniq_links = set()
    for i in all_links:
        for link in i:
            uniq_links.add(link)
    return list(uniq_links)

def getAllLinks(url):
    links = getLinks(url)
    all_links = recurseAllLinks(url, links)
    return cleanup(all_links)

def getAllComments(url, get_links=False):
    comments = {}
    all_links = getAllLinks(url)
    base_url = url.rstrip('/')
    for sub in [k for k in all_links if 'http' not in k]:
        current_url = (base_url + sub)
        if current_url not in comments.keys():
            comments[current_url] = []
        res = requests.get(current_url)
        matches = re.findall(r"""(<!--(.*?)-->)|(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)|(^'.*$)|(^#.*$)""", res.text)
        for match in matches:
            for m in match:
                if m:
                    comments[current_url].append(m.strip())
    if get_links:
        return [comments, all_links]
    return comments


url = "http://<ip>:<port>/" # Change this to site URL
comments, links = getAllComments(url, get_links=True)
print(links)
print(comments)
