import requests
from bs4 import BeautifulSoup

# TODO: Argument로 빼기
sont_title = '꽃송이가'

print('곡 제목:', sont_title)

http_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}
search_result = requests.get(f'https://www.melon.com/search/total/index.htm?q={sont_title}', headers=http_headers).text

soup = BeautifulSoup(search_result, 'html.parser')

# 리스트의 첫 번째 결과 선택
song_attr = soup.find(id='frm_searchSong').a['href']
criteria = 'goSongDetail'
song_id = song_attr[song_attr.find(criteria) + len(criteria) + 2:-3]
print('곡 ID:', song_id)

# 곡 상세 정보
song_detail = requests.get(f'https://www.melon.com/song/detail.htm?songId={song_id}', headers=http_headers).text
soup = BeautifulSoup(song_detail, 'html.parser')

lyric_lines = soup.find(id='d_video_summary').stripped_strings
lyric = ' '.join(lyric_lines)

print('가사:', lyric)
