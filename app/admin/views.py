from flask import request, redirect, url_for, render_template, flash, current_app
from flask.ext.login import login_required, current_user
from .forms import CategoryForm, TopicForm
from ..models import User, WritingCategory, WritingTopic
from .. import app, db
from ..decorators import admin_required


@app.route('/admin')
@login_required
@admin_required
def admin():
    return redirect(url_for('admin_topics'))


@app.route('/admin/topics')
@login_required
@admin_required
def admin_topics():
    cat_form = CategoryForm()
    topic_form = TopicForm()
    categories = WritingCategory.query.filter(WritingCategory.deleted==False).all()
    current_category_id = request.args.get('category_id', None)
    if not categories:
        current_category = None
        topics = None
        pagination = None
    else:
        page = request.args.get('page', 1, type=int)
        current_category = WritingCategory.query.get(current_category_id) \
                           if current_category_id is not None \
                           else categories[0]
        pagination = WritingTopic.query.filter(WritingTopic.category_id==current_category.id,
                                               WritingTopic.deleted==False) \
                                       .paginate(page,
                                                 per_page=current_app.config['ADMIN_TOPICS_PER_PAGE'],
                                                 error_out=False)
        topics = pagination.items
    return render_template('/admin/topics.html',
                           type='topics',
                           cat_form=cat_form, topic_form=topic_form,
                           categories=categories, current_category=current_category,
                           topics=topics,
                           pagination=pagination)


@app.route('/admin/add-category', methods=['POST'])
@login_required
@admin_required
def admin_add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = form.category.data
        c = WritingCategory.query.filter_by(category=category).first()
        if c is None:
            c = WritingCategory(category=category)
        c.deleted = False
        db.session.add(c)
        db.session.commit()
        flash('New category added.')
        return redirect(url_for('admin_topics', category_id=c.id))
        # else:
        #     flash('Cannot add existing category.')
    return redirect(url_for('admin_topics'))


@app.route('/admin/add-topic/<int:category_id>', methods=['POST'])
@login_required
@admin_required
def admin_add_topic(category_id):
    form = TopicForm()
    if form.validate_on_submit():
        topic = form.topic.data
        category = WritingCategory.query.get(category_id)
        if category is not None:
            t = WritingTopic(category_id=category_id, topic=topic)
            db.session.add(t)
            db.session.commit()
            flash('New topic added.')
        else:
            flash('Invalid category.')
    return redirect(url_for('admin_topics', category_id=category_id))


@app.route('/admin/delete-category/<int:category_id>')
@login_required
@admin_required
def admin_del_category(category_id):
    topics = WritingTopic.query.filter_by(category_id=category_id).all()
    for t in topics:
        t.deleted = True
        db.session.add(t)
    category = WritingCategory.query.get_or_404(category_id)
    category.deleted = True
    db.session.add(category)
    db.session.commit()
    return redirect(url_for('admin_topics'))


@app.route('/admin/delete-topic/<int:category_id>/<int:topic_id>')
@login_required
@admin_required
def admin_del_topic(category_id, topic_id):
    topic = WritingTopic.query.get_or_404(topic_id)
    topic.deleted = True
    db.session.add(topic)
    db.session.commit()
    return redirect(url_for('admin_topics', category_id=category_id))

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    login_users = db.session.query('id', 'nickname', 'qq', 'wechat_id', 'latest_login_date').from_statement(
        db.text('select id, nickname, qq, wechat_id, latest_login_date'
                ' from users'
                " where latest_login_date > '2016-03-01'"
                ' order by latest_login_date desc limit 20')).all()
    friends = db.session.query('nickname', 'nickname2', 'timestamp').from_statement(
        db.text('select A.nickname, B.nickname as nickname2, friends.timestamp'
                ' from friends join users A on user1_id=A.id'
                ' join users B on user2_id=B.id'
                ' where user1_id>user2_id'
                ' order by friends.timestamp desc limit 10')).all()
    invitations = db.session.query('nickname', 'nickname2', 'invitation_date').from_statement(
        db.text('select A.nickname, B.nickname as nickname2, invitation_date'
                ' from invitations join users A on from_user_id=A.id'
                ' join users B on to_user_id=B.id'
                ' order by invitation_date desc limit 20')).all()
    return render_template('admin/users.html',
                           type='users',
                           login_users=login_users,
                           friends=friends,
                           invitations=invitations)
