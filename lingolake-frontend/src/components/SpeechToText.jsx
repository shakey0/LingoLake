import React, { useState, useRef } from 'react';

const SpeechToText = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [result, setResult] = useState('');
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);

  const startRecording = () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        mediaRecorder.current = new MediaRecorder(stream);
        mediaRecorder.current.start();

        mediaRecorder.current.addEventListener("dataavailable", event => {
          audioChunks.current.push(event.data);
        });

        setIsRecording(true);
      });
  };

  const stopMicrophone = () => {
    if (mediaRecorder.current && mediaRecorder.current.stream) {
      mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
    }
  };

  const scrapRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
      mediaRecorder.current.stop();
      setIsRecording(false);
      audioChunks.current = [];
      stopMicrophone();
    }
  };

  const finishRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
      mediaRecorder.current.stop();
      setIsRecording(false);

      mediaRecorder.current.addEventListener("stop", () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append("audio", audioBlob, "recording.webm");

        fetch('/transcribe', {
          method: 'POST',
          body: formData
        })
        .then(response => response.json())
        .then(data => {
          if (data.transcription) {
            setResult(data.transcription);
          } else {
            setResult('Error: ' + data.error);
          }
        })
        .catch(error => {
          console.log('Error:', error);
          setResult('An error occurred during transcription.');
        });

        stopMicrophone();
        audioChunks.current = [];
      });
    }
  };

  return (
    <div>
      <h1>Speech to Text</h1>
      <button onClick={startRecording} disabled={isRecording}>Record answer</button>
      <button onClick={scrapRecording} disabled={!isRecording}>Scrap</button>
      <button onClick={finishRecording} disabled={!isRecording}>Finish</button>
      <p>{result}</p>
    </div>
  );
};

export default SpeechToText;
