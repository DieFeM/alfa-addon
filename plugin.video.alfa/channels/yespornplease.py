# -*- coding: utf-8 -*-
#------------------------------------------------------------
import re

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from core import urlparse
from bs4 import BeautifulSoup
from modules import autoplay

list_quality = []
list_servers = []

canonical = {
             'channel': 'yespornplease', 
             'host': config.get_setting("current_host", 'yespornplease', default=''), 
             'host_alt': ["https://yespornpleasexxx.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "pornstars/"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="canal", url=host ))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "xnxx-tags/" ))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%s?s=%s" % (host,texto)
    try:
        return lista(item)
    except Exception:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='box')
    for elem in matches:
        url = elem.a['href']
        title = elem.figcaption.text.strip()
        thumbnail = elem.img['src']
        if "svg+xml" in thumbnail:
            thumbnail = elem.img['data-src']
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    return itemlist


def canal(item):
    logger.info()
    itemlist = []
    # itemlist.append(Item(channel=item.channel, title="BangBros" , action="lista", url=host + "/bangbros/"))
    itemlist.append(Item(channel=item.channel, title="Brazzers" , action="lista", url=host + "/brazzers/"))
    itemlist.append(Item(channel=item.channel, title="Reality Kings" , action="lista", url=host + "/reality-kings/"))
    itemlist.append(Item(channel=item.channel, title="SexMex" , action="lista", url=host + "/sexmex/"))
    # soup = create_soup(item.url)
    # matches = soup.find('div', class_='text-center').find_all('a', href=re.compile(r"^https://yespornpleasexxx.com/")) #.select('a[href^="https://yespornpleasexxx.com/"]')
    # for elem in matches:
        # url = elem['href']
        # title = elem.text.strip()
        # thumbnail = ""
        # plot = ""
        # if not "tag" in url:
            # itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                                 # fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail= ""
        if elem.img:
            thumbnail = elem.img['src']
        if "base64" in thumbnail or ".gif" in thumbnail:
            thumbnail = elem.img['data-src']
        time = elem.find('p').text.strip()
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('div', class_='wp-video')
    matches = soup.find_all('iframe')
    for elem in matches:
        if elem.get('data-litespeed-src',''):
            url = elem['data-litespeed-src']
        else:
            url = elem['src']
        if "player-x.php?" in url:
            url = url.split("q=")
            url = url[-1]
            import base64
            url = base64.b64decode(url).decode('utf8')
            url = urlparse.unquote(url)
            url = BeautifulSoup(url, "html5lib", from_encoding="utf-8")
            url = url.a['href']
            url += "|Referer=%s" % host
        itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist
