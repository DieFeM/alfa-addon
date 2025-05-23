# -*- coding: utf-8 -*-
# Channel Playdede
# Created for Alfa addon
# By the Alfa Development Group
# Maintained by SistemaRayoXP
import re

from bs4 import BeautifulSoup
from core import httptools, scrapertools, servertools, tmdb, urlparse
from core.item import Item
from platformcode import config, logger, platformtools, unify
from channelselector import get_thumb
from modules import filtertools
from modules import autoplay


IDIOMAS = {"lat": "LAT", "esp": "CAST", "espsub": "VOSE", "engsub": "VOS", "eng": "VO"}

# <option value="9204">USERLOAD</option><option value="8591">UPLOADHUB</option><option value="18">FILEFOX</option>
# <option value="6186">STREAMRUBY</option><option value="653">ROSEFILE</option>
# <option value="714"><SPAN STYLE="FONT-WEIGHT: 700;FONT-SIZE: 18PX;COLOR:#FFD699">RECOMENDADO</SPAN></option>
# <option value="22">MEXA</option><option value="1001">FASTCLICK</option><option value="1002">DROPAPK</option>
# <option value="27">NITROFLARE</option><option value="34">ROCKFILE</option><option value="24">KATFILE</option>
# <option value="62">STREAMABLE</option><option value="64">ABCVIDEO</option>
# <option value="66">DDOWNLOAD</option><option value="999">ALTERNATIVO</option>

# <option value="1">POWVIDEO</option><option value="1000">POWVIDEO</option><option value="7701">FILEMOON</option><option value="9201">VOE</option>
# <option value="7561">STREAMWISH</option><option value="153">FILELIONS</option><option value="1195">STREAMVID</option>
# <option value="6183">VTUBE</option><option value="6187">VEMBED</option><option value="901">DIRECTO</option>
# <option value="2">STREAMPLAY</option><option value="70">STREAMPLAY</option><option value="10">RAPIDGATOR</option>
# <option value="4">UPSTREAM</option><option value="5">CLOUDVIDEO</option><option value="12">GAMOVIDEO</option>
# <option value="14">VIDLOX</option><option value="7565">MP4UPLOAD</option><option value="9202">ZPLAYER</option>
# <option value="15">MIXDROP</option><option value="1010">MIXDROP</option><option value="8">FILEFACTORY</option>
# <option value="23">1FICHIER</option><option value="45">WAAW</option><option value="51">STREAMTAPE</option>
# <option value="52">MEGA</option><option value="55">OKRU</option><option value="56">DOODSTREAM</option>
# <option value="57">EVOLOAD</option><option value="6656">VIDMOLY</option><option value="54">YOURUPLOAD</option>
# <option value="31">VIDOZA</option><option value="32">TURBOBIT</option><option value="38">CLICKNUPLOAD</option>
# <option value="65">HEXUPLOAD</option><option value="53">UQLOAD</option>


SERVIDORES = {
    "11": "clipwatching",
    "57": "evoload",
    "12": "gamovideo",
    "56": "doodstream",
    "54": "yourupload",
    "4": "upstream",
    "5": "cloudvideo",
    "55": "okru",
    "1": "powvideo",
    "2": "streamplay",
    "70": "streamplay",
    "15": "mixdrop",
    "1010": "mixdrop",
    "14": "vidlox",
    "7565": "mp4upload",
    "50": "fembed",
    "6656": "vidmoly",
    "45": "netutv",
    "51": "streamtape",
    "9201": "voe",
    "7701": "filemoon",
    "6183": "playtube",
    "7561": "streamwish",
    "153": "vidhidepro",
    "10": "rapidgator",
    "1195": "streamvid",
    "6187": "vidguard",
    "9202": "zplayer",
    "8": "filefactory",
    "23": "1fichier",
    "52": "mega",
    "31": "vidoza",
    "32": "turbobit",
    "38": "clicknupload",
    "65": "hexupload",
    "53": "uqload",
    "8777": "dailyuploads",
    "24": "katfile",
    "27":  "nitroflare",
    "7567": "ouo",
    "52654": "uploady",
    "9204": "userload",
    "66": "ddownload",
    "1002": "dropark",
    "1001": "fastclick",
    "filelions": "vidhidepro",
    "filemoon": "filemoon",
    "luluvideo": "lulustream",
    "vembed": "vidguard",
    "bigwarp": "tiwikiwi",
    "waaw": "netu",
    "voe": "voe",
    "streamwish": "streamwish",
    "powvideo": "powvideo",
    "streamplay": "streamplay",
    "streamtape": "streamtape",
    "vtube": "playtube",
    "streamsilk": "streamsilk",
    "vidmoly": "vidmoly",
    "doodstream": "doodstream",
}

