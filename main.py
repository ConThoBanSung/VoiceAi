from flask import Flask, request, jsonify
import speech_recognition as sr
from pydub import AudioSegment
import os
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Tạo thư mục uploads nếu nó không tồn tại
if not os.path.exists('uploads'):
    os.makedirs('uploads')

def transcribe_audio(audio_path, lang='en-US'):  # Mặc định là tiếng Anh
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language=lang)  # Thêm tham số ngôn ngữ
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
    lang = request.form.get('language', 'en-US')  # Ngôn ngữ mặc định là tiếng Anh

    audio_filename = secure_filename(audio_file.filename)
    audio_path = os.path.join('uploads', audio_filename)
    audio_file.save(audio_path)

    try:
        if audio_file.filename.endswith('.mp3'):
            wav_path = os.path.join('uploads', 'uploaded_audio.wav')
            AudioSegment.from_mp3(audio_path).export(wav_path, format='wav')
            text = transcribe_audio(wav_path, lang)  # Truyền ngôn ngữ vào hàm
        elif audio_file.filename.endswith('.wav'):
            text = transcribe_audio(audio_path, lang)  # Truyền ngôn ngữ vào hàm
        
        return jsonify({"text": text}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if 'wav_path' in locals() and os.path.exists(wav_path):
            os.remove(wav_path)

if __name__ == '__main__':
    app.run(debug=True)
