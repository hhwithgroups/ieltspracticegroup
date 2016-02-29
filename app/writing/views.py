__author__ = 'wei'

from flask import request, redirect, url_for, render_template, flash, current_app
from flask.ext.login import login_required, login_user, logout_user, current_user
from .forms import ArticleForm, CommentForm, AnnotationForm
from ..models import Article, ArticleComment, ArticleAnnotation, WritingCategory, WritingTopic
from .. import app, db
import json

@app.route('/writing')
@login_required
def writing():
    return redirect(url_for('writing_all_articles'))


# def _get_categories():
#     category_query = WritingCategory.query.with_entities(WritingCategory.id, WritingCategory.category)
#     all_cat = category_query.filter_by(pseudo_all=True).first()
#     other_cat = category_query.filter_by(pseudo_all=False, deleted=False).all()
#     other_cat.sort()
#     categories = [all_cat] + other_cat
#     return categories
#
#
# def _get_issues(cat, all=False):
#     all_issues = WritingTopic.query.order_by(WritingTopic.issue_number.desc())
#     if all:
#         issues = all_issues.filter_by(deleted=False).all()
#     else:
#         issues = all_issues.filter_by(category_id=cat, deleted=False).all()
#     return issues
#
#
# def _get_cat_issues(request):
#     categories = _get_categories()
#     cur_cat = int(request.args.get('category', categories[0][0]))
#     all = (cur_cat == categories[0][0])
#     issues = _get_issues(cur_cat, all)
#     cur_issue = request.args.get('issue', issues[0].issue_number if issues else 0)
#     current_topic = WritingTopic.query.filter_by(issue_number=int(cur_issue)).first()
#     return categories, cur_cat, issues, cur_issue, current_topic


@app.route('/writing/my-articles', methods=['GET', 'POST'])
@login_required
def writing_my_articles():
    form = ArticleForm()
    category_id = request.args.get('category', None, type=int)
    issue_number = request.args.get('issue', None, type=int)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['WRITING_ARTICLES_PER_PAGE']

    category_query = WritingCategory.query
    topic_query = WritingTopic.query.order_by(WritingTopic.issue_number.desc())
    article_query = current_user.articles.order_by(Article.timestamp.desc())
    if category_id is not None:
        topic_query = topic_query.filter_by(category_id=category_id)

    categories = category_query.all()
    topics = topic_query.all()
    current_topic = topic_query.filter_by(issue_number=issue_number).first()
    if not current_topic and topics:
        current_topic = topics[0]
        issue_number = topics[0].issue_number

    if form.validate_on_submit():
        topic = WritingTopic.query.filter_by(issue_number=issue_number, deleted=False).first()
        if topic is None:
            flash('Invalid topic')
            return redirect(url_for('writing_my_articles', category=category_id, issue=issue_number))
        category = WritingCategory.query.filter_by(id=topic.category_id, deleted=False).first()
        if topic is not None and category is not None:
            a = Article(category_id=topic.category_id, topic_id=topic.id,
                        content=form.content.data, author_id=current_user.id)
            db.session.add(a)
            flash('Your article has been published.')
        else:
            flash('Invalid category or topic.')
        return redirect(url_for('writing_my_articles', category=category_id, issue=issue_number))

    pagination = article_query.paginate(page, per_page=per_page, error_out=False)
    articles = pagination.items

    return render_template('writing/my-articles.html',
                           type='self', endpoint='writing_my_articles',
                           categories=categories, category_id=category_id,
                           topics=topics, issue_number=issue_number,
                           current_topic=current_topic, articles=articles,
                           form=form, pagination=pagination)

    # form = ArticleForm()
    #
    # categories, cur_cat, issues, cur_issue, current_topic = _get_cat_issues(request)
    # topic = current_topic.topic if current_topic else ''
    #
    # if form.validate_on_submit():
    #     topic = WritingTopic.query.filter_by(issue_number=int(cur_issue), deleted=False).first()
    #     category = WritingCategory.query.filter_by(id=topic.category_id, deleted=False).first()
    #     if topic is not None and category is not None:
    #         a = Article(category_id=topic.category_id, topic_id=topic.id,
    #                     content=form.content.data, author_id=current_user.id)
    #         db.session.add(a)
    #         flash('Your article has been published.')
    #     else:
    #         flash('Invalid category or topic.')
    #     return redirect(url_for('writing_my_articles', category=cur_cat, issue=cur_issue))
    #
    # page = request.args.get('page', 1, type=int)
    # if current_topic:
    #     pagination = current_user.articles \
    #                         .order_by(Article.timestamp.desc()) \
    #                         .paginate(page,
    #                                  per_page=current_app.config['WRITING_ARTICLES_PER_PAGE'],
    #                                  error_out=False)
    #     articles = pagination.items
    # else:
    #     pagination = None
    #     articles = []
    # return render_template('writing/my-articles.html',
    #                        type='self', form=form, endpoint='writing_my_articles',
    #                        categories=categories, cur_cat=int(cur_cat),
    #                        issues=issues, cur_issue=int(cur_issue),
    #                        topic=topic, articles=articles,
    #                        pagination=pagination)


