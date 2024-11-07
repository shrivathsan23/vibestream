import os

from vibestream import app

try:
    os.makedirs(os.path.join(app.root_path, app.config['UPLOADED_VIDEOS_DEST']))
    os.makedirs(os.path.join(app.root_path, app.config['UPLOADED_THUMBS_DEST']))

except Exception as e:
    pass

if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0')