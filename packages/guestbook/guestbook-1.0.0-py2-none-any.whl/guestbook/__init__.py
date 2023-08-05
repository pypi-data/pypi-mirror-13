#coding: utf-8
import shelve
from datetime import datetime   
from flask import Flask, request, render_template, redirect, escape, Markup

application = Flask(__name__)

DATA_FILE = 'guestbook.dat'

def save_data(name, comment, create_at):
    """投稿データを保存します
    """
    #shelveモジュールでデータベースファイルを開きます
    database = shelve.open(DATA_FILE)
    #データベースにgreeting_listがなければ、新しくリストを作ります
    if 'greeting_list' not in database:
        greeting_list = []
    else:
        #データベースからデータを取得します
        greeting_list = database['greeting_list']
    #リストの先頭に投稿データを追加します
    greeting_list.insert(0, {
        'name': name,
        'comment': comment,
        'create_at': create_at,
    })
    #データベースを更新します
    database['greeting_list'] = greeting_list
    #データベースファイルを閉じます
    database.close()

def load_data():
    """投稿されたデータを返します
    """
    #shelveモジュールでデータベースファイルを開きます
    database = shelve.open(DATA_FILE)
    #greeting_listを返します。データがなければ空のリストを返します
    greeting_list = database.get('greeting_list', [])
    database.close()
    return greeting_list

@application.route('/')
def index():
    """トップページ
    テンプレートを使用してページを表示します
    """
    #投稿データを読み込みます
    greeting_list = load_data()
    return render_template('index.html', greeting_list=greeting_list)

@application.route('/path', methods=['POST'])
def post():
    """投稿用URL
    """
    #投稿されたデータを取得します
    name = request.form.get('name') #名前
    comment = request.form.get('comment')
    create_at = datetime.now()
    #データを保存します
    save_data(name, comment, create_at)
    #保存後はトップページにリダイレクトします
    return redirect('/')

@application.template_filter('n12br')
def n12br_filter(s):
    """改行文字をbrタグに置き換えるテンプレートフィルタ
    """
    return escape(s).replace('\n',Markup('<br>'))

@application.template_filter('datetime_fmt')
def datetime_fmt_filter(dt):
    """datetimeオブジェクトを見やすい表示にするテンプレートフィルタ
    """
    return dt.strftime('%Y/%m/%d %H:%M:%S')

def main():
    application.run('127.0.0.1',8000)


if __name__ == '__main__':
    #IPアドレス127.0.0.1の8000番ポートでアプリケーションを実行します
    application.run('127.0.0.1', 8000, debug=True)


