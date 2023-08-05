import ox
import re
from ox.cache import read_url


def get_index():
    base = "http://smriti.com"
    url = base + "/hindi-songs/static-indexes/"
    data = read_url(url)
    movies = []
    for page in re.compile('<a href="(/hindi-songs/movies.*?)"').findall(data):
        url =  base + page
        data = read_url(url)
        movies += re.compile('<a href="(/hindi-songs/movie-.*?)"').findall(data)
    index = []
    for m in movies:
        url = base + m
        data = read_url(url).decode('utf-8', 'replace')
        movie = {}
        movie['url'] = url
        movie['title'] = re.compile('<h1>Songs of (.*?)</h1>').findall(data)[0]
        movie['songs'] = []
        for match in re.compile('<div class="onesong">(.*?):.*?<a href="(/hindi-songs/.*?utf8)">').findall(data):
            url = base + match[1].split('"')[-1]
            print url
            lyrics = read_url(url).decode('utf-8', 'replace')
            song = {
                'title': match[0],
                'url': url,
            }
            stats = re.compile("<ul class='pstats'>.*?</ul>", re.DOTALL).findall(lyrics)
            if stats:
                for kv in re.compile('<li><b>(.*?):</b>(.*?)</li>').findall(stats[0]):
                    song[kv[0].strip()] = ox.strip_tags(kv[1])
            lyrics = re.compile('<div class="songbody">(.*?)</div>', re.DOTALL).findall(lyrics)[0].strip()
            lyrics = lyrics[3:-4].replace('<br/>', '\n').replace('</p><p>', '\n\n').strip()
            song['lyrics'] = lyrics
            movie['songs'].append(song)
        index.append(movie)
    return index

if __name__ == '__main__':
    import json
    import codecs
    index = get_index()
    with codecs.open('/tmp/smriti.json', 'w', 'utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
