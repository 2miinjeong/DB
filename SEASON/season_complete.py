import requests
import mysql.connector

TMDB_API_KEY = 'cd88d12bfe4c5d842ef9a464b2f0bcd1'
language = 'ko'

# TV SERIES LISTS > POPULAR
# SERIES_ID
def fetch_popular_series(language='ko-KR', region='KR', page=1, total_results=200):
    url = f'https://api.themoviedb.org/3/tv/popular'
    params = {
        'api_key': TMDB_API_KEY,
        'language': language,
        'region': region,
        'page': page
    }

    excluded_genre_ids = [10763, 10766, 10767]  # 제외시킬 장르 id 목록

    results = []
    while len(results) < total_results:
        response = requests.get(url, params=params)
        data = response.json()
        for series in data['results']:
            if any(genre_id in excluded_genre_ids for genre_id in series.get('genre_ids', [])):
                continue  # 제외시킬 장르 id가 포함되어 있는 경우 해당 시리즈 생략
            results.append(series)
            if len(results) >= total_results:
                break
        page += 1
        params['page'] = page

    return results[:total_results]

# SERIES_ID 저장
popular_series = fetch_popular_series()
series_info = {series['id']: series['name'] for series in popular_series}

# SERIES_ID와 SEASON_ID 함께 출력
def fetch_seasons_info(series_ids, language='ko-KR'):
    series_seasons = []  # 시리즈 정보를 담을 리스트
    for series_id in series_ids:
        url = f'https://api.themoviedb.org/3/tv/{series_id}'
        params = {
            'api_key': TMDB_API_KEY,
            'language': language
        }
        response = requests.get(url, params=params)
        data = response.json()

        if 'seasons' in data:
            for season in data['seasons']:
                series_name = series_info[series_id]
                season_num = season['season_number']
                season_name = f"{series_name}{season_num}"
                series_seasons.append({
                    'series_id': series_id,
                    'series_name': series_name,
                    'season_id': season['id'],
                    'season_num': season_num,
                    'season_name': season_name,
                    'episode_count': season['episode_count'],
                    'air_date': season['air_date']
                })
    return series_seasons

#SERIES, SEASON 데이터 저장
series_seasons = fetch_seasons_info(series_info.keys())

# MySQL 연결
connection = mysql.connector.connect(host='localhost',
                                     user='root',
                                     password='0106',
                                     database='complete')

try:
    cursor = connection.cursor()

    #데이터베이스 삽입
    for item in series_seasons:
        season_id = item['season_id']
        series_id = item['series_id']
        series_name = item['season_name']
        season_num = item['season_num']
        episode_count = item['episode_count']
        air_date = item['air_date']
        
        
        # SQL 쿼리 실행
        sql = "INSERT INTO SEASON (SEASON_ID, SERIES_ID, SEASON_NAME, SEASON_NUM, EPISODE_COUNT, AIR_DATE) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (season_id, series_id, series_name, season_num, episode_count, air_date)
        cursor.execute(sql, val)

    # 변경사항 커밋
    connection.commit()

finally:
    # DB 연결 닫기
    if connection.is_connected():
        cursor.close()
        connection.close()
