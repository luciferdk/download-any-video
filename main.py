# backend.py
import os
import requests
from flask import Flask, request, send_from_directory, render_template
from urllib.parse import urlparse
from datetime import datetime

app = Flask(__name__)
app.config['DOWNLOAD_FOLDER'] = 'downloads'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'webm', 'avi', 'mov', 'mkv'}

# Create downloads directory if not exists
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_filename(url):
    # Create a filename from timestamp and URL parts
    parsed_url = urlparse(url)
    base_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{parsed_url.netloc}"
    return f"{base_name}.mp4"  # Default to .mp4 extension

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    try:
        video_url = request.form.get('url')
        if not video_url:
            return {'status': 'error', 'message': 'No URL provided'}, 400

        # Validate URL
        parsed_url = urlparse(video_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return {'status': 'error', 'message': 'Invalid URL'}, 400

        # Stream the download to handle large files
        response = requests.get(video_url, stream=True)
        if response.status_code != 200:
            return {'status': 'error', 'message': 'Failed to fetch video'}, 400

        # Generate filename
        filename = generate_filename(video_url)
        save_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)

        # Save the video
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return {'status': 'success', 'filename': filename}, 200

    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)