list_language = list(IDIOMAS.values())
list_quality = ["HD1080", "HD720", "HDTV", "DVDRIP"]
list_quality_tvshow = list_quality_movies = list_quality
list_servers = list(set(SERVIDORES.values()))

# https://entrarplaydede.com/

host = "https://www8.playdede.link/"
assistant = config.get_setting(
    "assistant_version", default=""
) and not httptools.channel_proxy_list(host)

canonical = {
    "channel": "playdede",
    "host": config.get_setting("current_host", "playdede", default=""),
    "host_alt": [host],
    "host_black_list": [
        "https://www7.playdede.link/", "https://www6.playdede.link/",
        "https://www5.playdede.link/", "https://www4.playdede.link/", "https://www3.playdede.link/",
        "https://www2.playdede.link/", "https://playdede.in/", "https://playdede.me/",
        "https://playdede.eu/", "https://playdede.us/", "https://playdede.to/",
        "https://playdede.nu/", "https://playdede.org/", "https://playdede.com/",
    ],
    "pattern": '<link\s*rel="shortcut\s*icon"[^>]+href="([^"]+)"',
    "set_tls": True,
    "set_tls_min": True,
    "retries_cloudflare": 1,
    "CF_stat": True if assistant else False,
    "session_verify": True if assistant else False,
    "CF_if_assistant": True if assistant else False,
    "CF_if_NO_assistant": False,
    "CF": False,
    "CF_test": False,
    "alfa_s": True,
}
host = canonical["host"] or canonical["host_alt"][0]
__channel__ = canonical["channel"]

timeout = 30
show_langs = config.get_setting("show_langs", channel=__channel__)
account = None


def get_source(
    url, json=False, soup=False, multipart_post=None, timeout=30, add_host=True, **opt
):
    logger.info()

    opt["canonical"] = canonical
    data = httptools.downloadpage(
        url, soup=soup, files=multipart_post, add_host=add_host, timeout=timeout, **opt
    )

    # Verificamos que tenemos una sesión válida, sino, no tiene caso devolver nada
    if "Iniciar sesión" in data.data:
        # Si no tenemos sesión válida, mejor cerramos definitivamente la sesión
        remove_cookies()
        global account
        if account:
            logout({})
        platformtools.dialog_notification(
            "No se ha inciado sesión",
            "Inicia sesión en el canal {} para poder usarlo".format(__channel__),
        )
        return None

    if json:
        data = data.json
    elif soup:
        data = data.soup
    else:
        data = data.data

    return data


def remove_cookies():
    # Borramos las cookies
    try:
        httptools.cj.clear()
        httptools.save_cookies()
    except Exception:
        pass


