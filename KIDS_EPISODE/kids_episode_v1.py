import requests

TMDB_API_KEY = 'cd88d12bfe4c5d842ef9a464b2f0bcd1'
language = 'ko'

# TV SERIES LISTS > POPULAR
# 01. series_id 필요
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
                # series_name과 season_num을 결합하여 season_name 생성
                season_name = f"{series_name} 시즌 {season_num}"
                series_seasons.append({
                    'series_id': series_id,
                    'series_name': series_name,
                    'season_id': season['id'],
                    'season_num': season_num,
                    'season_name': season_name,
                    'episode_count': season['episode_count']
                })
    return series_seasons

def fetch_episode_info(series_ids, season_number, language='ko-KR'):
    episodes = []
    for series_id in series_ids:
        url = f'https://api.themoviedb.org/3/tv/{series_id}/season/{season_number}'
        params = {
            'api_key': TMDB_API_KEY,
            'language': language
        }
        response = requests.get(url, params=params)
        data = response.json()
        if 'episodes' in data:
            for episode in data['episodes']:
                episodes.append({
                    'episode_id' : episode['id'],
                    'episode_name': episode['name'],
                    'episode_num': episode['episode_number'],
                    'episode_overview': episode['overview'],
                    'episode_air_date': episode['air_date'],
                    'episode_rtm': episode['runtime'],
                    'episode_still': episode['still_path']
                })
    return episodes

# 각 시리즈의 시즌 ID와 시리즈 정보를 가져와서 리스트에 저장
series_seasons = fetch_seasons_info(series_info.keys())

# 각 시리즈의 시즌 정보를 기반으로 에피소드 정보 가져오기
for season_info in series_seasons:
    series_id = season_info['series_id']
    season_number = season_info['season_num']
    
    # 해당 시리즈의 모든 시즌의 에피소드 정보 가져오기
    episode_info = fetch_episode_info([series_id], season_number)
    
    # 에피소드 정보 출력
    for episode in episode_info:
        print(f"Episode ID: {episode['episode_id']}, Season name: {season_info['season_name']}, {episode['episode_num']}, Episode Name: {episode['episode_name']}")
        print()
        print(f"줄거리: {episode['episode_overview']}, 방영날짜: {episode['episode_air_date']} ,RTM : {episode['episode_rtm']}")

