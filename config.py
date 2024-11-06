class Config:
    SECRET_KEY = 'secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_VIDEOS_DEST = 'static/videos'
    UPLOADED_THUMBS_DEST = 'static/images/thumbs'