def login():
    logger.info()
    remove_cookies()
    
    usuario = config.get_setting("user", channel=__channel__)
    clave = config.get_setting("pass", channel=__channel__)
    credentials = (
        ("user", (None, usuario)),
        ("pass", (None, clave)),
        ("_method", (None, "auth/login")),
    )

    if not usuario:
        logger.error("No se ingresó un nombre de usuario")
        return False

    if not clave:
        platformtools.dialog_notification(
            "Falta la contraseña",
            "Revisa la contraseña en la configuración del canal.",
            sound=False,
        )
        logger.error("No se ingresó una contraseña")
        return False

    if not httptools.get_cookie(host, "MoviesWebsite"):
        httptools.downloadpage(host, timeout=timeout, canonical=canonical)

    if httptools.get_cookie(host, "utoken"):
        return True

    logger.info("Iniciando sesión...")

    httptools.downloadpage(
        "{}ajax.php".format(host),
        files=credentials,
        add_referer=True,
        add_host=True,
        timeout=timeout,
        canonical=canonical,
    )
    httptools.downloadpage(host, timeout=timeout, canonical=canonical)

    if httptools.get_cookie(host, "utoken"):
        logger.info("¡Token de sesión conseguido!")
        platformtools.dialog_notification(
            "Sesión iniciada satisfactoriamente", "Disfruta del canal :)", sound=False
        )
        return True
    else:
        logger.error("¡Ouh! Parece que no hay token de inicio de sesión, reparar...")
        platformtools.dialog_notification(
            "Error al iniciar sesión",
            "Verifica que el usuario y contraseña sean correctos y que puedas iniciar sesión en la web. Si están correctos, genera un reporte desde el menú principal",
            sound=False,
        )
        return False


def logout(item):
    logger.info()

    # Borramos las cookies
    try:
        domain = urlparse.urlparse(host).netloc
        httptools.cj.clear(domain)
        httptools.save_cookies()
    except Exception:
        pass

    # Borramos el estado de login
    config.set_setting("user", "", channel=__channel__)
    config.set_setting("pass", "", channel=__channel__)

    platformtools.dialog_notification(
        "Sesión cerrada", "Reconfigura las credenciales", sound=False
    )

    # Mandamos a configuración del canal
    return platformtools.itemlist_refresh()


account = login()


def mainlist(item):
    logger.info()

    itemlist = []
    global account

    if not account:
        platformtools.dialog_notification(
            "Registro necesario",
            "Regístrate en playdede.com e ingresa tus credenciales para utilizar este canal",
            sound=False,
        )
        itemlist.append(
            Item(
                action="settings",
                channel=item.channel,
                folder=False,
                text_bold=True,
                thumbnail=get_thumb("setting_0.png"),
                title="Debes iniciar sesión para utilizar este canal",
            )
        )

    else:
        autoplay.init(item.channel, list_servers, list_quality)
        itemlist.append(
            Item(
                action="list_all",
                channel=item.channel,
                fanart=item.fanart,
                thumbnail=get_thumb("movies", auto=True),
                title="Películas",
                url="{}peliculas/".format(host),
                viewType="movies",
            )
        )
        itemlist.append(
            Item(
                action="list_all",
                channel=item.channel,
                fanart=item.fanart,
                thumbnail=get_thumb("tvshows", auto=True),
                title="Series",
                url="{}series/".format(host),
                viewType="tvshows",
            )
        )
        itemlist.append(
            Item(
                action="list_all",
                channel=item.channel,
                fanart=item.fanart,
                thumbnail=get_thumb("animacion", auto=True),
                title="Animación",
                url="{}animes/".format(host),
                viewType="tvshows",
            )
        )
        itemlist.append(
            Item(
                action="genres",
                channel=item.channel,
                fanart=item.fanart,
                thumbnail=get_thumb("colections", auto=True),
                title="Listas",
                url="{}listas/".format(host),
                viewType="videos",
            )
        )
        itemlist.append(
            Item(
                action="search",
                channel=item.channel,
                fanart=item.fanart,
                thumbnail=get_thumb("search", auto=True),
                title="Buscar",
                url=host,
                viewType="movies",
            )
        )
        itemlist.append(
            Item(
                action="logout",
                channel=item.channel,
                folder=False,
                plot="Cierra la sesión",
                title="Cerrar sesión",
                thumbnail=get_thumb("setting_0.png"),
            )
        )
        itemlist.append(
            Item(
                action="settings",
                channel=item.channel,
                folder=False,
                plot="Configura tus credenciales, búsqueda global, etc.",
                title="Configurar canal",
                thumbnail=get_thumb("setting_0.png"),
            )
        )
        itemlist = filtertools.show_option(
            itemlist,
            item.channel,
            list_language,
            list_quality_tvshow,
            list_quality_movies,
        )
        autoplay.show_option(item.channel, itemlist)
    return itemlist


