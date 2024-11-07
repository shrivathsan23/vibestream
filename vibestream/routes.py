import os

from vibestream.utils import *
from vibestream.forms import *
from vibestream.models import *
from vibestream import app, db, login_manager

from flask import abort, flash, redirect, render_template, request, Response, url_for
from flask_login import current_user, login_user, logout_user, login_required

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

UPLOADED_VIDEOS_DEST = app.config['UPLOADED_VIDEOS_DEST']
UPLOADED_THUMBS_DEST = app.config['UPLOADED_THUMBS_DEST']

@app.route('/')
def home():
    videos = sorted(Video.query.all(), key = lambda v: v.watch_count, reverse = True)
    users = {}

    for video in videos:
        users[video.id] = User.query.get(video.user_id).username
    
    return render_template('index.html', videos = videos, users = users)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('custom_404.html'), 404

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        hashed_password = generate_password_hash(form.password.data)

        if User.query.filter_by(username = username).first():
            flash('Username already exists!', 'warning')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email = email).first():
            flash('Email already exists!', 'warning')
            return redirect(url_for('register'))
        
        new_user = User(username = username, email = email, password = hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
        
        except:
            return render_template('custom_500.html'), 500

        flash('Account created successfully!', 'success')
        login_user(new_user)
        return redirect(url_for('home'))
    
    return render_template('register.html', title = 'Register', form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email = email).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        
        else:
            flash('Invalid Login credentials!', 'warning')
            return redirect(url_for('login'))
    
    return render_template('login.html', title = 'Login', form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    videos = current_user.videos
    return render_template('profile.html', videos = videos)

@app.route('/upload', methods = ['GET', 'POST'])
@login_required
def upload():
    form = VideoUploadForm()

    if form.validate_on_submit():
        title = form.title.data
        video = form.video.data
        filename = secure_filename(video.filename)
        
        video_entry = Video(title = title, filename = filename, uploader = current_user)

        try:
            db.session.add(video_entry)
            db.session.commit()
        
        except:
            return render_template('custom_500.html'), 500

        video_save_path = os.path.join(app.root_path, UPLOADED_VIDEOS_DEST, f'{video_entry.id}_{filename}')
        video.save(video_save_path)

        thumb_save_path = os.path.join(app.root_path, UPLOADED_THUMBS_DEST, f'{video_entry.id}.png')

        create_thumbnail(video_save_path, thumb_save_path)

        flash('Video Upload successfully!', 'success')
        return redirect(url_for('home'))
    
    return render_template('video_upload.html', form = form)

@app.route('/video/<int:video_id>')
def stream_video(video_id):
    video = Video.query.get_or_404(video_id)
    video_path = os.path.join(app.root_path, UPLOADED_VIDEOS_DEST, f'{video.id}_{video.filename}')
    video_extension = os.path.basename(video_path).split('.')[-1]

    uploader = User.query.get(video.user_id)
    uploader_videos = sorted(uploader.videos, key = lambda v: v.watch_count, reverse = True)

    thumb_path = os.path.join(app.root_path, UPLOADED_THUMBS_DEST, f'{video.id}.png')

    if not os.path.exists(thumb_path):
        create_thumbnail(video_path, thumb_path)
    
    video.watch_count += 1

    try:
        db.session.commit()
    
    except:
        return render_template('custom_500.html'), 500
    
    return render_template('video_stream.html', video = video, video_extension = video_extension, uploader = uploader.username, uploader_videos = uploader_videos)

@app.route('/watch/<int:video_id>')
def watch_video(video_id):
    video = Video.query.get_or_404(video_id)
    video_path = os.path.join(app.root_path, UPLOADED_VIDEOS_DEST, f'{video.id}_{video.filename}')
    video_extension = os.path.basename(video_path).split('.')[-1]
    video_size = os.path.getsize(video_path)

    range_header = request.headers.get('Range', None)

    if range_header:
        range_match = range_header.strip().lower().startswith('bytes=')

        if not range_match:
            abort(416)
        
        byte_range = range_header[6:]
        start_byte, end_byte = byte_range.split('-')

        start_byte = int(start_byte)
        end_byte = int(end_byte) if end_byte else start_byte + 1024 * 1024

        if start_byte >= video_size:
            abort(416)
        
        if end_byte > video_size:
            end_byte = video_size
        
        chunk = get_file_range(video_path, start_byte, end_byte)
        return Response(
            chunk,
            status = 206,
            content_type = f'video/{video_extension}',
            headers = {
                'Content-Range': f'bytes {start_byte}-{end_byte - 1}/{video_size}',
                'Accept-Ranges': 'bytes',
                'Content-Disposition': 'inline'
            }
        )
    
    return Response(
        open(video_path, 'rb').read(),
        status = 200,
        content_type = f'video/{video_extension}',
        headers = {
            'Content-Disposition': 'inline'
        }
    )

@app.route('/user/<string:username>')
def user_profile(username):
    user = User.query.filter_by(username = username).first()

    if user:
        if user == current_user:
            return redirect(url_for('profile'))
        else:
            videos = user.videos
            return render_template('user_profile.html', username = username, videos = videos)
    
    return render_template('custom_404.html'), 404

@app.route('/like/<int:video_id>')
@login_required
def like_video(video_id):
    return 'Video Liked'

@app.route('/comment/<int:video_id>')
@login_required
def comment_video(video_id):
    return 'Commented'

@app.route('/reply/<int:comment_id>')
@login_required
def reply_comment(comment_id):
    return 'Replied'