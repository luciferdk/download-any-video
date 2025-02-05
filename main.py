import os
import requests
from flask import Flask, request, jsonify, render_template
from urllib.parse import urlparse
from datetime import datetime

app = Flask(__name__)
app.config['DOWNLOAD_FOLDER'] = 'downloads'
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

def generate_filename(url):
    parsed_url = urlparse(url)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{timestamp}_{parsed_url.netloc}.mp4"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    try:
        video_url = request.form.get('url')
        if not video_url:
            return jsonify({'status': 'error', 'message': 'No URL provided'}), 400

        parsed_url = urlparse(video_url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            return jsonify({'status': 'error', 'message': 'Invalid URL'}), 400

        response = requests.get(video_url, stream=True, timeout=10)
        response.raise_for_status()

        filename = generate_filename(video_url)
        save_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return jsonify({'status': 'success', 'filename': filename})

    except requests.exceptions.RequestException as e:
        return jsonify({'status': 'error', 'message': f"Network error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f"Server error: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)