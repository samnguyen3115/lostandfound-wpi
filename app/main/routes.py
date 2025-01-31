import io
import mimetypes
import sys
from flask import Response, abort, render_template, flash, redirect, send_file, url_for, request, jsonify
from flask_login import current_user, login_required
from sqlalchemy.orm import selectinload
import sqlalchemy as sqla

from app import db
from app.main.models import Post, Report, Tag, postTags, ImageStore, Building, User
from app.main.forms import FilterForm, FoundPostForm, LostPostForm

from app.main import main_blueprint as bp_main


@bp_main.route('/', methods=['GET'])
@bp_main.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = FilterForm()
    color_filter = request.args.get('color_filter')
    building_filter = request.args.get('building_filter')
    post_type = request.args.get('post_type', 'found')
    form.color_filter.data = color_filter
    form.building_filter.data = building_filter

    page = request.args.get('page', 1, type=int)
    per_page = 9

    # Start building the query
    query = sqla.select(Post).where(Post.type == post_type).order_by(Post.timestamp.desc())

    # Apply filters if selected
    if color_filter:
        query = query.where(Post.color_tag_id == color_filter)
    if building_filter:
        query = query.where(Post.building_tag_id == building_filter)

    # Reset filters if the refresh button is clicked
    if request.args.get('submit2'):
        query = sqla.select(Post).where(Post.type == post_type).order_by(Post.timestamp.desc())

    # Apply pagination
    paginated_posts = db.paginate(query, page=page, per_page=per_page)

    # Flash message if no results found
    if not paginated_posts.items:
        flash('No posts found with the selected filters')

    return render_template('index.html', title="Lost And Found Portal", posts=paginated_posts, form=form)


@bp_main.route('/post/found', methods=['GET', 'POST'])
@login_required
def post_found():
    form = FoundPostForm()
    if form.validate_on_submit():
        post = Post(writer=current_user,
                    title=form.title.data,
                    color_tag=form.color_tag.data,
                    building_tag=form.building_tag.data,
                    left_location=form.left_location.data,
                    type='found')
        db.session.add(post)
        db.session.commit()
        if form.image.data:
            image_file = form.image.data
            image_data = image_file.read()  # Read the file data as binary
            # Guess the MIME type based on file extension
            image_type = mimetypes.guess_type(image_file.filename)[0]
            image = ImageStore(
                post_id=post.id, image_data=image_data, image_type=image_type)
            db.session.add(image)
            db.session.commit()
        flash('Your new post is created')
        return redirect(url_for('main.index'))
    return render_template('create_found_post.html', title='Post', form=form)


@bp_main.route('/post/lost', methods=['GET', 'POST'])
@login_required
def post_lost():
    form = LostPostForm()
    if form.validate_on_submit():
        post = Post(writer=current_user,
                    title=form.title.data,
                    color_tag=form.color_tag.data,
                    building_tag=form.building_tag.data,
                    reward=form.reward.data,
                    left_location=form.description.data,
                    type='lost')
        db.session.add(post)
        db.session.commit()
        if form.image.data:
            image_file = form.image.data
            image_data = image_file.read()  # Read the file data as binary
            # Guess the MIME type based on file extension
            image_type = mimetypes.guess_type(image_file.filename)[0]
            image = ImageStore(
                post_id=post.id, image_data=image_data, image_type=image_type)
            db.session.add(image)
            db.session.commit()
        flash('Your new post is created')
        return redirect(url_for('main.index'))
    return render_template('create_lost_post.html', title='Post', form=form)


@bp_main.route('/image/<int:post_id>')
def get_image(post_id):
    image_record = db.session.query(
        ImageStore).filter_by(post_id=post_id).first()
    if image_record is None or image_record.image_data is None:
        abort(404)
    return Response(image_record.image_data, mimetype=image_record.image_type or 'image/jpeg')


