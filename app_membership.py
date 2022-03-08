from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import jwt  # PYJWT 설치
import datetime
import hashlib  # 회원가입 시, 비밀번호를 암호화하여 DB에 저장

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
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('mainpage.html', nickname=user_info["nick"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 해주시기 바랍니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('membership.html', msg=msg)

@app.route('/register')
def register():
    return render_template('membership.html')


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

@app.route('/api/login', methods=['POST'])
def api_login():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    print('2',password_receive)
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    print('2',password_hash)
    result = db.user.find_one({'username': username_receive, 'password': password_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})

    # id_receive = request.form['id_give']
    # pw_receive = request.form['pw_give']
    #
    # pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()  # 회원가입 때와 같은 방법으로 pw 암호화
    #
    # result = db.user.find_one({'id': id_receive, 'pw': pw_hash}) # id, 암호화된pw을 가지고 해당 유저 찾기

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    # if result is not None:
    #     payload = {
    #         'id': id_receive,
    #         'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    #     }
    #     token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token을 줍니다.
        # return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
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


@app.route('/mainpage')
def logout():
    return render_template('test.html') ##########################수정필요#######################


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)