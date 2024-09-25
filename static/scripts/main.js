document.addEventListener('DOMContentLoaded', function() {
  let mediaRecorder;
  let audioChunks = [];
  const startRec = document.getElementById('startRecording');
  const scrapRec = document.getElementById('scrapRecording');
  const finishRec = document.getElementById('finishRecording');
  const result = document.getElementById('result');

  startRec.onclick = () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();

        mediaRecorder.addEventListener("dataavailable", event => {
          audioChunks.push(event.data);
        });

        startRec.disabled = true;
        scrapRec.disabled = false;
        finishRec.disabled = false;
      });
  };

  scrapRec.onclick = () => {
    mediaRecorder.stop();
    scrapRec.disabled = true;
    finishRec.disabled = true;

    mediaRecorder.addEventListener("stop", () => {
      audioChunks = [];
      startRec.disabled = false;
    });
  }

  finishRec.onclick = () => {
    mediaRecorder.stop();
    scrapRec.disabled = true;
    finishRec.disabled = true;

    mediaRecorder.addEventListener("stop", () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");

      fetch('/transcribe', {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        if (data.transcription) {
          result.textContent = data.transcription;
        } else {
          result.textContent = 'Error: ' + data.error;
        }
        startRec.disabled = false;
      })
      .catch(error => {
        console.log('Error:', error);
        result.textContent = 'An error occurred during transcription.';
        startRec.disabled = false;
      });

      audioChunks = [];
    });
  };
});
