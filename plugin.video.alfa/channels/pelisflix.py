# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from core import urlparse
from modules import autoplay
from platformcode import config, logger
from core import httptools, scrapertools, tmdb
from core import servertools, channeltools
from core import urlparse
from bs4 import BeautifulSoup
from channelselector import get_thumb

SERVER = {'01': 'Fembed', '02': 'Streamtape', '03': 'Doodstream', 'Ok': 'okru', 'Flixplayer': 'gounlimited', 
          'gounlimited': 'gounlimited', 'VIP': 'VIP', 'Dood': 'Doodstream', 'Femax20': 'Fembed', 'APP': 'directo'}
IDIOMAS = {"1": "CAST", "0": "LAT", "2": "VOSE", "Castellano": "CAST", "Latino": "LAT", "Subtitulado": "VOSE"}

list_language = list(IDIOMAS.values())
list_quality = []
list_servers = list(SERVER.values())


canonical = {
             'channel': 'pelisflix', 
             'host': config.get_setting("current_host", 'pelisflix', default=''), 
             'host_alt': ["https://pelisflixhd.fit/"], 
             'host_black_list': ['https://pelisflixhd.click/', 'https://pelisflixhd.buzz/', 'https://pelisflixhd.biz/',
                                 'https://pelisflixhd.cam/', 'https://pelisflixhd.fun/', 'https://pelisflixhd.net/', 
                                 'https://pelisflixhd.vip/', 'https://pelisflixhd.com/', 'https://pelisflixhd.pro/', 
                                 'https://pelisflixtv.lat/', 'https://pelisflix.town/', 'https://pelisflix.food/', 
                                 'https://pelisflix.works/', 'https://pelisflix.loan/', 'https://pelisflix.casa/',
                                 'https://pelisflix.show/', 'https://pelisflix.zone/', 'https://pelisflix.host/', 
                                 'https://pelisflix.codes/', 'https://pelisflix.mom/', 'https://pelisflix.tools/', 
                                 'https://pelisflix.quest/', 'https://pelisflix.hair/', 'https://pelisflix.store/'
                                 "https://pelis28.art/", "https://pelisflix2.fun/", "https://pelisflix.run/", 
                                 "https://pelisflix.pw/", "https://pelisflix.biz/", "https://ww2.pelisflix2.one/", 
                                 "https://pelisflix2.one/", "https://pelisflix.li/", "https://ww3.pelisflix2.one/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 3, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_save = host
__channel__ = canonical['channel']
ignore_response_code = True


def mainlist(item):
    logger.info()
    
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(item.clone(title="FINDVIDEOS" , action="findvideos", url= host + "pelicula1/sie-sagt-er-sagt/", thumbnail=get_thumb("movies", auto=True)))
    
    itemlist.append(item.clone(title="Estrenos" , action="lista", url= host + "genero/estrenos/", thumbnail=get_thumb("premieres", auto=True)))
    itemlist.append(item.clone(title="Peliculas" , action="lista", url= host + "peliculas-online/", thumbnail=get_thumb("movies", auto=True)))
    itemlist.append(item.clone(title="Series", action="lista", url= host + "series-online/", thumbnail=get_thumb("tvshows", auto=True)))
    itemlist.append(item.clone(title="Anime", action="lista", url= host + "genero/anime/", thumbnail=get_thumb("anime", auto=True)))
    itemlist.append(item.clone(title="Genero" , action="categorias", url= host, thumbnail=get_thumb('genres', auto=True)))

    itemlist.append(item.clone(title="Productora" , action="categorias", url= host + "peliculas", thumbnail=get_thumb("studio", auto=True)))
    # itemlist.append(item.clone(title="Año" , action="anno"))
    # itemlist.append(item.clone(title="Alfabetico", action="section", url=host, thumbnail=get_thumb("alphabet", auto=True)))
    itemlist.append(item.clone(title="Buscar...", action="search", thumbnail=get_thumb("search", auto=True)))

    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def configuracion(item):
    from platformcode import platformtools
    
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    
    return ret


def create_soup(url, referer=None, post=None, unescape=False):
    logger.info()
    
    headers = {'Referer': referer}
    
    data = httptools.downloadpage(url, headers=headers, post=post, ignore_response_code=ignore_response_code, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    
    return soup


def search(item, texto):
    logger.info()
    
    try:
        texto = texto.replace(" ", "+")
        item.url = "%s?s=%s" % (host, texto)
        if texto != "":
            return lista(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except Exception:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def anno(item):
    logger.info()
    from datetime import datetime
    
    itemlist = []
    
    now = datetime.now()
    year = int(now.year)
    while year >= 1940:
        itemlist.append(item.clone(title="%s" %year, action="lista", url= "%srelease/%s" % (host,year)))
        year -= 1
    
    return itemlist


def categorias(item):
    logger.info()
    
    itemlist = []
    
    if "Genero" in item.title:
        soup = create_soup(item.url).find("ul", class_="sub-menu")
    else:
        soup = create_soup(item.url).find("li", class_="menu-item-109").parent
    matches = soup.find_all("li")
    
    for elem in matches:
        url = elem.a["href"]
        title = elem.a.text
        if "/estrenos/" not in url: 
            itemlist.append(item.clone(action="lista", url=url, title=title))
    if "Genero" not in item.title:
        itemlist.append(item.clone(action="lista", url="%sgenero/dc-comics/" % host, title="DC"))
        itemlist.append(item.clone(action="lista", url="%sgenero/marvel/" % host, title="MARVEL"))
    
    return itemlist


def section(item):
    logger.info()
    
    itemlist = []
    
    soup = create_soup(item.url).find("ul", class_="AZList")
    
    for elem in soup.find_all("li"):
        url = elem.a["href"]
        title = elem.a.text
        itemlist.append(item.clone(action="alpha_list", url=url, title=title))
    
    return itemlist


def alpha_list(item):
    logger.info()
    
    itemlist = []
    
    soup = create_soup(item.url)
    matches = soup.find("section")
    
    if not matches:
        return itemlist
    for elem in matches.find_all("tr"):
        info = elem.find("td", class_="MvTbTtl")
        thumbnail = elem.img["data-lazy-src"]
        url = info.a["href"]
        title = info.a.text.strip()
        year = elem.find_all('td')[4].text
        new_item = item.clone(url=url, title=title, thumbnail=thumbnail, infoLabels={"year": year})
        if "series" in url:
            new_item.action = "seasons"
            new_item.contentSerieName = title
            new_item.contentType = 'tvshow'
        else:
            new_item.action = "findvideos"
            new_item.contentTitle = title
            new_item.contentType = 'movie'
            # new_item.language = language
        
        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    if not config.get_setting('unify') and not channeltools.get_channel_parameters(__channel__)['force_unify']:
        a = len(itemlist)-1
        for i in itemlist:
            if a >= 0:
                title= itemlist[a].contentTitle
                titulo = itemlist[a].title
                titulo = scrapertools.find_single_match(titulo, '(\\[COLOR[^"]+)')
                title = "%s %s" %(title, titulo)
                itemlist[a].title = title
                a -= 1
    
    next_page = soup.find('a', class_='current')
    if next_page and next_page.find_next_sibling("a"):
        next_page = next_page.find_next_sibling("a")['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="alpha_list", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url, referer=host)
    matches = soup.find_all("li", class_=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.h2.text.strip()
        thumbnail = elem.figure.img['data-src']
        year = elem.find(class_='Date')
        if year:
            year = year.text
            if year in title:
                title = title.replace(year, "")
        else:
            year = elem.find(class_='Date')
        if year == '':
            year = '-'
        
        new_item = item.clone(url=url, title=title, thumbnail=thumbnail, infoLabels={"year": year})
        
        if "serie" in url:
            new_item.action = "seasons"
            new_item.contentSerieName = title
            new_item.contentType = 'tvshow'
        else:
            new_item.action = "findvideos"
            new_item.contentTitle = title
            new_item.contentType = 'movie'
            # if language:
                # new_item.language = language
        
        itemlist.append(new_item)

    tmdb.set_infoLabels(itemlist, True)

    if not config.get_setting('unify') and not channeltools.get_channel_parameters(__channel__)['force_unify']:
        a = len(itemlist)-1
        for i in itemlist:
            if a >= 0:
                title= itemlist[a].contentTitle
                titulo = itemlist[a].title
                titulo = scrapertools.find_single_match(titulo, '(\\[COLOR[^"]+)')
                title = "%s %s" %(title, titulo)
                
                itemlist[a].title = title
                a -= 1

    next_page = soup.find('a', class_='current')
    if next_page and next_page.find_next_sibling("a"):
        next_page = next_page.find_next_sibling("a")['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    
    return itemlist


def seasons(item):
    logger.info()
    
    itemlist = list()
    infoLabels = item.infoLabels
    
    soup = create_soup(item.url)
    matches = soup.find_all("section", class_="SeasonBx")

    for elem in matches:
        url = elem.a['href']
        season = elem.find("span").text
        title = "Temporada %s" % season
        infoLabels["season"] = season
        infoLabels["mediatype"] = 'season'
        
        itemlist.append(item.clone(title=title, url=url, action="episodesxseasons", infoLabels=infoLabels))
    
    tmdb.set_infoLabels_itemlist(itemlist, True)
    
    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(item.clone(title="[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]", url=item.url,
                        action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName))
    
    return itemlist


def episodesxseasons(item):
    logger.info()
    
    itemlist = list()
    infoLabels = item.infoLabels
    season = infoLabels["season"]
    
    soup = create_soup(item.url)
    matches = soup.find_all("tr", class_="Viewed")

    for elem in matches:
        url = elem.a["href"]
        epi = elem.find('span', class_='Num').text
        infoLabels["episode"] = epi
        infoLabels["mediatype"] = 'episode'
        title = "%sx%s - Episodio %s" % (season, epi, epi)
        
        itemlist.append(item.clone(title=title, url=url, action="findvideos", infoLabels=infoLabels))
    
    tmdb.set_infoLabels_itemlist(itemlist, True)
    
    return itemlist


def episodios(item):
    logger.info()
    
    itemlist = []
    
    templist = seasons(item)
    
    for tempitem in templist:
        itemlist += episodesxseasons(tempitem)
    
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, ignore_response_code=ignore_response_code).data
    patron = '"(\d{1})":"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for lang, url in matches:
        lang = IDIOMAS.get(lang, lang)
        import base64
        url = base64.b64decode(url).decode('utf-8')
        itemlist.append(item.clone(action = "play", title = "%s", language=lang, url = url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


# def play(item):
    # logger.info()
    # logger.debug("ITEM: %s" % item)
    
    # itemlist = []

    # if "pelisflix" in item.url:
        # url = create_soup(item.url).find(class_='Video').iframe['src']
    # else:
        # url = item.url
    
    # if "index.php?h=" in url:
        # id = scrapertools.find_single_match(url, r"\?h=([A-z0-9]+)")
        # post_url= "%sstream/r.php" % host
        # post = {'h' : id}
        # url = httptools.downloadpage(post_url, post=post, ignore_response_code=ignore_response_code, 
                                     # follow_redirects=False).headers.get('location', '')
    
    # if "vip/?url=" in url:
        # url = create_soup(url).iframe['src'].replace("embed.html#", "details.php?v=")
        # data = httptools.downloadpage(url, ignore_response_code=ignore_response_code).json
        # url = data['file']
    
    # if "byegoto" in url:
        # id = scrapertools.find_single_match(url, '=([^"]+)')
        # url = "%sbyegoto/rd.php" % host
        # post = {'url': id}
        # url = httptools.downloadpage(url, ignore_response_code=ignore_response_code, post=post).url
    
    # if "nuuuppp" in url:
       
        
        # server = "https://nuuuppp.pro/"
        # headers={"referer": server}
        # data = httptools.downloadpage(url, headers=headers).data
        # id = scrapertools.find_single_match(data, 'sesz="([^"]+)"')
        # url = "https://sv4.nupload.site/?s=%s" % id
        # url = httptools.downloadpage(url, headers=headers).url
        # url += "|Referer=%s" % server
        # url += "|Origin=https://nuuuppp.pro"
    
    # if "mega1080p" in url:
        # from lib import jsunpack
        # url = httptools.downloadpage(url, ignore_response_code=ignore_response_code).data
        # pack = scrapertools.find_single_match(url, "p,a,c,k,e,d.*?</script>")
        # unpack = jsunpack.unpack(pack).replace("\\", "")
        # url = scrapertools.find_single_match(unpack, "'file':'([^']+)'")
        # url = url.replace("/master", "/720/720p")
        # url = "https://pro.mega1080p.club/%s" %url
        # url += "|Referer=%s" %url
    
    # if "VIP" in server:
        # url = create_soup(url).find(class_='Video').iframe['src']
        # data = httptools.downloadpage(url, ignore_response_code=ignore_response_code).data
        # matches = re.compile("go_to_player\('([^']+)'\)", re.DOTALL).findall(data)
        # for url in matches:
            # itemlist.append(Item(channel=item.channel, title="%s", url=url, action="play", language=lang))
        # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server)
    # itemlist.append(['m3u', url])
    
    # return itemlist

