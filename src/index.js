import * as smd from "streaming-markdown";

const muteButton = document.getElementById("muteButton");
const muteIcon = document.getElementById("muteIcon");
const volumeSlider = document.getElementById("volumeSlider");
const transcription = document.getElementById("transcription");
const startRecording = document.getElementById("startRecording");
const stopRecording = document.getElementById("stopRecording");
const getLocation = document.getElementById("getLocation");
const location = document.getElementById("location");
const askQuestion = document.getElementById("askQuestion");
const questionInput = document.getElementById("questionInput");
const llmResponse = document.getElementById("llmResponse");

let audioElement = new Audio();
audioElement.muted = true;

function getCurrentPosition() {
  return new Promise((resolve, reject) => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(resolve, reject);
    } else {
      reject(new Error("Geolocation is not supported by this browser."));
    }
  });
}

async function sendLocationToBackend() {
  try {
    const position = await getCurrentPosition();
    const { latitude, longitude } = position.coords;

    location.textContent =
      "Latitude : " + latitude + " - Longitude : " + longitude;

    const response = await fetch("/wikipedia", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ latitude, longitude }),
    });

    await processStreamedResponse(response);
  } catch (error) {
    console.error("Error getting location or fetching LLM data:", error);
  }
}

function deleteAudio(audioPath) {
  fetch("/delete_audio", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ audio_path: audioPath }),
  })
    .then((response) => {
      if (response.ok) {
        console.log("Audio file deleted successfully");
      } else {
        console.error("Failed to delete audio file");
      }
    })
    .catch((error) => {
      console.error("Error deleting audio file:", error);
    });
}

async function processStreamedResponse(response) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let result = "";
  llmResponse.textContent = "";
  const renderer = smd.default_renderer(llmResponse);
  const parser = smd.parser(renderer);
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    result += decoder.decode(value, { stream: true });
    try {
      const json = JSON.parse(result);
      if (json.text) {
        renderMarkdown(parser, json.text);
      }
      if (json.audio) {
        audioElement.src = json.audio;
        audioElement.onended = () => {
          console.log("Audio playback finished, clearing audio source.");
          deleteAudio(audioElement.src);
          audioElement.src = "";
        };
        audioElement.onerror = () => {
          console.error("Error playing audio file:", json.audio);
        };
        audioElement.play();
      }
      result = "";
    } catch (error) {
      console.error(error);
    }
  }
}

function renderMarkdown(parser, text) {
  smd.parser_write(parser, text);
}

async function ask() {
  const question = questionInput.value;

  try {
    const response = await fetch("/llm", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });

    await processStreamedResponse(response);
  } catch (error) {
    console.error("Error asking LLM:", error);
  }
}

async function handleRecording() {
  let mediaRecorder;
  let audioChunks = [];

  const start = () => {
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();
        startRecording.disabled = true;
        startRecording.disabled = false;

        mediaRecorder.ondataavailable = (event) => {
          audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
          audioChunks = [];

          const formData = new FormData();
          formData.append("file", audioBlob, "audio.webm");

          transcription.textContent = "Transcription en cours...";

          try {
            const response = await fetch("/transcribe", {
              method: "POST",
              body: formData,
            });
            const data = await response.json();
            transcription.textContent = data.transcription;
          } catch (error) {
            console.error("Error transcribing audio:", error);
            transcription.textContent = "Erreur lors de la transcription.";
          }
        };
      })
      .catch((error) => {
        console.error("Error accessing audio stream:", error);
      });
  };

  startRecording.addEventListener("click", start);
  stopRecording.addEventListener("click", () => {
    mediaRecorder.stop();
    startRecording.disabled = false;
    stopRecording.disabled = true;
  });
}

getLocation.addEventListener("click", sendLocationToBackend);
askQuestion.addEventListener("click", ask);

muteButton.addEventListener("click", () => {
  if (audioElement.muted) {
    audioElement.muted = false;
    muteButton.innerHTML = `<i id="muteIcon" class="bi bi-volume-up"></i> Mute`;
  } else {
    audioElement.muted = true;
    muteButton.innerHTML = `<i id="muteIcon" class="bi bi-volume-mute"></i> Unmute`;
  }
});

volumeSlider.addEventListener("input", (event) => {
  audioElement.volume = event.target.value;
});

handleRecording();