def settings(item):
    logger.info()

    platformtools.show_channel_settings()
    platformtools.itemlist_refresh()

    return


def genres(item):
    logger.info()

    itemlist = []
    soup = get_source(item.url, soup=True)
    if not soup:
        return []

    if not soup:
        platformtools.dialog_notification(
            "Cambio de estructura",
            "Reporta el error desde el menú principal",
            sound=False,
        )

        return itemlist

    items = soup.find("div", id="movidyMain").find_all("article")

    for article in items:
        try:
            data = article.find("a", attrs={"up-target": "body"})
            fanart = article.find(class_="postersMov").find_all("img")[1]["src"]
            thumb = article.find(class_="postersMov").find("img")["src"]
            title = data.find("h2").text
            plot = "[COLOR=green]Creado por:[/COLOR] {}\n[COLOR=red]Corazones:[/COLOR] {}".format(
                article.find(class_="kcdirs").span.text,
                article.find("div", class_="createdbyT").span.text,
            )
            url = data["href"]
            url = "{}%s".format(host) % url

            it = item.clone(
                action="list_all",
                fanart=fanart,
                plot=plot,
                thumbnail=thumb,
                title=title,
                tmdb=False,
                url=url,
            )

            itemlist.append(it)
        except Exception:
            pass

    btnnext = soup.find("div", class_="pagPlaydede")

    if btnnext:
        itemlist.append(item.clone(title="Siguiente >", url=btnnext.find("a")["href"]))

    return itemlist


def list_all(item):
    logger.info()
    
    itemlist = []
    soup = get_source(item.url, soup=True)
    if not soup:
        platformtools.dialog_notification(
            "Cambio de estructura",
            "Reporta el error desde el menú principal",
            sound=False,
        )
        return itemlist
    
    items = soup.find_all("article", id=re.compile(r"^post-(?:\d+|)"))
    # items = soup.find('div', id=' archive-content').find_all('article')
    
    shown_half = 1 if item.half else 0
    items_half = len(items) // 2
    items = items[items_half:] if shown_half == 1 else items[:items_half]
    
    for article in items:
        data = article.find("div", class_="data")
        year = data.find("p").text
        year = scrapertools.find_single_match(year, "(\d{4})")
        infoLabels = {"year": year, "genres": data.find("span").text}
        thumbnail = article.find("img")["src"]
        title = data.find("h3").text
        url = article.find("a")["href"]
        url = "{}%s".format(host) % url
        
        """
        if 'tmdb.org' in thumbnail:
            infoLabels['filtro'] = scrapertools.find_single_match(thumbnail, "/(\w+)\.\w+$")
        """
        
        it = Item(
            action="findvideos",
            channel=item.channel,
            fanart=item.fanart,
            infoLabels=infoLabels,
            thumbnail=thumbnail,
            title=title,
            url=url,
        )
        
        it.context = filtertools.context(it, list_language, list_quality)
        it.context.extend(autoplay.context)
        
        if "serie" in it.url or "anime" in it.url:
            c_type = "tvshows"
        
        elif "pelicula" in it.url:
            c_type = "movies"
        
        else:
            c_type = "tvshows"
        
        if c_type == "tvshows":
            it.action = "seasons"
            it.contentSerieName = title
            it.contentType = "tvshow"
            it.viewType = "episodes"
        
        elif c_type == "movies":
            it.contentTitle = title
            it.contentType = "movie"
            it.viewType = "movies"
        
        itemlist.append(it)
    
    if not isinstance(item.tmdb, bool) or item.tmdb is not False:
        tmdb.set_infoLabels(itemlist, True)
    
    btnnext = soup.find("div", class_="pagPlaydede").find_all('a')
    
    if shown_half == 0:
        itemlist.append(item.clone(title="Siguiente >", half=1))
    elif btnnext:
        btnnext = btnnext[-1]['href']
        itemlist.append(item.clone(title="Siguiente >", half=0, url=btnnext))
    
    return itemlist


