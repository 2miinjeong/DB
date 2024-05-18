import requests
import mysql.connector

TMDB_API_KEY = 'cd88d12bfe4c5d842ef9a464b2f0bcd1'
language = 'ko'

def fetch_popular_series(genre_id=10762, language='ko-KR', region='KR', page=1, total_results=200):
    url = 'https://api.themoviedb.org/3/discover/tv'
    params = {
        'api_key': TMDB_API_KEY,
        'language': language,
        'region': region,
        'page': page,
        'with_genres': genre_id
    }

    results = []
    while len(results) < total_results:
        response = requests.get(url, params=params)
        data = response.json()
        for series in data['results']:
            # origin_country가 KR을 포함하는 경우에만 결과에 추가
            if 'KR' in series.get('origin_country', []):
                results.append(series)
                if len(results) >= total_results:
                    break
        page += 1
        params['page'] = page

    return results[:total_results]

# SERIES_ID 저장
popular_series = fetch_popular_series()
series_info = {series['id']: series['name'] for series in popular_series}

# SERIES_ID와 시즌 ID를 함께 출력
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

def fetch_episode_info(series_id, season_number, language='ko-KR'):
    url = f'https://api.themoviedb.org/3/tv/{series_id}/season/{season_number}'
    params = {
        'api_key': TMDB_API_KEY,
        'language': language
    }
    response = requests.get(url, params=params)
    data = response.json()
    episodes = []
    if 'episodes' in data:
        for episode in data['episodes']:
            episodes.append({
                'episode_id': episode['id'],
                'episode_name': episode['name'],
                'episode_num': episode['episode_number'],
                'episode_overview': episode['overview'],
                'episode_air_date': episode['air_date'],
                'episode_rtm': episode['runtime'],
                'episode_still': episode['still_path']
            })
    return episodes

# 데이터베이스 연결
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='0106',
    database='sample'
)

try:
    cursor = connection.cursor()
    
    # 시리즈 정보 데이터베이스에 저장
    series_seasons = fetch_seasons_info(series_info.keys())
    for item in series_seasons:
        season_id = item['season_id']
        series_id = item['series_id']
        series_name = item['series_name']
        season_num = item['season_num']
        episode_count = item['episode_count']
        air_date = item['air_date']

        '''
        sql = "INSERT INTO SERIES (SEASON_ID, SERIES_ID, SEASON_NAME, SEASON_NUM, EPISODE_COUNT, AIR_DATE) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (season_id, series_id, series_name, season_num, episode_count, air_date)
        cursor.execute(sql, val)
        '''
        
        # 에피소드 정보 데이터베이스에 저장
        episodes_list = fetch_episode_info(series_id, season_num)
        for episode in episodes_list:
            episode_id = episode['episode_id']
            episode_name = episode['episode_name']
            episode_num = episode['episode_num']
            episode_overview = episode['episode_overview']
            episode_air_date = episode['episode_air_date']
            episode_rtm = episode['episode_rtm']
            episode_still = episode['episode_still']

            episode_still_url = f"https://image.tmdb.org/t/p/original{episode_still}" if episode_still else None
            
            sql = "INSERT INTO KIDS3 (EPISODE_ID, SEASON_NAME, EPISODE_NUM, EPISODE_NAME, EPISODE_OVERVIEW, EPISODE_AIR_DATE, EPISODE_RTM, EPISODE_STILL) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            val = (episode_id, f"{series_name} 시즌 {season_num}", episode_num, episode_name, episode_overview, episode_air_date, episode_rtm, episode_still_url)  
            cursor.execute(sql, val)


    # 변경 사항 커밋
    connection.commit()

finally:
    # 연결 닫기
    if connection.is_connected():
        cursor.close()
        connection.close()
