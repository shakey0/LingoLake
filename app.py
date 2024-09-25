from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
from pydub import AudioSegment
import io

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
  if 'audio' not in request.files:
    return jsonify({'error': 'No audio file provided'}), 400

  audio_file = request.files['audio']
  print('Received audio file:', audio_file.filename)
  
  # Convert the audio to WAV format
  audio = AudioSegment.from_file(audio_file)
  wav_audio = io.BytesIO()
  audio.export(wav_audio, format="wav")
  wav_audio.seek(0)

  # Perform speech recognition
  recognizer = sr.Recognizer()
  with sr.AudioFile(wav_audio) as source:
    audio_data = recognizer.record(source)
    try:
      text = recognizer.recognize_google(audio_data)
      return jsonify({'transcription': text})
    except sr.UnknownValueError:
      return jsonify({'error': 'Speech recognition could not understand the audio'}), 400
    except sr.RequestError:
      return jsonify({'error': 'Could not request results from speech recognition service'}), 500

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5001, debug=True)
