from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .db import get_db
from .interactive_conditional_samples import interact_model

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created'
        ' FROM post p'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

def get_post(id):
    post = get_db().execute(
        'SELECT p.id, title, body, created'
        'WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    return post

@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            text = interact_model(raw_text=title)
            db.execute(
                'INSERT INTO post (title, body)'
                ' VALUES (?, ?)',
                (title, text)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')