@bp_main.route('/post/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.userid != current_user.id:
        flash("You are not authorized to delete this post.", "danger")
        return redirect(url_for('main.index'))

    # Delete associated images explicitly if cascading is not enabled
    ImageStore.query.filter_by(post_id=post_id).delete()

    # Delete the post
    db.session.delete(post)
    db.session.commit()

    flash("Post deleted successfully!", "success")
    return redirect(url_for('main.index'))


@bp_main.route('/post/<post_id>/detail', methods=['GET', 'POST'])
@login_required
def post_detail(post_id):
    post = db.session.scalars(sqla.select(
        Post).where(Post.id == post_id)).first()
    reports = post.report 
    if post is None:
        flash('Post not found')
    return render_template('post_detail.html', title='Post Detail', post=post, reports = reports)


@bp_main.route('/map', methods=['GET'])
@login_required
def map():
    return render_template('map.html', title='Map')


@bp_main.route('/building/<building_id>', methods=['GET'])
@login_required
def map_building(building_id):
    building = db.session.get(Building, building_id)
    name = building.get_name()
    place = building.get_place()
    body = building.get_body()
    count = building.get_count()
    theme = building.get_theme()
    image = building.get_image()
    places_info = zip(place, body, image)
    return render_template('building.html', title='Map', building_id=building_id, name=name, place=place, body=body, count=count, theme=theme, image=image, places_info=places_info)


@bp_main.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def display_profile(user_id):
    user = db.session.get(User, user_id)
    form = FilterForm()
    color_filter = request.args.get('color_filter')
    building_filter = request.args.get('building_filter')
    form.color_filter.data = color_filter
    form.building_filter.data = building_filter
    print(f"Color Filter: {color_filter}")
    print(f"Building Filter: {building_filter}")
    # Start building the query for all posts ordered by timestamp
    query = db.session.scalars(sqla.select(Post).where(
        Post.writer == user).order_by(Post.timestamp.desc()))

    # If there is a color filter, add the condition to filter based on the color tag's name
    if color_filter and color_filter != '':
        if building_filter and building_filter != '':
            query = db.session.scalars(sqla.select(Post).where(sqla.and_(
                Post.color_tag_id == color_filter, Post.building_tag_id == building_filter, Post.writer == user)))
        else:
            query = db.session.scalars(sqla.select(Post).where(
                sqla.and_(Post.color_tag_id == color_filter, Post.writer == user)))
    else:
        if (building_filter) and building_filter != '':
            query = db.session.scalars(sqla.select(Post).where(
                sqla.and_(Post.building_tag_id == building_filter, Post.writer == user)))
    all_posts = query.all()

# For admin to view reported posts
    reported_query = db.session.scalars(
        sqla.select(Post)
        .distinct(Post.id)
        .join(Report)
        .where(Report.get_reported == True)
        .order_by(Post.id, Post.timestamp.desc())
    )
    if color_filter and color_filter != '':
        reported_query = reported_query.join(
            Tag, Tag.id == Post.color_tag_id).filter(Tag.name == color_filter)

    if building_filter and building_filter != '':
        reported_query = reported_query.filter(
            Post.building_tag_id == building_filter)

    refresh = request.args.get('submit2')
    if refresh:
        query = db.session.scalars(sqla.select(Post).where(
            Post.writer == user).order_by(Post.timestamp.desc()))
        reported_query = db.session.scalars(
            sqla.select(Post)
            .distinct(Post.id)
            .join(Report)
            .where(Report.get_reported == True)
            .order_by(Post.id, Post.timestamp.desc())
        )
    all_reported_posts = reported_query.all()
    if not all_posts:
        if db.session.scalars(sqla.select(Post)).all():
            flash('No posts found')
        all_posts = db.session.scalars(sqla.select(Post).where(
            Post.writer == user).order_by(Post.timestamp.desc())).all()

    if not all_reported_posts:
        if db.session.scalars(sqla.select(Post).join(Report).where(Report.get_reported == True)).all():
            flash('No reported posts found')
        all_reported_posts = db.session.scalars(
            sqla.select(Post)
            .distinct(Post.id)
            .join(Report)
            .where(Report.get_reported == True)
            .order_by(Post.id, Post.timestamp.desc())
        ).all()
    return render_template('display_profile.html', title='My Profile', user=user, posts=all_posts, form=form, reported_posts=all_reported_posts)


@bp_main.route('/guide', methods=['GET', 'POST'])
def guide():
    return render_template('guide.html', title='Guide')


@bp_main.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html', title='About')


@bp_main.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html', title='Contact')


@bp_main.route('/report/<int:post_id>', methods=['GET', 'POST'])
def report_post(post_id):
    post = Post.query.get_or_404(post_id)

    # # Check if the user is trying to report their own post
    # if post.userid == current_user.id:
    #     flash("You cannot report your own post.", "danger")
    #     return redirect(url_for('main.index'))

    # # Check if the post has already been reported by the current user
    # existing_report = Report.query.filter_by(post_id=post.id).first()
    # if existing_report:
    #     flash("You have already reported this post.", "warning")
    #     return redirect(url_for('main.index'))

    # Handle the report reason from the form (POST)
    if request.method == 'POST':
        report_reason = request.form.get('report_reason')

        # Create a new report with the reason
        new_report = Report(
            post_id=post.id,
            get_reported=True,
            report_reason=report_reason
        )
        db.session.add(new_report)
        db.session.commit()

        flash("Post reported successfully!", "success")
        return redirect(url_for('main.post_detail', post_id=post.id))

    return redirect(url_for('main.post_detail', post_id=post.id))

