# -*- coding: utf-8 -*-

# created by sergio@pachini.ru
# updated by kestl1st@gmail.com (@kestl) v.1.2 2012-10-16

import re,urllib2,base64,hashlib,md5,urllib
import calendar
from datetime import *
import time

VERSION						= 1.2
VIDEO_PREFIX				= "/video/soap4me"
NAME						= 'soap4me'
ART							= 'art.png'
ICON						= 'icon.png'
BASE_URL					= 'http://soap4.me/'
API_URL						= 'http://soap4.me/api/'
LOGIN_URL					= 'http://soap4.me/login/'
USER_AGENT					= 'xbmc for soap'
LOGGEDIN					= False
TOKEN						= False
SID							= ''
title1						= NAME

def Start():
	ObjectContainer.title1 = title1
	ObjectContainer.art = R(ART)

	DirectoryItem.thumb = R(ICON)
	VideoItem.thumb = R(ICON)
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = USER_AGENT
	HTTP.Headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
	HTTP.Headers['Accept-Encoding'] ='gzip,deflate,sdch'
	HTTP.Headers['Accept-Language'] ='ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3'
	HTTP.Headers['x-api-token'] = TOKEN


def Login():
	global LOGGEDIN, SID, TOKEN

	if not Prefs['username'] and not Prefs['password']:
		return 2
	else:

		try:
			values = {
				'login' : Prefs["username"],
				'password' : Prefs["password"]}

			obj = JSON.ObjectFromURL(LOGIN_URL, values, encoding='utf-8', cacheTime=1,)
			#strn = JSON.StringFromObject(obj)
		except:
			obj=[]
			LOGGEDIN = False
			return 3
		SID = obj['sid']
		TOKEN = obj['token']
		if len(TOKEN) > 0:
			LOGGEDIN = True
			Dict['sid'] = SID
			Dict['token'] = TOKEN

			return 1
		else:
			LOGGEDIN = False
			Dict['sessionid'] = ""

			return 3


def Thumb(url):
	if url=='':
		return Redirect(R(ICON))
	else:
		try:
			data = HTTP.Request(url, cacheTime=CACHE_1WEEK).content
			return DataObject(data, 'image/jpeg')
		except:
			return Redirect(R(ICON))


@handler("/video/soap4me", NAME, ICON, ART)
def MainMenu():

	oc = ObjectContainer(objects = [
			DirectoryObject(
				key = Callback(Soaps),
				title=u"Все сериалы"
			),
			DirectoryObject(
				key = Callback(Watching),
				title=u"Я смотрю"
			),
			DirectoryObject(
				key = Callback(Unwatched),
				title=u"Новые эпизоды"
			),
			PrefsObject(
				title	= u"Настройки",
				thumb = R('settings.png')
			)
		])

	return oc


@route("/video/soap4me/soaps")
def Soaps():

	logged = Login()
	if logged == 2:
		return MessageContainer(
			"Ошибка",
			"Ведите пароль и логин"
		)

	elif logged == 3:
		return MessageContainer(
			"Ошибка",
			"Отказано в доступе"
		)
	else:

		dir = ObjectContainer(
			title2 = u'список сериалов',
			content = ContainerContent.Shows
		)
		url = API_URL + 'soap/'
		obj = GET(url)

		for items in obj:
			title = items["title"]
			summary = items["description"]
			poster = 'http://covers.s4me.ru/soap/big/'+items["sid"]+'.jpg'
			rating = items["imdb_rating"]
			summary = summary.replace('&quot;','"')
			fan = 'http://thetvdb.com/banners/fanart/original/'+items['tvdb_id']+'-1.jpg'
			id = items["sid"]
			thumb=Function(Thumb, url=poster)
			dir.add(
				DirectoryObject(
					key = Callback(show_seasons, id = id, soap_title = title),
					title = title,
					summary = summary,
					art = fan,
					rating = rating,
					infoLabel = '',
					thumb = thumb
				)
			)
		return dir

@route("/video/soap4me/watching")
def Watching():

	logged = Login()
	if logged == 2:
		return MessageContainer(
			"Ошибка",
			"Ведите пароль и логин"
		)

	elif logged == 3:
		return MessageContainer(
			"Ошибка",
			"Отказано в доступе"
		)
	else:
		dir = ObjectContainer(
			title2 = u'список сериалов',
			content = ContainerContent.Shows
		)
		url = API_URL + 'soap/my/'
		obj = GET(url)

		for items in obj:
			#Log.Debug('#####'+str(items).encode('utf-8')+'#####')
			title = items["title"]
			summary = items["description"]
			poster = 'http://covers.s4me.ru/soap/big/'+items["sid"]+'.jpg'
			rating = items["imdb_rating"]
			summary = summary.replace('&quot;','"')
			fan = 'http://thetvdb.com/banners/fanart/original/'+items['tvdb_id']+'-1.jpg'
			id = items["sid"]
			thumb=Function(Thumb, url=poster)
			dir.add(
				DirectoryObject(
					key = Callback(show_seasons, id = id, soap_title = title),
					title = title,
					summary = summary,
					art = fan
				)
			)
		return dir

