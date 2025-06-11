import os
from flask import Flask, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import pytz

app = Flask(__name__)

# アップロード先のディレクトリ
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# SQLite設定
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///post.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# DBモデル
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100))  # 画像のファイル名
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# JSTフィルター
@app.template_filter('to_jst')
def to_jst(utc_dt):
    jst = pytz.timezone('Asia/Tokyo')
    return utc_dt.astimezone(jst)

# DB初期化
with app.app_context():
    db.create_all()

# トップページ
@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

# 投稿詳細
@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

# 新規作成
@app.route('/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image = request.files.get('image')

        filename = None
        if image and image.filename != '':
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        post = Post(title=title, content=content, image=filename)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('new_post.html')

# 編集
@app.route('/edit/<int:id>', methods=['GET', 'POST'], endpoint='edit_post')
def edit_post(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        
        image = request.files.get('image')
        if image and image.filename != '':
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            post.image = filename

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_post.html', post=post)

# 削除
@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
