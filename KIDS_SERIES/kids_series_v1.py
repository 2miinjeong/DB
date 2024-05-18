#인기 tv프로그램 200개 > 장르가 kids > 컨텐츠 제작 국가가 한국인 것 출력

from langdetect import detect
import requests

# TMDB API 키
TMDB_API_KEY = 'cd88d12bfe4c5d842ef9a464b2f0bcd1'
language = 'ko'

#TV SERIES LISTS > POPULAR
#SERIES_ID
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


#TV SERIES > CONTENT_RATING
#RATING
def fetch_series_rating(series_id):
    url = f'https://api.themoviedb.org/3/tv/{series_id}/content_ratings'
    params = {
        'api_key': TMDB_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()
    
    kr_rating = None
    de_rating = None
    
    if 'results' in data:
        for result in data['results']:
            iso_3166_1 = result.get('iso_3166_1')
            rating = result.get('rating')
            
            if iso_3166_1 == 'KR':
                kr_rating = rating
            elif iso_3166_1 == 'DE':
                de_rating = rating
    
    if kr_rating:
        return kr_rating
    elif de_rating:
        return de_rating
    else:
        return None
    
#TV SERIES > DETAILS
#CAST, CREW
def fetch_series_details(series_id, language='ko-KR'):
    url = f'https://api.themoviedb.org/3/tv/{series_id}'
    params = {
        'api_key': TMDB_API_KEY,
        'language': language,
        'append_to_response': 'credits'  # 출연진 및 제작진 정보
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'overview' not in data or not data['overview']:
        params['language'] = 'en'
        response = requests.get(url, params=params)
        data = response.json()

    return data

#TV SERIES > IMAGES
#LOGO, POSTER
def fetch_series_images(series_id, language='ko'):
    url = f'https://api.themoviedb.org/3/tv/{series_id}/images'
   
    params = {
        'api_key': TMDB_API_KEY,
        'language': language
    }

    response = requests.get(url, params=params)
    data = response.json()
    
    # 한국어 버전 없을 시 영어버전 출력
    if ('posters' not in data or len(data['posters']) == 0) or ('logos' not in data or len(data['logos']) == 0):
        params['language'] = 'en'
        response = requests.get(url, params=params)
        data = response.json()

        if 'posters' in data and len(data['posters']) > 0:
            data['posters'] = data['posters'][:1]
        if 'logos' in data and len(data['logos']) > 0:
            data['logos'] = data['logos'][:1]

    return data

#TV SERIES > VIDEOS
#TRAILER 
def fetch_series_videos(series_id, language='en'):
    url = f'https://api.themoviedb.org/3/tv/{series_id}/videos'

    params = {
        'api_key': TMDB_API_KEY,
        'language': language,
    }
    response = requests.get(url, params=params)
    data = response.json()

    key_mapping = {
        'Trailer': 'trailer',
        'Clip': 'clip',
        'Teaser': 'teaser',
        'Opening Credits': 'opening_credits'
    }

    for item in data.get('results', []):
        video_type = item.get('type')
        if video_type in key_mapping:
            return item.get('key')

    return None


def print_series_info(series, series_images, series_videos):

    #01. SERIES_ID
    print("id:", series['id'])

    ##. First_air_date
    print("first_air_date", series['first_air_date'])

    #02. SUB_CATEGORY 
    #고정값

    #03. TITLE
    print("제목:", series['name'])

    #04. GENRE
    if 'genres' in series:
        if len(series['genres']) == 1: # 장르 내 리스트가 하나뿐인 경우에는 언어 상관없이 출력
            genre = series['genres'][0]['name']
        else:
            genres = [genre['name'] for genre in series['genres'] if detect(genre['name']) == 'ko']
            genre = ", ".join(genres)
    else:
        genre = None
    
    
    #05. RATING
    series_id = series['id']
    rating = fetch_series_rating(series_id)
    print("등급:", rating)

    #06. SEASON_NUM
    print("시즌 수:", f"{series['number_of_seasons']}")

    #07. OVERVIEW
    print("줄거리:", series['overview'])
    

    #08. CAST
    if 'credits' in series and 'cast' in series['credits']:
        print("출연진:")
        for cast in series['credits']['cast'][:3]:
            print(f"{cast['name']}")
    
    #09. CREW
    if 'credits' in series and 'crew' in series['credits']:
        print("제작진:")
        if series['credits']['crew']:  # 제작진 정보가 있는 경우에만 출력
            crew = series['credits']['crew'][0]  # 첫 번째 제작진 정보만 출력
            print(f"{crew['name']}")
    
    #10. LOGO
    if 'logos' in series_images:
        for logo in series_images['logos']:
            print("로고 URL:", f"https://image.tmdb.org/t/p/original{logo['file_path']}")

    #11. POSTER_URL
    if 'posters' in series_images:
         for poster in series_images['posters']:
            print("포스터 URL:", f"https://image.tmdb.org/t/p/original{poster['file_path']}")

    #12. TRAILER_URL
    if series_videos is not None:  
        print("예고편 URL:", f"https://www.youtube.com/watch?v={series_videos}")


def main():
    popular_tv_series = fetch_popular_series()

    for series in popular_tv_series:
        series_details = fetch_series_details(series['id'])
        series_images = fetch_series_images(series['id'])
        series_videos = fetch_series_videos(series['id']) 
        print_series_info(series_details, series_images, series_videos) 
        print()

if __name__ == "__main__":
    main()
