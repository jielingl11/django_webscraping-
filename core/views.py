from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators import csrf


import urllib
import urllib.request as req
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import numpy as np
import time
import requests
import re

def google_results(request):
    info_raw_t=[]
    info_raw_l=[]
    
    keyword= request.GET.get('keyword')
    keyword= keyword.replace(" ", "+")
    for i in range(11):
        number= str(10*i)
        url = 'https://www.google.com/search?q={keyword}&start='+number
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        for element in driver.find_elements_by_xpath('//div[@class="g"]'):
            title = element.find_element_by_xpath('.//h3').text
            link = element.find_element_by_xpath('.//div[@class="yuRUbf"]/a').get_attribute('href')
            info_raw_t.append(title.lower())
            info_raw_l.append(link.lower())      
        
    return info_raw_l, info_raw_t
    
def find_contact_info(url, page_source):
    try:
        print('finding contact info for', url)
        EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
    
        list_of_emails=[]
        for re_match in re.finditer(EMAIL_REGEX, page_source):
            list_of_emails.append(re_match.group())   
        if len(list_of_emails)==0:
            list_of_emails.append('No Found')
            
        duplicates=[]
        for i in list_of_emails:
         if list_of_emails.count(i)>1:
             if i not in duplicates:
                 duplicates.append(i)
    
        return duplicates
    except:
        pass

def find_homepages(title, link):
    info=[]
    homepage=[]
    for i in range(len(title)):
        count= 0
        sub_link= link[i]
        count = sub_link.count("/")
        q_find=sub_link.count('?')
        ul_find= sub_link.count('_')
        e_find=sub_link.count('_')
        if count == 3 and q_find==0 and ul_find==0 and e_find==0:
            homepage.append(sub_link)
            info.append(title[i])
    return info, homepage 

def find_contact_list(link_h):
    try:
        contact=[]
        for url in link_h:
            page= find_homepage_text(url)
            email= find_contact_info(url, page)
            contact.append(email) 
    except:
        contact.append('')
        pass
    finally:
        return contact

def find_homepage_text(url):
    try:
        request= requests.get(url, headers={
        "User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Mobile Safari/537.36"})         
        return request.text
    except:
        pass

def home(request):
    result = None
    if 'keyword' in request.GET:
        google_result = google_results(request)
        title= google_result[1]
        link= google_result[0]
        homepage= find_homepages(title, link)
        # title_h= homepage[0]
        link_h= homepage[1]
        # contact_h= find_contact_list(link_h)
        # link= ", ".join( repr(e) for e in link_h  
        result= {'link': link_h}
    return render(request, 'core/home.html', {'result': result})

