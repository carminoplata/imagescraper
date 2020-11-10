# ImageScraper

ImageScraper is a web scraper which goal is to collect at most N images belonging at a user's category joined to the same amount of images of other 3 default
categories: 

- Animals
- Objects
- People



## Why should I use it?

This scraper is really useful when you want to create a dataset of Web Images to adopt for developing your model classification. 

Possible Applications:

- Image Classification
- Creation of noise dataset

## Limits

Actually, the Image Scraper is going to collect images only from Bing Search

## How to run

1) Clone the repository and get in imagescraper.
2) Run the following command:

  ```
  python3 imagescraper.py -i <category_to_search> -n <num_of_images> -o <output_folder> 
  ```

**WARNING**: output_folder is the full path at the folder where you want to store images and it must exist.

