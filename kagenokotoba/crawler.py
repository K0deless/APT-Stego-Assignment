#!/usr/bin/python3

'''
Python tool to hide information inside of text through a key.

File: crawler.py

@authors:
    - David Regueira
    - Santiago Rocha
    - Eduardo Blazquez
    - Jorge Sanchez
'''


""" Crawler utility to recover cover text, cover image and URL """

import requests, random
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO


class SourceFinding():
    """ Source Text and Image crawler """
    _SESSION = requests.session()
    _HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
                    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Accept-language":"en;q=0.5,ru;q=0.3",
                    "Accept-Encoding":"gzip, deflate, br"}

    def __init__(self, source_url = '', source_language = ''):
        self.source_url = source_url
        self.source_language = source_language

    def generate(self):
        """
        Main function from the class to extract
        the text to hide information.

        :return: str with the text where to hide information
        :return: str of source language
        """
        if self.source_language != '':
            if self.source_language == "es":
                if self.source_url != '':
                    return self.get_source_es(self.source_url)
                else:
                    return self.random_source_es(), "es"
            elif self.source_language == "en":
                if self.source_url != '':
                    return self.get_source_en(self.source_url)
                else:
                    return self.random_source_en(), "en"
            else:
                if self.source_url != '':
                    return self.get_source_ru(self.source_url)
                else:
                    return self.random_source_ru(), "ru"

        return None, None


    def get_source_es(self, tale_url):
        """ Locate a text and an image from a spanish website """
        req = self._SESSION.get(tale_url, headers=self._HEADERS)
        bsObj = BeautifulSoup(req.text, "html.parser")
        text = bsObj.find("div", {"class","alm-nextpage"}).get_text()
        image_link = bsObj.find("div", {"class":"imagen-post"}).find("img", {"class":"new-featured-image"})["data-src"]

        self._get_text(text)
        self._get_image(image_link)


    def random_source_es(self):
        """ Locate information from a spanish webpage through a random book """
        tales_list = []
        url = "https://www.pequeocio.com/cuentos-infantiles/cuentos-clasicos/"

        req = self._SESSION.get(url, headers=self._HEADERS)
        bsObj = BeautifulSoup(req.text, "html.parser")
        tales_links = bsObj.find("section", {"class","card-module"}).findAll("div", {"class","card-information"})
        for tale_link in tales_links:
            tales_list.append(tale_link.find("a")["href"])

        random_tale_url = random.choice(tales_list)
        self.get_source_es(random_tale_url)

        return random_tale_url

    def get_source_en(self, character_url):
        """ Locate a text and an image from an english website """
        req = self._SESSION.get(character_url, headers=self._HEADERS)
        bsObj = BeautifulSoup(req.text, "html.parser")
        text = bsObj.find("div", {"id":"mw-content-text"}).get_text()
        image_link = bsObj.find("div", {"id":"mw-content-text"}).find("img")["src"]
        image_link = "http:"+image_link

        self._get_text(text)
        self._get_image(image_link)


    def random_source_en(self):
        """ Locate information from an english webpage through a random simpson character """
        characters_list = []
        url = "https://en.wikipedia.org/wiki/List_of_The_Simpsons_characters"

        req = self._SESSION.get(url, headers=self._HEADERS)
        bsObj = BeautifulSoup(req.text, "html.parser")
        rows = bsObj.find("table", {"class","wikitable"}).findAll("tr")[3:]
        for row in rows:
            if row.find("a"):
                characters_list.append(row.find("a")['href'])

        random_character_url = "https://en.wikipedia.org"+random.choice(characters_list)
        self.get_source_en(random_character_url)

        return random_character_url

    def get_source_ru(self, random_new):
        """ Locate a text and an image from a russian website """
        req = urlopen(random_new)
        response = str(req.read(), 'utf-8')
        bsObj = BeautifulSoup(response, "html.parser")
        text = bsObj.find("div", {"class":"b-text"}).findAll("p")
        text_new = ''
        for item in text:
            text_new += item.get_text()
        image_link = bsObj.find("img", {"class":"g-picture"})["src"]

        self._get_text(text_new)
        self._get_image(image_link)


    def random_source_ru(self):
        """ Locate information from a russian webpage through a random post """
        news_list = []
        url = "https://lenta.ru/rubrics/world/politic/"
        req = urlopen(url)
        response = str(req.read(), 'utf-8')
        bsObj = BeautifulSoup(response, "html.parser")
        rows = bsObj.find("div", {"class":"news-list"}).findAll("div", {"class":"news"})

        for row in rows:
            if row.find("a"):
                news_list.append(row.find("a")['href'])

        random_new_url = "https://lenta.ru"+random.choice(news_list)
        self.get_source_ru(random_new_url)

        return random_new_url

    def _get_text(self, text):
        with open("cover.txt", "w") as f:
            f.write(text)

        f.close()

    def _get_image(self, image_link):
        req = self._SESSION.get(image_link, headers=self._HEADERS)

        _tmp_image = Image.open(BytesIO(req.content))
        _tmp_image.save("cover.png", "PNG")


if __name__ == "__main__":
    '''
    source = SourceFinding(None)

    command = input("""
    Language of the sources ?

    [es]pañol
    [en]glish
    [ru]ssian

    """)
    if command == "es":
        metadata = source.random_source_es()
        print(metadata)
    elif command == "en":
        metadata = source.random_source_en()
        print(metadata)
    else:
        source.random_source_ru()
    '''