@route("/video/soap4me/unwatched")
def Unwatched():

	logged = Login()
	if logged == 2:
		return MessageContainer(
			"Ошибка",
			"Ведите пароль и логин"
		)

	elif logged == 3:
		return MessageContainer(
			"Ошибка",
			"Отказано в доступе"
		)
	else:

		dir = ObjectContainer(
			title2 = u'список сериалов',
			content = ContainerContent.Shows
		)
		url = API_URL + 'soap/my/'
		obj = GET(url)

		for items in obj:
			if items["unwatched"]!=None:
				#Log.Debug('#####'+str(items).encode('utf-8')+'#####')
				soap_title = items["title"]
				title = items["title"]+ " (" +str(items["unwatched"])+ ")"
				summary = items["description"]
				poster = 'http://covers.s4me.ru/soap/big/'+items["sid"]+'.jpg'
				rating = items["imdb_rating"]
				summary = summary.replace('&quot;','"')
				fan = 'http://thetvdb.com/banners/fanart/original/'+items['tvdb_id']+'-1.jpg'
				id = items["sid"]
				dir.add(
					TVShowObject(
						key = Callback(show_seasons, id = id, soap_title = soap_title, unwatched = True),
						title = title,
						summary = summary,
						art = fan,
						rating = float(rating),
						rating_key = str(id),
						thumb = Resource.ContentsOfURLWithFallback(url=poster)
					)
				)
		return dir

@route("/video/soap4me/show_seasons")
def show_seasons(id, soap_title, unwatched = False):

	dir = ObjectContainer(
		title2 = soap_title,
		content = ContainerContent.Seasons
	)
	url = API_URL + 'episodes/'+id
	data = GET(url)
	season = {}
	useason = {}
	#Log.Debug('?????'+str(data).encode('utf-8')+'?????')

	if unwatched:
		for episode in data:
			if episode['watched'] == None:
				#Log.Debug(str(episode['episode']))
				if int(episode['season']) not in season:
					season[int(episode['season'])] = episode['season_id']
				if int(episode['season']) not in useason.keys():
					useason[int(episode['season'])] = []
					useason[int(episode['season'])].append(int(episode['episode']))
				elif int(episode['episode']) not in useason[int(episode['season'])]:
					useason[int(episode['season'])].append(int(episode['episode']))
	else:
		for episode in data:
			if int(episode['season']) not in season:
				season[int(episode['season'])] = episode['season_id']

	#Log.Debug(str(useason))

	for row in season:
		#info = {}
		title = "Season %s" % (str(row))
		season_id = str(row)
		poster = "http://covers.s4me.ru/season/big/%s.jpg"%season[row]
		dir.add(
			SeasonObject(
				key = Callback(show_episodes, sid = id, season = season_id, unwatched = unwatched),
				title = title,
				index = row,
				rating_key = str(id) + '_' + season_id,
				show = soap_title,
                thumb = Resource.ContentsOfURLWithFallback(url=poster),
			)
		)
	return dir

@route("/video/soap4me/show_episodes")
def show_episodes(sid, season, unwatched = False):
	dir = ObjectContainer(
		title2 = u'список эпизодов',
		content = ContainerContent.Episodes
	)
	url = API_URL + 'episodes/'+sid
	data = GET(url)
	quality = Prefs["quality"]
	#episode_names = {}
	show_only_hd = False

	if quality == "HD":
		for episode in data:
			if season == episode['season']:
				if episode['quality'] == '720p':
					show_only_hd = True
					break
	Log(data)
	for row in data:
		if season == row['season']:

			if quality == "HD" and show_only_hd == True and row['quality'] != '720p':
				continue
			elif quality == "SD" and show_only_hd == False and row['quality'] != 'SD':
				continue
			else:
				if row['watched'] != None and unwatched:
					continue
				else:
					eid = row["eid"]
					ehash = row['hash']
					sid = row['sid']
					title = row['title_en'].encode('utf-8').replace('&#039;', "'").replace("&amp;", "&").replace('&quot;','"')
					poster = "http://covers.s4me.ru/season/big/%s.jpg"%row['season_id']
					summary = row['spoiler']
					dir.add(
						EpisodeObject(
							key = Callback(play_video, eid = eid, sid = sid, ehash = ehash),
							rating_key = ehash,
					        title = title,
					        thumb = Resource.ContentsOfURLWithFallback(url=poster),
					        summary = summary
						)
					)

	return dir

@route("/video/soap4me/play_video")
def play_video(sid, eid, ehash):
	token = Dict['token']

	myhash = hashlib.md5(str(token)+str(eid)+str(sid)+str(ehash)).hexdigest()
	params = {"what": "player", "do": "load", "token":token, "eid":eid, "hash":myhash}

	try:
		data = JSON.ObjectFromURL("http://soap4.me/callback/", params, headers = {'x-api-token': Dict['token'], 'Cookie': 'PHPSESSID='+Dict['sid']})
		if data["ok"] == 1:
			return ObjectContainer(
				title2 = u'список эпизодов',
				content = ContainerContent.Episodes,
				objects = [
					EpisodeObject(
						key = Callback(play_video, eid = eid, sid = sid, ehash = ehash),
						rating_key = ehash,
						summary = "summary",
						title = "title",
						show = "show",
						absolute_index = 13,
				        items = [
				        	MediaObject(
								parts = [
									PartObject(
										key = "http://%s.soap4.me/%s/%s/%s/" % (data['server'], token, eid, myhash)
									)
								],
								video_codec = VideoCodec.H264,
								audio_codec = AudioCodec.AAC,
								container = Container.MP4
				    		)
				        ]
					)
				]
			)
		else:
			Log(data)
			return None
	except Exception as e:
		return MessageContainer(
			u"Ошибка",
			e
		)

def GET(url):
	return JSON.ObjectFromURL(url, headers = {'x-api-token': Dict['token']}, cacheTime = 0)