@app.route('/writing/all-articles')
@login_required
def writing_all_articles():
    category_id = request.args.get('category', None, type=int)
    issue_number = request.args.get('issue', None, type=int)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['WRITING_ARTICLES_PER_PAGE']

    category_query = WritingCategory.query
    topic_query = WritingTopic.query.order_by(WritingTopic.issue_number.desc())
    article_query = Article.query.order_by(Article.timestamp.desc())
    if category_id is not None:
        topic_query = topic_query.filter_by(category_id=category_id)
        article_query = article_query.filter_by(category_id=category_id)
    if issue_number is not None:
        article_query = article_query.join(WritingTopic, WritingTopic.id==Article.topic_id) \
                                     .filter(WritingTopic.issue_number==issue_number)

    categories = category_query.all()
    topics = topic_query.all()
    current_topic = topic_query.filter_by(issue_number=issue_number).first()
    pagination = article_query.paginate(page, per_page=per_page, error_out=False)
    articles = pagination.items

    return render_template('writing/all-articles.html',
                           type='all', endpoint='writing_all_articles',
                           categories=categories, category_id=category_id,
                           topics=topics, issue_number=issue_number,
                           current_topic=current_topic, articles=articles,
                           pagination=pagination)


    # categories, cur_cat, issues, cur_issue, current_topic = _get_cat_issues(request)
    # topic = current_topic.topic if current_topic else ''
    #
    # page = request.args.get('page', 1, type=int)
    # if current_topic:
    #     pagination = Article.query \
    #                         .order_by(Article.timestamp.desc()) \
    #                         .filter_by(topic_id=current_topic.id) \
    #                         .paginate(page,
    #                                   per_page=current_app.config['WRITING_ARTICLES_PER_PAGE'],
    #                                   error_out=False)
    #     articles = pagination.items
    # else:
    #     pagination = None
    #     articles = []
    # return render_template('writing/all-articles.html',
    #                        type='all', endpoint='writing_all_articles',
    #                        categories=categories, cur_cat=int(cur_cat),
    #                        issues=issues, cur_issue=int(cur_issue),
    #                        topic=topic, articles=articles,
    #                        pagination=pagination)


