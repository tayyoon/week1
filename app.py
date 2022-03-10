from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import jwt  # PYJWT 설치
import datetime
import hashlib  # 회원가입 시, 비밀번호를 암호화하여 DB에 저장
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)


# 서버연결1
# from pymongo import MongoClient
#
# client = MongoClient("mongodb+srv://test:sparta@cluster0.qgh8x.mongodb.net/Cluster0?retryWrites=true&w=majority")
# db = client.dbsparta


# 서버연결2 (문희)
import pymongo
import certifi

client = pymongo.MongoClient("mongodb+srv://test:sparta@cluster0.qgh8x.mongodb.net/Cluster0?retryWrites=true&w=majority",
    tlsCAFile=certifi.where())
db = client.dbsparta


SECRET_KEY = 'SPARTA'


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"username": payload['id']})
        music_list = list(db.season.find({}, {'_id': False}))
        return render_template('index.html', nickname=user_info["nickname"], musics=music_list)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 해주시기 바랍니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/login')
def register():
    return render_template('login.html')


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']

    print('1',password_receive)
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    print('1',password_hash)
    doc = {
        "username": username_receive,
        "password": password_hash,
        "nickname": nickname_receive,
     }
    db.user.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.user.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})
# 로그인 시 로그인 정보 데이터베이스 내 자료들과 확인 후 로그인 여부 결정
@app.route('/api/login', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    result = db.user.find_one({'username': username_receive, 'password': password_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode("utf-8")
        # localhost 실행시 .decode() 제거 필요

        return jsonify({'result': 'success', 'token': token})

    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
@app.route('/api/nick', methods=['GET'])
def api_valid():

    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        userinfo = db.user.find_one({'username': payload['username']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

# @app.route('/mainpage/logout')
# def logout():
#     return render_template('index.html') ##########################################작업필요

@app.route('/index')
def mainpage():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"username": payload['id']})
        music_list = list(db.season.find({}, {'_id': False}))
        return render_template('index.html', nickname=user_info["nickname"], musics=music_list)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 해주시기 바랍니다."))


@app.route("/index/music", methods=["POST"])
def music_post():
    url_receive = request.form['url_give']
    season_receive = request.form['season_give']
    comment_receive = request.form['comment_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    songs = soup.select('#conts > div.section_info > div > div.entry > div.info')

    for title in songs:
        title = title.select_one('div.song_name').text.replace('앨범명','').strip()

    for artist in songs:
        artist = artist.select_one('div.artist > a[title]').text

    img = soup.select_one('meta[property="og:image"]')['content']

    doc = {
        'title':title,
        'artist': artist,
        'image':img,
        'season':season_receive,
        'comment':comment_receive
    }
    db.season.insert_one(doc)
    print(doc)
    return jsonify({'msg':'저장 완료!'})

# 각 계절마다 그 계절의 조건에 맞는 데이터 가져가서 리스팅
@app.route("/index/music/spring", methods=["GET"])
def music_get_1():
    music_list = list(db.season.find({'season': "1"}, {'_id': False}))
    return jsonify({'musics': music_list})
    return render_template('index.html', musics=music_list)

@app.route("/index/music/summer", methods=["GET"])
def music_get_2():
    music_list = list(db.season.find({'season': "2"}, {'_id': False}))
    return jsonify({'musics': music_list})

@app.route("/index/music/april", methods=["GET"])
def music_get_3():
    music_list = list(db.season.find({'season': "3"}, {'_id': False}))
    return jsonify({'musics': music_list})

@app.route("/index/music/winter", methods=["GET"])
def music_get_4():
    music_list = list(db.season.find({'season': "4"}, {'_id': False}))
    return jsonify({'musics': music_list})

@app.route("/index/comment", methods=["POST"])
    # 달려있는 코멘트 수정 
def edit_comment():
    comment_receive = request.form['new_comment_give']
    title_receive = request.form['input_title_give']
    find_title = db.season.find_one({'title': title_receive})['title']
    if find_title == title_receive:
        db.season.update_one({'title': title_receive}, {'$set': {'comment': comment_receive}})
        return jsonify({'msg': '저장 완료!'})
    else:
        return jsonify({'msg': '음악을 찾을 수 없습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
