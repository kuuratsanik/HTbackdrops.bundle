import unicodedata

HTBD_BASEURL = 'http://htbackdrops.com/'
HTBD_SEARCH_MUSIC_ART  = HTBD_BASEURL + 'search.php?search_keywords=%s&search_terms=all&cat_id=1&search_fields=all'
HTBD_SEARCH_MUSIC_THUMBS  = HTBD_BASEURL + 'search.php?search_keywords=%s&search_terms=all&cat_id=5&search_fields=all'

def Start():
  HTTP.CacheTime = CACHE_1DAY
  #adjust images per page
  #x = str(HTTP.Request(HTBD_BASEURL + 'search.php', values={'setperpage':'30','submit':'Go'}))
  
class HTBDAgent(Agent.Artist):
  name = 'Home Theater Backdrops'
  languages = [Locale.Language.English]
  primary_provider = False
  contributes_to = ['com.plexapp.agents.lastfm']
  
  def search(self, results, media, lang):
    if media.primary_metadata is not None:
      query = String.URLEncode(self.stripAccents(media.primary_metadata.title))
      Log(query)
      #try:
      previousName = ''
      for img in HTML.ElementFromURL(HTBD_SEARCH_MUSIC_ART % query).xpath('//img[contains(@src,"./data/thumbnails")]'):
        Log(HTML.StringFromElement(img))
        curName = img.get('alt')
        if curName != previousName:
          score = 100 - Util.LevenshteinDistance(media.primary_metadata.title.lower(), curName.lower())
          results.Append(MetadataSearchResult(id = curName, score = score))
      #except:
    results.Sort('score', descending=True)
    
  def update(self, metadata, media, lang):
    for s in [HTBD_SEARCH_MUSIC_ART, HTBD_SEARCH_MUSIC_THUMBS]:
      i = 0
      for img in HTML.ElementFromURL(s % String.URLEncode(self.stripAccents(metadata.id))).xpath('//img[contains(@src,"./data/thumbnails")]'):
        if self.stripAccents(img.get('alt')).lower() == self.stripAccents(metadata.id).lower():
          i += 1
          thumbUrl = img.get('src').replace('./',HTBD_BASEURL)
          thumb = HTTP.Request(thumbUrl)
          largeImgUrl = thumbUrl.replace('thumbnails','media')
          if s == HTBD_SEARCH_MUSIC_ART:
            metadata.art[largeImgUrl] = Proxy.Preview(thumb, sort_order = i)
          else:
            metadata.posters[largeImgUrl] = Proxy.Preview(thumb, sort_order = i)

  def stripAccents(self, str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(str))
    only_ascii = nkfd_form.encode('ASCII', 'ignore')
    return only_ascii
