from flask import Flask, request, jsonify
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from flask_cors import CORS
import google.generativeai as genai

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
CORS(app)

# Cấu hình Gemini API (thay bằng API key của bạn)
genai.configure(api_key='AIzaSyBVbwUc_adfRW9H8XbDy49SFea0N_JBaMw')

# Hàm chuyển đổi giọng nói thành văn bản
def transcribe_audio(audio_data, lang='en-US'):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_data) as source:
        audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language=lang)
    return text

# Hàm sử dụng API Gemini để thêm dấu câu
def add_punctuation(text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Prompt rõ ràng để hướng dẫn API thêm dấu câu
    prompt = (
        "Please add punctuation mark to make this text more logically ( output is the paragraph like the input but with punctuation mark)"
        f"{text}"
    )
    
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            candidate_count=1,
            stop_sequences=["x"],  # Thêm dừng nếu cần
            max_output_tokens=len(text) + 50,  # Điều chỉnh cho phù hợp với văn bản đầu vào
            temperature=0.7,
        ),
    )
    
    # Trả về văn bản đã được thêm dấu câu
    return response.text  # Lấy dữ liệu từ trường 'text'

# Định tuyến cho API upload file âm thanh
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

        # Thêm dấu câu sử dụng Gemini API
        punctuated_text = add_punctuation(text)

        return jsonify({"text": punctuated_text}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