@app.route('/writing/commented-article')
@login_required
def writing_commented_articles():
    category_id = request.args.get('category', None, type=int)
    issue_number = request.args.get('issue', None, type=int)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['WRITING_ARTICLES_PER_PAGE']

    category_query = WritingCategory.query
    article_query = current_user.commented_and_annotated_articles \
                                .order_by(Article.timestamp.desc())
    topic_ids = article_query.with_entities(Article.topic_id).distinct().all()
    topic_ids = [t[0] for t in topic_ids]
    topic_query = WritingTopic.query.order_by(WritingTopic.issue_number.desc()) \
                                    .filter(WritingTopic.id.in_(topic_ids))
    if category_id is not None:
        topic_query = topic_query.filter_by(category_id=category_id)
        article_query = article_query.filter_by(category_id=category_id)
    if issue_number is not None:
        article_query = article_query.join(WritingTopic, WritingTopic.id==Article.topic_id) \
                                     .filter(WritingTopic.issue_number==issue_number)

    categories = category_query.all()
    topics = topic_query.all()
    current_topic = topic_query.filter(WritingTopic.issue_number==issue_number).first()
    pagination = article_query.paginate(page, per_page=per_page, error_out=False)
    articles = pagination.items

    return render_template('writing/all-articles.html',
                           type='commented', endpoint='writing_commented_articles',
                           categories=categories, category_id=category_id,
                           topics=topics, issue_number=issue_number,
                           current_topic=current_topic, articles=articles,
                           pagination=pagination)

    # (categories, cur_cat, issues,
    #  cur_issue, current_topic) = _get_cat_issues(request)
    # topic = current_topic.topic if current_topic else ''
    #
    # page = request.args.get('page', 1, type=int)
    # if current_topic:
    #     pagination = current_user.commented_and_annotated_articles \
    #                              .order_by(Article.timestamp.desc()) \
    #                              .paginate(page,
    #                                        per_page=current_app.config['WRITING_ARTICLES_PER_PAGE'],
    #                                        error_out=False)
    #     articles = pagination.items
    # else:
    #     pagination = None
    #     articles = []
    # return render_template('writing/all-articles.html',
    #                        type='commented', endpoint='writing_commented_articles',
    #                        categories=categories, cur_cat=int(cur_cat),
    #                        issues=issues, cur_issue=int(cur_issue),
    #                        topic=topic, articles=articles,
    #                        pagination=pagination)


@app.route('/writing/view-article/<int:id>')
@login_required
def writing_view_article(id):
    article = Article.query.get_or_404(id)
    if article.topic.deleted:
        return redirect(url_for('admin_all_articles'))
    page = request.args.get('page', 1, type=int)
    sub = request.args.get('sub', 'comment')
    comment_form = CommentForm()
    annotation_form = AnnotationForm()
    pagination = article.comments.order_by(ArticleComment.timestamp.desc()).paginate(
        page, per_page=current_app.config['WRITING_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    annotations = []
    for a in article.annotations.order_by(ArticleAnnotation.start).all():
        a_json = {"author": a.author.nickname,
                  "author_avatar": a.author.gravatar(size=50),
                  "content": a.content,
                  "timestamp": str(a.timestamp),
                  "start": a.start,
                  "end": a.end}
        annotations.append(a_json)
    annotations = json.dumps(json.dumps(annotations))
    return render_template('writing/view-article.html',
                           article=article, type='view',
                           pagination=pagination,
                           comment_form=comment_form,
                           comments=comments,
                           annotation_form=annotation_form,
                           annotations=annotations,
                           sub=sub)


@app.route('/writing/comment/<int:id>', methods=['POST'])
@login_required
def writing_comment(id):
    form = CommentForm()
    if form.validate_on_submit():
        article = Article.query.get(id)
        if article is not None:
            c = ArticleComment(author_id=current_user.id,
                               content=form.content.data,
                               article_id=id)
            db.session.add(c)
            flash('Your comment has been committed.')
        else:
            flash('Invalid article.')
    return redirect(url_for('writing_view_article', id=id, sub='comment'))


@app.route('/writing/annotate/<int:id>', methods=['POST'])
@login_required
def writing_annotate(id):
    form = AnnotationForm()
    if form.validate_on_submit():
        article = Article.query.get(id)
        if article is not None:
            c = ArticleAnnotation(author_id=current_user.id,
                               content=form.content.data,
                               article_id=id,
                               start=form.start.data,
                               end=form.end.data)
            db.session.add(c)
            flash('Your annotation has been committed.')
        else:
            flash('Invalid article.')
    return redirect(url_for('writing_view_article', id=id, sub='annotate'))

