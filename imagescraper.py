#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 13:31:29 2020

@author: carmine
"""
#from bing_image_downloader import downloader

import logging
import logging.config
import os
import sys
import threading

from bingsearch import BingSearch
from pathlib import Path

def parsearguments(args):
    target = ''
    output_folder = ''
    num_images = 0
    i = 1
    loglevel = 'INFO'
    if args[0] != '-i' :    
        raise ValueError
                   
    while i < len(args) and args[i]!='-n':
        target += args[i] + ' '
        i+= 1
        
    if args[i] != '-n' or i >= len(args):
        raise ValueError
        
    num_images = int(args[i+1])
    
    if args[i+2] != '-o':
        raise ValueError
    
    output_folder = args[i+3]
    
    i+=3
    
    if i < (len(args)-1) :
        loglevel = args[i+1]
    
    return target, num_images, output_folder, loglevel




if __name__ == '__main__':
    logging.config.fileConfig(os.path.join(os.getcwd(), 'config/logging.conf'))
    logger = logging.getLogger('ImageScraper')
    logger.info("Welcome to ImageScraper!")
    
    if(len(sys.argv) < 2):
        logger.error("Run: imagescraper.py -i <query_to_search> -n <num_of_images> "
              +" -o <output_folder>")
        exit(-1)
    try:
        target, num_images, output_folder, loglevel = parsearguments(sys.argv[1:])
    
        if(not target or not num_images or not output_folder):
            logger.error("Impossible parse the arguments")
            
        logging.info("Searching {} using Bing Search...".format(target))
        
        lock = threading.Lock()
        cv = threading.Condition(lock)
        
        if not os.path.isdir(output_folder):
                os.mkdir("{}/{}".format(os.getcwd(), output_folder))
        beerSearcher = BingSearch("BeerSearcher", target,
                                  "+filterui:imagesize-medium", num_images,
                                  output_folder, cv, loglevel)
        peopleSearcher = BingSearch("PeopleSearcher", "people",
                                    "+filterui:imagesize-medium", num_images,
                                    output_folder, cv, loglevel)
        animalSearcher = BingSearch("AnimalSearcher","animals",
                                    "+filterui:imagesize-medium", num_images,
                                    output_folder, cv, loglevel)
        objectSearcher = BingSearch("ObjectSearcher", "objects", 
                                    "+filterui:imagesize-medium", num_images,
                                    output_folder, cv, loglevel)
        
        #beerSearcher.run()
        
        
        tasks = [beerSearcher, peopleSearcher, animalSearcher, objectSearcher]
        
        for t in tasks:
            t.start()
            
        for t in tasks:
            t.join()
    except IndexError as e: 
        logger.error(e.with_traceback())
    except ValueError:
        logger.error("Unknown command!\n Please run:\n imagescraper.py -i "
              + "<query_to_search> -n <num_of_images> -o <output_folder> ")