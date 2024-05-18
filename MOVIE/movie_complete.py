import requests
import mysql.connector

# 이민정 TMDB API_KEY
api_key = 'cd88d12bfe4c5d842ef9a464b2f0bcd1'

# 영화 장르 API
genre_url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}&language=ko-KR'
response = requests.get(genre_url)
genre_data = response.json()

# 장르 ID를 한국어 이름으로 매핑하는 딕셔너리
genre_dict = {}
for genre in genre_data['genres']:
    genre_dict[genre['id']] = genre['name']

#인기영화 API
url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=ko-KR&page='
movies = []

# 각 영화의 ID를 저장할 세트
movie_ids = set()

for page in range(1, 11):  # 10 페이지까지 요청
    response = requests.get(url + str(page))
    data = response.json()
    results = data.get('results', [])
    
    for movie in results:
        movie_id = movie.get('id')
        if movie_id not in movie_ids:  # 이미 있는 경우 건너뛰기
            movies.append(movie)
            movie_ids.add(movie_id)

# MySQL 연결/localhost > sample 테이블
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="0106",
    database="complete"
)
cursor = db_connection.cursor()

# 데이터 처리 및 삽입
for movie in movies:
    # 영화 정보 추출
    movie_id = movie.get('id')
    title = movie.get('title')
    genre_names = [genre_dict.get(genre_id) for genre_id in movie.get('genre_ids', [])]
    genre = ", ".join(genre_names)
    overview = movie.get('overview')
    poster_path = movie.get('poster_path')
    poster_url = f"https://image.tmdb.org/t/p/original/{poster_path}" if poster_path else None
    
    # 각 영화의 세부 정보를 가져오기 위한 API 요청
    details_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=ko-KR&append_to_response=credits,videos'
    details_response = requests.get(details_url)
    details_data = details_response.json()

    #관람연령 출력을 위한 API요청
    release_url = f'https://api.themoviedb.org/3/movie/{movie_id}/release_dates?api_key={api_key}'
    release_response = requests.get(release_url)
    release_data = release_response.json()
    
    # 출연진 정보/CAST
    cast = details_data.get('credits', {}).get('cast', [])
    actor_info = ", ".join([actor.get('name') for actor in cast[:3]])

    # 감독 정보/CREW
    crew = details_data.get('credits', {}).get('crew', [])
    directors = [crew_member.get('name') for crew_member in crew if crew_member.get('job') == 'Director']
    director_info = ", ".join(directors)
    
    # 예고편 주소/TRAILER_URL
    videos = details_data.get('videos', {}).get('results', [])
    trailer_url = None
    if videos:
        trailer_path = videos[0].get('key')
        if trailer_path:
            trailer_url = f"https://www.youtube.com/watch?v={trailer_path}"
    
    # 런타임/RUNTIME
    runtime = details_data.get('runtime')
    if runtime is None:
        runtime = 0

    # 개봉일/release_date
    release_date = details_data.get('release_date')

    # 관람 등급/kr_certification
    kr_certification = None  # 초기화
    if 'results' in release_data:
        # results 배열 안에서 한국(KR) 정보 찾기
        for movie_data in release_data['results']:
            if movie_data['iso_3166_1'] == 'KR':
                # certification 값 가져오기
                release = movie_data.get('release_dates', [])[0]
                kr_certification = release.get('certification')
                if kr_certification is None:
                    kr_certification = 'null'
                break  # 한국(KR) 정보를 찾으면 루프 종료
    
    # SQL 쿼리 실행
    sql = "INSERT INTO MOVIE (MOVIE_ID, SUB_CATEGORY, TITLE, GENRE, RELEASE_DATE, RATING, CONTENT_SUM, CAST, CREW, POSTER_URL, TRAILER_URL, RTM) VALUES (%s, '영화', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    if kr_certification is None:
        values = (movie_id, title, genre, release_date, None, overview, actor_info, director_info, poster_url, trailer_url, runtime)
    else:
        values = (movie_id, title, genre, release_date, kr_certification, overview, actor_info, director_info, poster_url, trailer_url, runtime)

    try:
        cursor.execute(sql, values)
    except mysql.connector.Error as e:
        print(f"영화 {title} 삽입 중 오류 발생:", e)
    continue

# 변경사항 커밋 및 연결 종료
db_connection.commit()
db_connection.close()
