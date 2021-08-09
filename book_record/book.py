from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.db import get_db

bp = Blueprint('book', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT id, created, title, author, detail'
        ' FROM post'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('book/index.html', posts=posts)


@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        detail = request.form['detail']
        error = None

        if not title:
            error = 'Title is required.'
        
        if not author:
            error = 'Author is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, author, detail)'
                ' VALUES (?, ?, ?)',
                (title, author, detail)
            )
            db.commit()
            return redirect(url_for('book.index'))
    
    return render_template('book/create.html')


def get_post(id):
    post = get_db().execute(
        'SELECT id, created, title, author, detail'
        ' FROM post'
        ' WHERE id = ?',
        (id,) 
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
    
    return post


@bp.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        detail = request.form['detail']
        error = None
    
        if not title:
            error = 'Title is required.'
        
        if not author:
            error = 'Author is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, author = ?, detail = ?'
                ' WHERE id = ?',
                (title, author, detail, id)
            )
            db.commit()
            return redirect(url_for('book.index'))
    
    return render_template('book/update.html', post=post)


@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('book.index'))
