# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector lulustream By Alfa development Group
# --------------------------------------------------------
import re
from core import httptools, jsontools
from core import scrapertools
from platformcode import logger

video_urls = []

#Error al reproducir

def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    response = httptools.downloadpage(page_url)
    global data
    data = response.data
    if not response.sucess or "Not Found" in data or "File was deleted" in data or "is no longer available" in data:
        return False, "[lulustream] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    url = scrapertools.find_single_match(data, 'sources: \[{file:"([^"]+)"')
    url +="|Referer=https://luluvdo.com/"
    video_urls.append(["[lulustream]", url])
    return video_urls
