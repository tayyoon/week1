from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

import pymongo
import certifi

client = pymongo.MongoClient("mongodb+srv://test:sparta@cluster0.qgh8x.mongodb.net/Cluster0?retryWrites=true&w=majority",
    tlsCAFile=certifi.where())
db = client.dbsparta

@app.route('/')
def home():
    music_list = list(db.season.find({}, {'_id': False}))
    return render_template('index.html', musics=music_list)



#################################수정
@app.route("/music", methods=["POST"])
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
#################################수정


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


@app.route("/", methods=["GET"])
def music_get_11():
    music_list = list(db.season.find({}, {'_id': False}))
    return render_template('index2.html', musics=music_list)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)