def search(item, texto):
    logger.info()

    try:
        if texto:
            item.url = "{}search/?s={}".format(host, urlparse.quote_plus(texto))

            return list_all(item)

        else:
            return

    except Exception:
        # Se captura la excepción, para no interrumpir al buscador global si un canal falla
        import traceback

        logger.error(traceback.format_exc())

        return []


def seasons(item):
    logger.info()

    itemlist = []
    soup = get_source(item.url, soup=True)
    if not soup:
        return []
    items = soup.find("div", id="seasons").find_all("div", class_="se-c")

    for div in items:
        try:
            season = int(div["data-season"])
        except ValueError:
            season = 1

        itemlist.append(
            item.clone(
                action="episodesxseason",
                contentSeason=season,
                episode_data=str(div),
                contentType="season",
                title=config.get_localized_string(60027) % season,
            )
        )

    tmdb.set_infoLabels(itemlist, True)

    return itemlist


def episodios(item):
    logger.info()

    itemlist = []
    templist = seasons(item)

    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item):
    logger.info()

    itemlist = []
    soup = BeautifulSoup(item.episode_data, "html5lib", from_encoding="utf-8")
    items = soup.find("ul", class_="episodios").find_all("li")

    for li in items:
        episode = scrapertools.find_single_match(
            li.find("div", class_="numerando").text, "\d+ - (\d+)"
        )
        infoLabels = item.infoLabels
        infoLabels["episode"] = episode
        title = "{}x{} - {}".format(
            item.contentSeason, episode, li.find("div", class_="epst").text
        )
        url = li.find("a")["href"]
        url = "{}%s".format(host) % url

        itemlist.append(
            Item(
                action="findvideos",
                channel=item.channel,
                contentEpisode=episode,
                infoLabels=infoLabels,
                thumbnail=li.find("img")["src"],
                title=title,
                url=url,
            )
        )

    tmdb.set_infoLabels(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    
    soup = get_source(item.url, soup=True)
    if not soup:
        return []
    matches = []
    
    matches = soup.findAll("div", class_="playerItem")
    descargas = soup.findAll("div", class_="linkSorter")
    for lst in descargas:
        matches.extend(lst.find_all("li"))
    # logger.debug(matches)
    
    for elem in matches:
        if not elem.find(class_='reportLink'): continue
        quality = ""
        server = ""
        language = IDIOMAS.get(elem.get("data-lang", "").lower(), "")
        quality = elem.get("data-quality", "")
        player=elem.get("data-loadplayer", "")
        
        if quality:
            url = elem.find("a")["href"]
            server = SERVIDORES.get(elem.get("data-provider", ""), "")
            if not server:
                server = elem.span.b.text
                server = SERVIDORES.get(server.lower(), "")
            # logger.debug(url +"      "+ elem.get("data-provider"))
        else:
            data = elem.find("div", class_="meta")
            
            if data:
                quality = data.p.span.text
                server = data.find("h3").text
                server = SERVIDORES.get(server.lower(), "")
                url = "%sembed.php?id=%s" % (host, player)
            # logger.debug(url +"      "+ server)
        
        itemlist.append(
            item.clone(
                action="play",
                language=language,
                # player=player,
                quality=quality,
                server=server,
                # title=title,
                url=url,
            )
        )
    
    # Ordenar por language
    itemlist.sort(key=lambda x: x.language)
    
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    
    return itemlist


def play(item):
    logger.info()

    if host in item.url:
        data = get_source(item.url)
        item.url = scrapertools.find_single_match(data, 'var url\s*=\s*"([^"]+)"')
    
    devuelve = servertools.findvideosbyserver(item.url, item.server)
    if devuelve:
        #Sonic3 vidmoly     https://vidmoly.me/w/6etlw26o0hgu  >>  https://vidmoly.me/6etlw26o0hgu.html
        #DESACTICVADO por captcha el server streamplay  https://streamplay.to/embed-gumabp75uwfi-960x580.html >> https://stre4mplay.one/gumabp75uwfi
        #MUSAFA  playtube    https://vtube.network/embed-hilj6t7313oy.html >> https://vtbe.to/hilj6t7313oy.html
        item.url =  devuelve[0][1]
    
    return [item]
