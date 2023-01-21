import os
from datetime import datetime

import flask_login
from flask import Blueprint, render_template, request, url_for, redirect, \
    jsonify, flash
from flask_login import login_required
from sqlalchemy import desc
from werkzeug.utils import secure_filename

from app import db, app
from app.forms import NewPost
from app.models import Posts

blueprint = Blueprint(
    'base_blueprint',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static')


@blueprint.route('/')
@blueprint.route('/page/<int:page>')
def home(page=1):
    posts = Posts.query.with_entities(Posts.id, Posts.title, Posts.content,
                                      Posts.created_time,
                                      Posts.tags).filter_by().order_by(
        Posts.created_time.desc()).paginate(page, Posts.PER_PAGE, False)
    current_page = posts.page
    user = flask_login.current_user
    return render_template('index.html', posts=posts, max_page=posts.pages,
                           current_page=current_page)


@blueprint.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create a post."""
    form = NewPost
    if request.method == 'POST':
        title = request.form.get('title').strip()
        content = request.form.get('content')
        new_post = Posts(title=title,
                         content=content, user_id=1,
                         created_time=datetime.now())
        db.session.add(new_post)  # Adds new Users record to database
        db.session.commit()  # Commits all changes
        return redirect(url_for('base_blueprint.home'))
    return render_template('new_post.html', form=form)


@blueprint.route('/edit_post/<post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit post."""
    form = NewPost
    print('TUTUT')
    if request.method == 'POST':
        post = Posts.query.get_or_404(post_id)
        title = request.form.get('title').strip()
        content = request.form.get('content')
        post.title = title
        post.content = content
        db.session.commit()  # Commits all changes
    post = Posts.query.filter(Posts.id == post_id).first_or_404()
    return render_template('new_post.html', form=form, title=post.title,
                           content=post.content)


def previous_post_id(pid):
    pid = int(pid)
    count = Posts.query.filter_by().count()
    prev_post = None
    while count > 0:
        pid = pid - 1
        if db.session.query(Posts).get(pid) is not None:
            prev_post = db.session.query(Posts).get(pid)
            break
        else:
            count = count - 1
    return prev_post


def next_post_id(pid):
    pid = int(pid)
    count = Posts.query.filter_by().count()
    next_post = None
    while count > 0:
        pid = pid + 1
        if db.session.query(Posts).get(pid) is not None:
            next_post = db.session.query(Posts).get(pid)
            break
        else:
            count = count - 1
    return next_post


@blueprint.route('/post/<post_id>', methods=['GET'])
def post(post_id):
    """Show a post."""
    post = Posts.query.filter(Posts.id == post_id).first_or_404()
    next_post = next_post_id(post_id)
    prev_post = previous_post_id(post_id)
    return render_template('post.html', post=post, prev_post=prev_post,
                           next_post=next_post)


@blueprint.route('/remove_post/<post_id>', methods=['GET'])
@login_required
def remove_post(post_id):
    """Remove post."""
    post = Posts.query.get_or_404(post_id)
    if post:
        db.session.delete(post)
        db.session.commit()  # Commits all changes
        return redirect(url_for('base_blueprint.home'))


def get_last_posts():
    """Show last posts."""
    posts = Posts.query.with_entities(Posts.id, Posts.title,
                                      Posts.created_time).order_by(
        desc(Posts.created_time)).limit(3).all()
    return posts


@app.before_request
def set_globals():
    app.jinja_env.globals['last_posts'] = get_last_posts()


@blueprint.route('/tag/<tag>', methods=['GET'])
def posts_by_tag(tag):
    posts = Posts.query.with_entities(Posts.id, Posts.title, Posts.content,
                                      Posts.created_time, Posts.tags). \
        filter_by(tags=tag).order_by(Posts.created_time.desc()).paginate(
        page=None, per_page=None, error_out=True,
        max_per_page=None)
    current_page = posts.page
    max_page = current_page
    return render_template('index.html', posts=posts, max_page=max_page,
                           current_page=current_page)


@blueprint.route('/search', methods=['GET'])
def search():
    what_you_need = request.query_string
    print(what_you_need)
    results = []
    posts = Posts.query.with_entities(Posts.id, Posts.title, Posts.content,
                                      Posts.created_time, Posts.tags). \
        filter_by().order_by(Posts.created_time.desc())
    for i in posts.all():
        results.append(
            {'id': i[0], 'title': i[1], 'plaintext': i[2], 'tags': i[4],
             'primary_tag': i[4],
             'excerpt': i[2][:100],
             'url': '{}/post/{}'.format(request.url_root, i[0])})
    end_result = {'posts': results}
    return jsonify(end_result)
    # return jsonify()


def allowed_file(filename):
    allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/file-upload', methods=['GET', 'POST'])
def file_upload():
    # TODO add post name for file
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
