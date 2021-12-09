from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from flask_paginate import Pagination, get_page_parameter

from werkzeug.exceptions import abort

from flaskr.db import get_db

bp = Blueprint('book', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        word = request.form['search_word']
        posts = get_db().execute(
            'SELECT id, created, title, author, detail'
            ' FROM post'
            ' WHERE title LIKE ? OR author LIKE ?'
            ' ORDER BY created DESC',
            ('%' + word + '%', '%' + word + '%') 
        ).fetchall()
        page = request.args.get(get_page_parameter(), default=1, type=int)
        per_page = 3
        res = posts[(page-1)*per_page:page*per_page]
        pagination = Pagination(page=page, total=len(posts), per_page=per_page, css_framework='bootstrap4')

        return render_template('book/index.html', res=res, request_form=request.form, pagination=pagination)

    else:
        db = get_db()
        posts = db.execute(
            'SELECT id, created, title, author, detail'
            ' FROM post'
            ' ORDER BY created DESC'
        ).fetchall()
        page = request.args.get(get_page_parameter(), default=1, type=int)
        per_page = 3
        res = posts[(page-1)*per_page:page*per_page]
        pagination = Pagination(page=page, total=len(posts), per_page=per_page, css_framework='bootstrap4')

        return render_template('book/index.html', res=res, request_form=request.form, pagination=pagination)


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


@bp.route('/individual/<int:id>', methods=['GET', 'POST'])
def individual(id):
    db = get_db()
    post = get_post(id)

    if request.method == 'POST':
        comment = request.form['comment']
        db.execute(
            'INSERT INTO comments (comment, post_id)'
            ' VALUES (?, ?)',
            (comment, id)
        )
        db.commit()
    
    comments = db.execute(
        'SELECT comment, created'
        ' FROM comments'
        ' WHERE post_id = ?'
        ' ORDER BY created DESC',
        (id,)
    ).fetchall()

    return render_template('book/individual.html', post=post, comments=comments)
