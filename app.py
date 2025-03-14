from flask import Flask, render_template, request, send_file, redirect, url_for
from yt_dlp import YoutubeDL
import os
import threading
import time

app = Flask(__name__)

DOWNLOAD_FOLDER = "./downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Hàm tải video
def download_video(youtube_url, resolution):
    ydl_opts = {
        'format': f'bestvideo[height<={resolution}]+bestaudio/best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
    }
    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(youtube_url, download=True)
        filename = ydl.prepare_filename(result)
        return filename

# Hàm tải âm thanh
def download_audio(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(youtube_url, download=True)
        filename = ydl.prepare_filename(result).replace('.webm', '.mp3')
        return filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    youtube_url = request.form['url']
    download_type = request.form['type']  # 'video' hoặc 'audio'
    resolution = request.form.get('resolution', '720')  # Độ phân giải mặc định là 720p

    try:
        if download_type == 'video':
            file_path = download_video(youtube_url, resolution)
        elif download_type == 'audio':
            file_path = download_audio(youtube_url)
        else:
            return "Loại tải xuống không hợp lệ.", 400

        # Trả file cho người dùng
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"Lỗi: {str(e)}", 500

# Dọn dẹp file cũ tự động
def delete_old_files_periodically():
    while True:
        current_time = time.time()
        for filename in os.listdir(DOWNLOAD_FOLDER):
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > 24 * 60 * 60:  # File cũ hơn 1 ngày
                    os.remove(file_path)
        time.sleep(24 * 60 * 60)

if __name__ == "__main__":
    threading.Thread(target=delete_old_files_periodically, daemon=True).start()
    app.run(debug=True)
