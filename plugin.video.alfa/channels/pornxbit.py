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

##############      CF2

canonical = {
             'channel': 'pornxbit', 
             'host': config.get_setting("current_host", 'pornxbit', default=''), 
             'host_alt': ["https://www.pornxbit.com"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Peliculas" , action="lista", url=host + "/full-movie/?asgtbndr=1"))
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/porn-videos/?filter=latest&asgtbndr=1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/porn-videos/?filter=most-viewed&asgtbndr=1"))
    # itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "/porn-videos/?filter=longest&asgtbndr=1"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "/actors/"))
    # itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/sites/?sort_by=avg_videos_popularity&from=01"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/?s=%s&filter=latest&asgtbndr=1" % (host,texto)
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
    soup = create_soup(item.url).find('div', class_='videos-list')
    matches = soup.find_all('article', id=re.compile(r"^post-\d+"))
    for elem in matches:

        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='current')
    if next_page:
        next_page = next_page.parent.find_next_sibling("li").a['href']
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
    else:
        data = httptools.downloadpage(url).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('main')
    matches = soup.find_all('article', class_=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title'].replace("&#8211;", "-")
        thumbnail = elem.img['data-src']
        time = elem.find('span', class_='duration')
        quality = elem.find('span', class_='hd-video')
        if time:
            time = time.text.strip()
        else:
            time = ""
        if quality:
            quality = quality.text
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (time,quality,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='current')
    if next_page:
        next_page = next_page.parent.find_next_sibling("li").a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('div', class_='responsive-player')
    matches = soup.find_all('iframe')
    for elem in matches:
        url = elem['src']
        itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

