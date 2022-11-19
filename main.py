import argparse
import csv
import json
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from typing import List
from webdriver_manager.chrome import ChromeDriverManager

# Constants
PROG_VERSION = '1.0'


# TODO: 멜론은 제대로 검색되지 않는 문제가 있음. (예. "가을"을 검색하면 "가을이", "가을에" 이런 것들 검색 안됨.)
# TODO: 따라서 이와 같이 여러개를 검색해야 함 -> 가을, 가을과, 가을에, 가을은, 가을을, 가을의, 가을이
def __extract_song_ids(keyword: str, section: str, genre: str):
    print(f'[START] 멜론 곡 ID 목록 추출 (키워드: [{keyword}], 방법: [{section}], 장르: [{genre}])')

    # 검색 결과 페이지당 결과 수
    song_count_per_page = 50
    
    song_ids = []

    # Init Google Chrome Driver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    page = 1
    while True:
        start_index = (page - 1) * song_count_per_page + 1
        print(f'  - 검색 결과 {page}페이지 스크래핑')

        url = f'https://www.melon.com/search/song/index.htm?q={keyword}&section={section}&searchGnbYn=Y&kkoSpl=N#params%5Bq%5D={keyword}&params%5Bsort%5D=ganada&params%5Bsection%5D={section}&params%5BgenreDir%5D={genre}&params%5BmwkLogType%5D=T&po=pageObj&startIndex={start_index}'
        driver.get(url)

        # 너무 빠르게 검색하면 결과가 제대로 파싱되지 않으므로 명시적으로 sleep time을 준다.
        driver.implicitly_wait(2)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        song_trs = soup.find(id='frm_defaultList').find_all('tr')
        for tr in song_trs:
            try:
                # 예) javascript:searchLog('web_song','SONG','SO','가을','30636089');melon.link.goSongDetail('30636089');
                song_attr = tr.a['href']

                # goSongDetail을 찾은 다음 앞의 goSongDetail(' 와 뒤의 '); 를 잘라서 곡 ID(song_id)만 추출
                song_id_criteria = 'goSongDetail'
                song_id = song_attr[song_attr.find(song_id_criteria) + len(song_id_criteria) + 2:-3]

                song_ids.append(song_id)
            except:
                # 멜론 검색 결과에는 뜨는데 곡 정보가 없는 경우
                continue

        # 한 페이지에 song_count_per_page 만큼의 곡이 없는 경우 마지막 페이지
        if len(song_ids) % song_count_per_page != 0:
            break
        else:
            page += 1

    driver.close()
    print(f'[END] 멜론 곡 ID 목록 추출 완료 (총 {len(song_ids)}곡)\n')

    return song_ids


def __scrap_song_details(song_ids: List[str]):
    print('[START] 멜론 곡 상세 페이지에서 (곡명, 아티스트명, 가사) 스크래핑')

    # 사용자가 브라우징하는 것처럼 보이기 위해 HTTP Header 조작
    fake_http_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }

    songs = []
    for song_id in song_ids:
        url = f'https://www.melon.com/song/detail.htm?songId={song_id}'
        page_html = requests.get(url, headers=fake_http_headers).text

        soup = BeautifulSoup(page_html, 'html.parser')

        # 곡명, 아티스트명 추출
        info_form = soup.find(id='downloadfrm')
        title = info_form.find('div', {'class':'song_name'}).text.replace('곡명', '', 1).strip()
        artist = info_form.find('div', {'class':'artist'}).text.strip()

        # 가사 추출
        try:
            lyric_lines = soup.find(id='d_video_summary').stripped_strings
            # 가사를 한 줄로 만들기
            lyric = ' '.join(lyric_lines)
        except:
            # 가사가 없는 경우
            lyric = ''
        
        songs.append({
            'id': song_id,
            'title': title,
            'artist': artist,
            'lyric': lyric,
            'url': url
        })
    
    print('[END] 멜론 곡 상세 페이지 스크래핑 완료\n')
    
    return songs


def __save_songs_to_file(songs: list, filename: str, format: str):
    filepath = f'./{filename}.{format}'
    print(f'[START] 검색 결과를 파일로 저장 [경로: {filepath}]')

    if format == 'json':
        with open(filepath, 'w', encoding='utf-8') as outfile:
            json.dump(songs, outfile, indent=4)

    elif format == 'csv':
        with open(filepath, 'w', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=['id', 'title', 'artist', 'lyric', 'url'])
            writer.writeheader()
            writer.writerows(songs)
    else:
        raise Exception('파일 형식(format) 오류')
    
    print('[END] 파일 생성 완료\n')


if __name__ == '__main__':
    # Init argument parser
    parser = argparse.ArgumentParser(prog='Melon Lyric Scraper')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + PROG_VERSION)
    parser.add_argument('keyword', help='검색 키워드')
    parser.add_argument('-s', '--section', help='검색 방법 [all: 전체, artist: 아티스트명, song: 곡명(기본값), album: 앨범명]', choices=['all', 'artist', 'song', 'album'], default='song')
    # TODO: 장르 (-g, --genre) 추가
    parser.add_argument('-o', '--output', help='결과 출력 형식 [csv(기본값), json]', choices=['csv', 'json'], default='csv')
    
    args = parser.parse_args()
    keyword = args.keyword
    section = args.section
    # 발라드
    genre = 'GN0101'
    output_format = args.output
    print(f'검색 키워드: [{keyword}], 검색 방법: [{section}], 장르: [{genre}], 출력 형식: [{output_format}]\n')

    # 1. 곡 ID 추출
    song_ids = __extract_song_ids(keyword=keyword, section=section, genre=genre)

    # 2. 곡 세부 정보 (곡명, 아티스트명, 가사) 추출
    songs = __scrap_song_details(song_ids=song_ids)
    # TODO: 가사가 없거나, 중복된 가사 제거?

    # 3. 파일로 저장
    __save_songs_to_file(songs=songs, filename=f'output_{keyword}_{section}_{genre}', format=output_format)
