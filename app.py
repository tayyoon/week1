from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.thhpe.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route('/')
def home():
    return render_template('index.html')

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