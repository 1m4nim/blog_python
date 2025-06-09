from flask import Flask, request, redirect, url_for, render_template

app = Flask(__name__)

# 投稿データの簡易保存用（本来はDBを使います）
posts = []

@app.route('/')
def index():
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    if 0 <= post_id < len(posts):
        post = posts[post_id]
        return render_template('post_detail.html', post=post)
    return "投稿が見つかりません", 404

@app.route('/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        posts.append({'title': title, 'content': content})
        return redirect(url_for('index'))
    return render_template('new_post.html')

if __name__ == '__main__':
    app.run(debug=True)
