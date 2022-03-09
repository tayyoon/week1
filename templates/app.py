from flask import Flask, render_template, jsonify, request, session, redirect, url_for
app = Flask(__name__)

# from pymongo import MongoClient
# client = MongoClient('mongodb+srv://test:sparta@cluster0.qgh8x.mongodb.net/cluster0?retryWrites=true&w=majority')
# db = client.dbsparta

import jwt
import datetime
import hashlib
import certifi
import pymongo
client = pymongo.MongoClient("mongodb+srv://test:sparta@cluster0.qgh8x.mongodb.net/Cluster0?retryWrites=true&w=majority",
    tlsCAFile=certifi.where())
db = client.dbsparta
SECRET_KEY = 'SPARTA'

import requests
from bs4 import BeautifulSoup

#################################
##  HTML을 주는 부분             ##
#################################
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('mainpage.html', nickname=user_info["nick"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 페이지로 이동합니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 해주시기 바랍니다."))

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('log-reg.html', msg=msg)

# joinMembership으로 넘기는 부분
# @app.route('/login')
# def letsjoin():
#     return render_template('login.html')

# @app.route('/register')
# def register():
#     return render_template('joinMembership.html')

@app.route('/mainpage')
def mainpage():
    music_list = list(db.season.find({}, {'_id': False}))
    return render_template('index.html', musics=music_list)

#################################
##  로그인을 위한 API            ##
#################################

# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']

    print('1', password_receive)
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    print('1', password_hash)

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


# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

# 로그인페이지: GET, /   회원가입로드: GET, /joinMembership   회원가입: POST, /signUp
# ID 중복검사: POST, /check_dup  로그인로드: GET, /login  로그인하기: POST, /api/login

# 메인페이지
@app.route("/music", methods=["POST"])
def music_post():
    url_receive = request.form['url_give']
    season_receive = request.form['season_give']
    comment_receive = request.form['comment_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    # 여기에 코딩을 해서 meta tag를 먼저 가져와보겠습니다.
    title = soup.select_one('meta[property="og:title"]')['content']
    img = soup.select_one('meta[property="og:image"]')['content']


    doc = {
        'title':title,
        'image':img,
        'season':season_receive,
        'comment':comment_receive
    }
    db.season.insert_one(doc)
    return jsonify({'msg':'저 완료!'})

@app.route("/music", methods=["GET"])
def music_get():
    music_list = list(db.season.find({}, {'_id': False}))
    return jsonify({'musics':music_list})

@app.route("/music/spring", methods=["GET"])
def music_get_1():
    music_list = list(db.season.find({'season': "1"}, {'_id': False}))
    return jsonify({'musics': music_list})
    return render_template('index.html', musics=music_list)

@app.route("/music/summer", methods=["GET"])
def music_get_2():
    music_list = list(db.season.find({'season': "2"}, {'_id': False}))
    return jsonify({'musics': music_list})

@app.route("/music/april", methods=["GET"])
def music_get_3():
    music_list = list(db.season.find({'season': "3"}, {'_id': False}))
    return jsonify({'musics': music_list})

@app.route("/music/winter", methods=["GET"])
def music_get_4():
    music_list = list(db.season.find({'season': "4"}, {'_id': False}))
    return jsonify({'musics': music_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)