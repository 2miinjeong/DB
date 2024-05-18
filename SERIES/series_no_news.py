import mysql.connector
import requests
from datetime import datetime

# MySQL 연결 설정
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0106",
    database="sample2"
)
mycursor = mydb.cursor()

# TMDB API 키
TMDB_API_KEY = 'cd88d12bfe4c5d842ef9a464b2f0bcd1'
language = 'ko'

# TV SERIES LISTS > POPULAR
#SERIES_ID
from datetime import datetime

def fetch_popular_series(language='ko-KR', region='KR', page=1, total_results=100):
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
                continue  # 제외시킬 장르 id가 포함되어 있는 경우 해당 시리즈를 건너뜁니다.
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

# TV SERIES > DETAILS
# CAST, CREW, OVERVIEW
def fetch_series_details(series_id, language='ko-KR'):
    url = f'https://api.themoviedb.org/3/tv/{series_id}'
    params = {
        'api_key': TMDB_API_KEY,
        'language': language,
        'append_to_response': 'credits'  
    }

    response = requests.get(url, params=params)
    data = response.json()
    
    if 'overview' not in data or not data['overview']:
        params['language'] = 'en'
        response = requests.get(url, params=params)
        data = response.json()

    return data


# TV SERIES > IMAGES
# LOGO, POSTER
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

# TV SERIES > VIDEOS
# TRAILER 
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

    if not data.get('results'):
        return None

    for item in data['results']:
        video_type = item.get('type')
        if video_type in key_mapping:
            return item.get('key')

    return None


def insert_series_to_database(series, series_images, series_videos):
    '''
    sql_check_existence = "SELECT SERIES_ID FROM SERIES WHERE SERIES_ID = %s"
    val_check_existence = (series['id'],)
    mycursor.execute(sql_check_existence, val_check_existence)
    result = mycursor.fetchone()
    

    #00. PRIMARY_KEY 중복 방지
    if result:
        print(f"Series with ID {series['id']} already exists in the database.")
        return
    '''
 

    #01. SERIES_ID
    series_id = series['id']

    #02. SUB_CATEGORY
    #고정값

    #03. TITLE
    title = series['name']

    #04. GENRE
    if 'genres' in series:
        genres = [genre['name'] for genre in series['genres']]
        genre = ", ".join(genres)
    else:
        genre = None

    #05. RATING
    series_id = series['id']
    rating = fetch_series_rating(series_id)

    #06. SEASON_NUM
    season_num = f"{series['number_of_seasons']}"

    #07. OVERVIEW
    overview = series['overview']

    #08. CAST
    cast_names = [cast['name'] for cast in series['credits']['cast'][:3]]
    cast = ', '.join(cast_names)

    #09. CREW
    crew_names = [crew['name'] for crew in series['credits']['crew'][:3]]
    crew = ', '.join(crew_names) if crew_names else None

    #10. LOGO
    logo_url = ""
    if 'logos' in series_images:
        logo_url = ", ".join([f"https://image.tmdb.org/t/p/original{logo['file_path']}" for logo in series_images['logos']])
    
    #11. POSTER
    poster_url = ""
    if 'posters' in series_images:
        poster_url = ", ".join([f"https://image.tmdb.org/t/p/original{poster['file_path']}" for poster in series_images['posters']])


    #12. TRAILER
    trailer_url = f"https://www.youtube.com/watch?v={series_videos}"


    #SQL INSERT
    sql = "INSERT INTO SERIES2 (SERIES_ID, SUB_CATEGORY, TITLE, GENRE, SERIES_RATING, SEASON_NUM, SERIES_OVERVIEW, CAST, CREW, LOGO, POSTER, TRAILER) VALUES (%s, '시리즈', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (series_id, title, genre, rating, season_num, overview, cast, crew, logo_url, poster_url, trailer_url)
    mycursor.execute(sql, val)
    mydb.commit()



def main():
    popular_tv_series = fetch_popular_series()

    for series in popular_tv_series:
        series_details = fetch_series_details(series['id'])
        series_images = fetch_series_images(series['id'])
        series_videos = fetch_series_videos(series['id'])  # series_videos 가져오기
        insert_series_to_database(series_details, series_images, series_videos)

if __name__ == "__main__":
    main()