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

# https://ok.xxx  https://www.pornhat.com  https://hello.porn/  https://ok.porn   https://www.perfectgirls.xxx/
# https://max.porn/  https://pornstars.tube/
canonical = {
             'channel': 'perfectgirls', 
             'host': config.get_setting("current_host", 'perfectgirls', default=''), 
             'host_alt': ["https://www.perfectgirls.xxx/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Ultimos" , action="lista", url=host))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "popular/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "trending/"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "pornstars/"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "channels/"))
    # itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%ssearch/%s/" % (host, texto)
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
    matches = soup.find_all('div', class_='thumb-bl')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        url = urlparse.urljoin(item.url,url)
        cantidad = elem.find('div', class_='thumb-total')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail) )
    next_page = soup.find('li', class_='pagination-next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    matches = soup.find_all('div', class_='thumb-bl-video')
    for elem in matches:
        logger.debug(elem)
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-original']
        if not thumbnail.startswith("http"):
            thumbnail = "https:%s" % thumbnail
        plot = ""
        url = urlparse.urljoin(item.url,url)
        action = "play"
        if logger.info() is False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='pagination-next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url, next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page ))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    pornstars = soup.find('div', class_='video-info').find_all('a', href=re.compile("/pornstars/"))
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    lista = item.contentTitle.split()
    lista.insert (0, pornstar)
    item.contentTitle = ' '.join(lista)    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist