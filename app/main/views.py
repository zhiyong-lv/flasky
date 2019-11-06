from datetime import datetime
from flask import render_template, redirect, url_for, abort, flash
from flask import current_app, request
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required
from . import main
from .forms import PostForm, EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import User, Permission, Role, Post


@main.route('/post/<int:id>', endpoint='post', methods=['GET', 'POST'])
@login_required
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('main.post', id=post.id))
    form.body.data = post.body
    current_app.logger.debug('start render template')
    return render_template('edit_post.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('auth/common.html', form=form, user=user, header='Edit Profile - Input Related Informations')


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('auth/common.html', form=form, header='Edit Profile - Input Your New Informations')


@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators!"


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"


@main.route('/', endpoint='index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    # posts = Post.query.order_by(Post.timestamp.desc()).all()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination, current_time=datetime.utcnow())
    # form = NameForm()
    # login_name = session.get('name') if session.get('name') is not None else 'Stranger'
    # session['name'] = login_name if form.name.data is None else form.name.data
    # # first time, will return false, because client will send a GET request
    # # instead of a POST request
    # if form.validate_on_submit():
    #     existed_user = User.query.filter_by(username=form.name.data).first()
    #     if existed_user is None:
    #         user = User(username=form.name.data)
    #         db.session.add(user)
    #         session['known'] = False
    #         app = current_app._get_current_object()
    #         if app.config['FLASKY_ADMIN']:
    #             send_email(app.config['FLASKY_ADMIN'], 'New User',
    #                        'mail/new_user', user=form.name.data)
    #     else:
    #         session['known'] = True
    #     session['name'] = form.name.data
    #     form.name.data = None
    #     return redirect(url_for('main.index'))
    # return render_template('index.html', current_time=datetime.utcnow(), form=form,
    #                        known=session.get('known', False), name=session['name'])
