from flask import Flask, request, jsonify, render_template
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import speech_recognition as sr
from pydub import AudioSegment
from dotenv import load_dotenv
from lib.process_answer import process_answer
import io

app = Flask(__name__)

load_dotenv()

talisman = Talisman(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["500 per day", "100 per hour"]
)

@app.route('/')
@limiter.limit("10 per minute")
def index():
  return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
@limiter.limit("10 per minute")
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
      feedback = process_answer.process("What do you usually do at the weekend?", text, "Chinese", "A2")
      print("FEEDBACK")
      print(feedback)
      return jsonify({'feedback': feedback['response']})
    except sr.UnknownValueError:
      return jsonify({'error': 'Speech recognition could not understand the audio'}), 400
    except sr.RequestError:
      return jsonify({'error': 'Could not request results from speech recognition service'}), 500
    
@app.route('/evaluate', methods=['POST'])
@limiter.limit("10 per minute")
def evaluate():
  data = request.get_json()
  answer = data.get('answer')
  feedback = process_answer.process("What do you usually do at the weekend?", answer, "Chinese", "A2")
  print(feedback)
  return jsonify({'feedback': feedback['response']})

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5001, debug=True)
