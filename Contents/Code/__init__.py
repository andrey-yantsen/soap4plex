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

episodes_cache              = None
episodes_cache_sid			= None

def Start():
	ObjectContainer.title1 = title1
	ObjectContainer.art = R(ART)

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
			dir.add(
				TVShowObject(
					key = Callback(show_seasons, show_id = id, soap_title = title),
					rating_key = str(id),
					title = title,
					summary = summary,
					art = fan,
					rating = float(rating),
					thumb = Resource.ContentsOfURLWithFallback(url=poster)
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
			dir.add(
				TVShowObject(
					key = Callback(show_seasons, show_id = id, soap_title = title),
					rating_key = str(id),
					title = title,
					summary = summary,
					art = fan,
					rating = float(rating),
					thumb = Resource.ContentsOfURLWithFallback(url=poster)
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
				title = items["title"]
				summary = items["description"]
				poster = 'http://covers.s4me.ru/soap/big/'+items["sid"]+'.jpg'
				rating = items["imdb_rating"]
				summary = summary.replace('&quot;','"')
				fan = 'http://thetvdb.com/banners/fanart/original/'+items['tvdb_id']+'-1.jpg'
				id = items["sid"]
				dir.add(
					TVShowObject(
						key = Callback(show_seasons, show_id = id, soap_title = soap_title, unwatched = 1),
						title = title,
						summary = summary,
						art = fan,
						rating = float(rating),
						rating_key = str(id),
						thumb = Resource.ContentsOfURLWithFallback(url=poster)
					)
				)
		return dir

def format_episode_list(show_id):
	global episodes_cache_sid, episodes_cache
	if episodes_cache_sid == show_id:
		return episodes_cache

	data = GET(API_URL + 'episodes/' + show_id)

	show_tree = {}
	for row in data:
		if not row['season'] in show_tree:
			show_tree[row['season']] = {
				'episodes': {},
				'id': row['season_id']
			}

		if not row['episode'] in show_tree[row['season']]['episodes']:
			show_tree[row['season']]['episodes'][row['episode']] = {
				'spoiler': row['spoiler'],
				'title_en': row['title_en'],
				'watched': row['watched'],
				'files': [
					{
						'id': row['eid'],
						'title_ru': row['title_ru'],
						'hash': row['hash'],
						'translate': row['translate'],
						'quality': row['quality']
					}
				]
			}
		else:
			ep = show_tree[row['season']]['episodes'][row['episode']]
			ep['watched'] = max(ep['watched'], row['watched'])
			ep['files'].append(
					{
						'id': row['eid'],
						'title_ru': row['title_ru'],
						'hash': row['hash'],
						'translate': row['translate'],
						'quality': row['quality']
					}
				)

	episodes_cache_sid = show_id
	episodes_cache = show_tree

	return show_tree

@route("/video/soap4me/show_seasons")
def show_seasons(show_id, soap_title, unwatched = 0):

	dir = ObjectContainer(
		title2 = soap_title,
		content = ContainerContent.Seasons
	)
	seasons = format_episode_list(show_id)
	unwatched_data = {x: min([int(v['episodes'][y]['watched'] != None) for y in seasons[x]['episodes']]) for x, v in seasons.items()}

	for row in sorted(seasons):
		if unwatched and unwatched_data[row] > 0:
			continue
		season_id = str(row)
		title = "Season %s" % (season_id)
		poster = "http://covers.s4me.ru/season/big/%s.jpg" % seasons[row]['id']
		dir.add(
			SeasonObject(
				key = Callback(show_episodes, show_id = show_id, season = season_id, unwatched = unwatched, soap_title = soap_title),
				title = title,
				index = int(row),
				rating_key = 'season_' + seasons[row]['id'],
				show = soap_title,
                thumb = Resource.ContentsOfURLWithFallback(url=poster),
			)
		)
	return dir

@route("/video/soap4me/show_episodes")
def show_episodes(show_id, season, soap_title, unwatched = 0):
	dir = ObjectContainer(
		title2 = u'список эпизодов',
		content = ContainerContent.Episodes
	)

	show_tree = format_episode_list(show_id)
	
	seasons_lengths = [len(show_tree[str(x)]['episodes']) for x in range(1, int(season) - 1)]
	episodes_cnt = reduce(lambda a, b: a + b, seasons_lengths, 0)
	
	for episode in sorted(show_tree[season]['episodes']):
		row = show_tree[season]['episodes'][episode]
		if row['watched'] != None and int(unwatched) == 1:
			continue
		else:
			title = row['title_en'].encode('utf-8').replace('&#039;', "'").replace("&amp;", "&").replace('&quot;','"')
			poster = "http://covers.s4me.ru/season/big/%s.jpg" % show_tree[season]['id']
			dir.add(
				EpisodeObject(
					key = Callback(play_video, show_id = show_id, season = season, episode = episode, soap_title = soap_title),
					rating_key = 'episode_' + str(show_id) + '_' + str(season) + '_' + str(episode),
			        title = title,
			        show = soap_title,
			        index = int(episode)
				)
			)

	return dir

@route("/video/soap4me/play_video")
def play_video(show_id, season, episode, soap_title, translation = None):
	show_tree = format_episode_list(show_id)

	info = show_tree[season]['episodes'][episode]
	season_id = show_tree[season]['id']

	poster = "http://covers.s4me.ru/season/big/%s.jpg" % season_id

	media_objects = []

	for i in info['files']:
		q = i['quality'].lower().rstrip('p')

		media_objects.append(MediaObject(
			parts = [
				PartObject(
					key = Callback(get_video_link, sid = show_id, eid = i['id'], ehash = i['hash'])
				)
			],
			video_codec = VideoCodec.H264,
			audio_codec = AudioCodec.AAC,
			container = Container.MP4,
			optimized_for_streaming = True,
			video_resolution = q
		))

	return ObjectContainer(
		title1 = soap_title,
		title2 = u'список эпизодов',
		content = ContainerContent.Episodes,
		objects = [
			EpisodeObject(
				key = Callback(play_video, show_id = show_id, season = season, episode = episode, soap_title = soap_title),
				rating_key = 'episode_' + str(show_id) + '_' + str(season) + '_' + str(episode),
				summary = info['spoiler'],
				title = info['title_en'],
				show = soap_title,
				season = int(season),
				index = int(episode),
				thumb = Resource.ContentsOfURLWithFallback(url=poster),
		        items = media_objects
			)
		]
	)

def get_video_link(eid, sid, ehash):
	token = Dict['token']
	myhash = hashlib.md5(str(token)+str(eid)+str(sid)+str(ehash)).hexdigest()
	params = {"what": "player", "do": "load", "token":token, "eid":eid, "hash":myhash}

	try:
		data = JSON.ObjectFromURL("http://soap4.me/callback/", params, headers = {'x-api-token': Dict['token'], 'Cookie': 'PHPSESSID='+Dict['sid']})
		if data["ok"] == 1:
			return Redirect("http://%s.soap4.me/%s/%s/%s/" % (data['server'], token, eid, myhash))
		else:
			Log(data)
			return None
	except Exception as e:
		return ObjectContainer(header=u"Ошибка", message=e)

def GET(url):
	return JSON.ObjectFromURL(url, headers = {'x-api-token': Dict['token']}, cacheTime = 0)

