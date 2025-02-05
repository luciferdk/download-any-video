
from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

def download_video(video_url, output_path='downloaded_video.mp4'):
    try:
        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        os.makedirs('downloads', exist_ok=True)
        output_path = os.path.join('downloads', output_path)

        with open(output_path, 'wb') as video_file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    video_file.write(chunk)
                    downloaded_size += len(chunk)

        return True, f"Download complete! Video saved as: {output_path}"
    except requests.exceptions.RequestException as e:
        return False, f"Error occurred: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def handle_download():
    data = request.json
    video_url = data.get('video_url')
    filename = data.get('filename', 'downloaded_video.mp4')

    success, message = download_video(video_url, filename)
    return jsonify({'success': success, 'message': message})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
