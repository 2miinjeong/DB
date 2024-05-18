import requests

TMDB_API_KEY = 'cd88d12bfe4c5d842ef9a464b2f0bcd1'
language = 'ko'

# TV SERIES LISTS > POPULAR
def fetch_popular_series(language='ko-KR', region='KR', page=1, total_results=200):
    url = f'https://api.themoviedb.org/3/tv/popular'
    params = {
        'api_key': TMDB_API_KEY,
        'language': language,
        'region': region,
        'page': page
    }

    results = []
    while len(results) < total_results:
        response = requests.get(url, params=params)
        data = response.json()
        results.extend(data['results'])
        page += 1
        params['page'] = page

    return results[:total_results]

# SERIES_ID 저장
popular_series = fetch_popular_series()
series_info = {series['id']: series['name'] for series in popular_series}

# SERIES_ID와 시즌 ID를 함께 출력
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


# 각 시리즈의 시즌 ID와 시리즈 정보를 가져와서 리스트에 저장
series_seasons = fetch_seasons_info(series_info.keys())

# 저장된 시리즈 정보 출력
for item in series_seasons:
    print(f"Season ID: {item['season_id']} Series ID: {item['series_id']} {item['season_name']} {item['episode_count']}")
