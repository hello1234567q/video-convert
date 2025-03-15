from flask import Flask, request, jsonify, send_file, render_template
from io import BytesIO
import yt_dlp

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/donate')
def donate():
    return render_template('donate.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    download_type = data.get('type')  # 'video' hoặc 'audio'

    if not url or download_type not in ['video', 'audio']:
        return jsonify({'error': 'Invalid request parameters'}), 400

    ydl_opts = {
        'format': 'bestvideo+bestaudio' if download_type == 'video' else 'bestaudio',
        'noplaylist': True,
        'quiet': True,
    }

    try:
        buffer = BytesIO()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', 'download')  # Lấy tiêu đề video
            extension = 'mp4' if download_type == 'video' else 'mp3'

            # Ghi file tạm vào buffer
            ydl.download([url])
            buffer.seek(0)

            # Gửi file về client với tên tệp
            return send_file(
                buffer,
                mimetype=f'video/{extension}' if download_type == 'video' else 'audio/mpeg',
                as_attachment=True,
                download_name=f"{title}.{extension}"  # Sử dụng tiêu đề làm tên tệp
            )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
