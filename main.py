import json
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

SONG_COUNT_PER_PAGE = 50

chrome_options = webdriver.ChromeOptions()
chrome_options.headless = True

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# TODO: Argument로 빼기
song_title = '가을'
song_section = 'song'   # 곡명으로 검색
song_genre = 'GN0101'   # 발라드

print(f'멜론에서 제목에 "{song_title}"이 들어간 발라드 장르 노래들의 가사를 파싱합니다.')

song_ids = []

print('[START] 멜론 곡명 검색 결과 페이지로부터 song_id 파싱')
page = 0
while True:
    print(f'  페이지 {page} ...', end=' ')

    start_index = page * SONG_COUNT_PER_PAGE + 1

    url = f'https://www.melon.com/search/song/index.htm?q={song_title}&section={song_section}&searchGnbYn=Y&kkoSpl=N#params%5Bq%5D={song_title}&params%5Bsort%5D=ganada&params%5Bsection%5D={song_section}&params%5BgenreDir%5D={song_genre}&params%5BmwkLogType%5D=T&po=pageObj&startIndex={start_index}'
    driver.get(url)
    driver.implicitly_wait(2)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    song_trs = soup.find(id='frm_defaultList').find_all('tr')
    for tr in song_trs:
        try:
            song_attr = tr.a['href']
            song_id_criteria = 'goSongDetail'
            song_id = song_attr[song_attr.find(song_id_criteria) + len(song_id_criteria) + 2:-3]
            song_ids.append(song_id)
        except:
            continue
    
    print('완료')

    if len(song_ids) % 50 != 0:
        break
    else:
        page += 1

driver.close()
print(f'[END] 멜론 곡명 검색 결과 페이지로부터 song_id 파싱 (총 {len(song_ids)}곡)')

http_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache'
}

print('[START] 곡 상세 페이지(song_id 이용)에서 노래 가사 파싱')
songs = []
for song_id in song_ids:
    url = f'https://www.melon.com/song/detail.htm?songId={song_id}'
    page_html = requests.get(url, headers=http_headers).text

    soup = BeautifulSoup(page_html, 'html.parser')

    info_form = soup.find(id='downloadfrm')
    title = info_form.find('div', {'class':'song_name'}).text.replace('곡명', '', 1).strip()
    artist = info_form.find('div', {'class':'artist'}).text.strip()

    try:
        lyric_lines = soup.find(id='d_video_summary').stripped_strings
        lyric = ' '.join(lyric_lines)
    except:
        # 가사가 없는 경우
        lyric = ''

    # print('URL:', url)
    # print('곡명:', title)
    # print('아티스트:', artist)
    # print('노래 가사:', lyric)

    songs.append({
        'id': song_id,
        'title': title,
        'artist': artist,
        'lyric': lyric,
        'url': url
    })

print('[END] 곡 상세 페이지(song_id 이용)에서 노래 가사 파싱')

print('[START] 결과 파일 생성')
with open(f'./output_{song_title}.json', 'w', encoding='utf-8') as outfile:
    json.dump(songs, outfile, indent=4)

print('END] 결과 파일 생성')
