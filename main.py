from flask import Flask, request, jsonify
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

def transcribe_audio(audio_data, lang='en-US'):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_data) as source:
        audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language=lang)
    return text

@app.route('/upload', methods=['POST'])
def upload():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided."}), 400

    audio_file = request.files['audio']
    
    if audio_file.filename == '':
        return jsonify({"error": "No file selected."}), 400

    if not (audio_file.filename.endswith('.mp3') or audio_file.filename.endswith('.wav')):
        return jsonify({"error": "Unsupported file format. Please upload an MP3 or WAV file."}), 400

    # Nhận ngôn ngữ từ request
    lang = request.form.get('language', 'en-US')

    # Đọc tệp âm thanh vào BytesIO
    audio_data = BytesIO(audio_file.read())

    try:
        if audio_file.filename.endswith('.mp3'):
            # Chuyển đổi MP3 sang WAV
            audio_segment = AudioSegment.from_mp3(audio_data)
            wav_data = BytesIO()
            audio_segment.export(wav_data, format='wav')
            wav_data.seek(0)  # Đặt con trỏ về đầu tệp
            text = transcribe_audio(wav_data, lang)
        elif audio_file.filename.endswith('.wav'):
            text = transcribe_audio(audio_data, lang)

        return jsonify({"text": text}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
