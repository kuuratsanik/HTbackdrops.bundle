SEARCH_ARTIST  = 'http://htbackdrops.com/api/TESTKEY/searchXML?keywords=%s&default_operator=and&limit=50&aid=1,5'
MUSIC_ART      = 'http://htbackdrops.com/api/TESTKEY/searchXML?keywords=%s&default_operator=and&limit=50&aid=1'
MUSIC_THUMBS   = 'http://htbackdrops.com/api/TESTKEY/searchXML?keywords=%s&default_operator=and&limit=50&aid=5'
THUMB_URL      = 'http://htbackdrops.com/api/TESTKEY/download/%s/thumbnail' # (max. width and height of 125px)
FULL_IMAGE_URL = 'http://htbackdrops.com/api/TESTKEY/download/%s/fullsize'  # (original full-size image)

def Start():
  HTTP.CacheTime = CACHE_1WEEK

class HTBDAgent(Agent.Artist):
  name = 'Home Theater Backdrops'
  languages = [Locale.Language.English]
  primary_provider = False
  contributes_to = ['com.plexapp.agents.lastfm']

  def search(self, results, media, lang):
    if media.primary_metadata is not None:
      artistName = String.StripDiacritics(media.primary_metadata.title).lower()
      previousName = ''

      for artist in XML.ElementFromURL(SEARCH_ARTIST % String.URLEncode(artistName)).xpath('//image/title/text()'):
        curName = String.StripDiacritics(artist).lower()
        if curName != previousName:
          score = 100 - Util.LevenshteinDistance(artistName, curName)
          results.Append(MetadataSearchResult(id = curName, score = score))
          previousName = curName

    results.Sort('score', descending=True)

  def update(self, metadata, media, lang):
    for s in [MUSIC_ART, MUSIC_THUMBS]:
      for id in XML.ElementFromURL(s % String.URLEncode(metadata.id)).xpath('//image/id/text()'):
        thumb = HTTP.Request(THUMB_URL % (id), cacheTime=CACHE_1MONTH)
        largeImgUrl = FULL_IMAGE_URL % id

        if s == MUSIC_ART:
          if largeImgUrl not in metadata.art:
            metadata.art[largeImgUrl] = Proxy.Preview(thumb)
        else:
          if largeImgUrl not in metadata.posters:
            metadata.posters[largeImgUrl] = Proxy.Preview(thumb)
