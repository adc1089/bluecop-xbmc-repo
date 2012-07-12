import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re

import demjson
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
from pyamf.remoting.client import RemotingService
import resources.lib._common as common

pluginhandle = int (sys.argv[1])
BASE_URL = 'http://feed.theplatform.com/f/AqNl-B/7rsRlZPHdpCt/categories?&form=json&fields=order,title,fullTitle,label&fileFields=duration,url,width,height&sort=order'
BASE = 'http://www.oxygen.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    data = common.getURL(BASE_URL)
    shows = demjson.decode(data)['entries']
    db_shows = []
    for item in shows:
        print item
        url = item['plcategory$fullTitle']
        name = item['title']
        if db==True:
            db_shows.append((name,'oxygen','showroot',url))
        else:
            common.addShow(name, 'oxygen', 'showroot', url)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')

def showroot():
    common.addDirectory('Full Episodes', 'oxygen', 'episodes', common.args.url)
    common.addDirectory('All Videos', 'oxygen', 'allvideos', common.args.url)
    common.setView('seasons')

def allvideos():
    process('http://feed.theplatform.com/f/AqNl-B/iyAsU_4kQn1I')
    common.setView('episodes')
    
def episodes():
    process('http://feed.theplatform.com/f/AqNl-B/iLe_F3t4pzHB')
    common.setView('episodes')

def process(urlBase, fullname = common.args.url):
    #url = 'http://feed.theplatform.com/f/AqNl-B/iyAsU_4kQn1I'
    url = urlBase
    url += '?form=json'
    url += '&fields=guid,title,description,categories,content,defaultThumbnailUrl'#,:fullEpisode
    url += '&fileFields=duration,url,width,height'
    url += '&count=true'
    url += '&byCategories='+urllib.quote_plus(fullname)
    #url += '&byCustomValue={fullEpisode}{false}'
    data = common.getURL(url)
    episodes = demjson.decode(data)['entries']
    for episode in episodes:
        name = episode['title']
        description = episode['description']
        thumb= episode['plmedia$defaultThumbnailUrl']
        duration=str(int(episode['media$content'][0]['plfile$duration']))
        url=episode['media$content'][0]['plfile$url']
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="oxygen"'
        u += '&sitemode="play"'
        infoLabels={ "Title":name,
                     #"Season":season,
                     #"Episode":episode,
                     "Plot":description,
                     #"premiered":airDate,
                     "Duration":duration,
                     "TVShowTitle":common.args.name
                     }
        common.addVideo(u,name,thumb,infoLabels=infoLabels)

#Get SMIL url and play video
def play():
    smilurl=common.args.url
    swfUrl = 'http://features.oxygen.com/videos/pdk/swf/flvPlayer.swf'
    data = common.getURL(smilurl)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    print tree.prettify()
    rtmpbase = tree.find('meta')
    if rtmpbase:
        rtmpbase = rtmpbase['base']
        items=tree.find('switch').findAll('video')
        hbitrate = -1
        sbitrate = int(common.settings['quality']) * 1024
        for item in items:
            bitrate = int(item['system-bitrate'])
            if bitrate > hbitrate and bitrate <= sbitrate:
                hbitrate = bitrate
                playpath = item['src']
                if '.mp4' in playpath:
                    playpath = 'mp4:'+playpath
                else:
                    playpath = playpath.replace('.flv','')
                finalurl = rtmpbase+' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
    else:
        items=tree.find('switch').findAll('video')
        hbitrate = -1
        sbitrate = int(common.settings['quality']) * 1024
        for item in items:
            bitrate = int(item['system-bitrate'])
            if bitrate > hbitrate and bitrate <= sbitrate:
                hbitrate = bitrate
                finalurl = item['src']
    item = xbmcgui.ListItem(path=finalurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
