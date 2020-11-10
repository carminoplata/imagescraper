#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 17:47:25 2020

@author: carmine
"""

import imghdr
import logging
import os
import posixpath
import re
import threading
import urllib.request

from urllib.error import URLError, HTTPError

class BingSearch(threading.Thread):
    
    def __init__(self, name, query, filters, limit, output_dir, cv, level):
        super().__init__(name=name)
        self.name = name
        self.query = query
        self.filters = filters
        self.download_count = 0
        assert type(limit) == int, "limit must be integer"
        self.limit = limit
        self.output_dir = output_dir
        self.timeout = 60
        self.page_counter = 0
        self.base_url = 'https://www.bing.com/images/async?q=' \
        + urllib.parse.quote_plus(self.query)
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; ' \
            + 'rv:81.0) Gecko/20100101 Firefox/81.0'
        self.headers = {'User-Agent': self.user_agent}
        self.cv = cv
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - [%(name)s] - [%(levelname)s] - %(message)s')
        filehandler = logging.FileHandler("{}/BeerScraper/log/{}.log".format(os.getcwd(),
                                                         self.name))
        filehandler.setFormatter(formatter)
        self.logger.addHandler(filehandler)

    
    def save_image(self, link, file_path):
        
        self.logger.debug("Saving Image into {}".format(file_path))
        
        request = urllib.request.Request(link, None, self.headers)
        image = urllib.request.urlopen(request, timeout=self.timeout).read()
        self.logger.debug("Image Downloaded from {}".format(link))
        if not imghdr.what(None, image):
            self.logger.warning('Error: Invalid image, not saving {}\n'
                  .format(link))
            raise ValueError
            
        with self.cv:
            with open(file_path, 'wb') as f:
                f.write(image)
            self.cv.notify_all()

        
    
    def download_image(self, link):
        self.download_count += 1

        # Get the image link
        try:
            path = urllib.parse.urlsplit(link).path
            filename = posixpath.basename(path).split('?')[0]
            file_type = filename.split(".")[-1]
            if file_type.lower() not in ["jpe", "jpeg", "jfif", "exif", 
                                         "tiff", "gif", "bmp", "png", "webp", 
                                         "jpg"]:
                file_type = "jpg"

            # Download the image
            self.logger.debug("Downloading Image #{} from {}"
                  .format(self.download_count, link))
            
            
            
            self.save_image(link, self.output_dir + "/{}_{}.{}".format(self.name,
                str(self.download_count), file_type))
            self.logger.info("File Downloaded !\n")
        except Exception as e:
            self.download_count -= 1
            self.logger.error("Issue getting: {}\n[!] Error:: {}"
                              .format(link, e))
    
    def run(self):
        
        while self.download_count < self.limit:
            self.logger.info("Scraping from page {}"
                             .format(self.page_counter + 1))
            self.base_url += '&first='+ str(self.page_counter) + '&count=' \
                + str(self.limit) + '&adlt=false&qft=' + self.filters
            try:
                request = urllib.request.Request(self.base_url, None, 
                                             headers = self.headers)
            
                response = urllib.request.urlopen(request)
                
                html = response.read().decode('utf-8')
                links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
                self.logger.info("Found {} images on page {}"
                      .format(len(links), self.page_counter+1))
                for link in links:
                    if self.download_count < self.limit:
                        self.download_image(link)
                    else:
                        self.logger.info("Downloaded {} images."
                              .format(self.download_count))
                        break

                self.page_counter += 1
                
            except HTTPError as error:
                self.logger.warning("Error {} during processing "
                      .format(str(error.code)))
                
            except URLError as error:
                self.logger.error("Error during processing {}"
                      .format(self.base_url))
                self.logger.error("Caused by:{} ".format(str(error.reason)))
                
            
        
    