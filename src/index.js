import * as smd from "streaming-markdown";

const muteButton = document.getElementById("muteButton");
const volumeSlider = document.getElementById("volumeSlider");
const transcription = document.getElementById("transcription");
const startRecording = document.getElementById("startRecording");
const stopRecording = document.getElementById("stopRecording");
const getLocation = document.getElementById("getLocation");
const getRestaurants = document.getElementById("getRestaurants");
const getAccomodations = document.getElementById("getAccomodations");
const getEvents = document.getElementById("getEvents");
const getCulturals = document.getElementById("getCulturals");
const askQuestion = document.getElementById("askQuestion");
const questionInput = document.getElementById("questionInput");
const llmResponse = document.getElementById("llmResponse");

let autoScrollEnabled = true;
let audioQueue = [];
let isPlaying = false;
let audioElement = new Audio();
audioElement.muted = true;

function checkScrollPosition() {
  const nearBottom =
    window.innerHeight + window.scrollY >= document.body.offsetHeight - 100;
  if (nearBottom) {
    autoScrollEnabled = true;
  } else {
    autoScrollEnabled = false;
  }
}

function scrollToBottom() {
  if (autoScrollEnabled) {
    window.scrollTo({
      top: document.body.scrollHeight,
      behavior: "smooth",
    });
  }
}

function getCurrentPosition() {
  return new Promise((resolve, reject) => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      });
    } else {
      reject(new Error("Geolocation is not supported by this browser."));
    }
  });
}

async function fetchLocationData(url) {
  try {
    llmResponse.classList.add("d-none");
    questionInput.value = "";

    const position = await getCurrentPosition();
    const { latitude, longitude } = position.coords;

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ latitude, longitude }),
    });

    if (parseInt(response.status) === 200) {
      await processStreamedResponse(response);
    }
  } catch (error) {
    console.error("Error getting location or fetching LLM data:", error);
  }
}

function deleteAudio(audioPath) {
  fetch("./delete_audio", {
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

async function playNextAudio() {
  if (audioQueue.length === 0) {
    isPlaying = false;
    return;
  }
  isPlaying = true;
  const nextAudio = audioQueue.shift();
  audioElement.src = nextAudio;
  try {
    await playAudio(audioElement);
    deleteAudio(audioElement.src);
    playNextAudio();
  } catch (error) {
    console.error("Error playing audio:", error);
    playNextAudio();
  }
}

function playAudio(audioElement) {
  return new Promise((resolve, reject) => {
    audioElement.play();
    audioElement.onended = resolve;
    audioElement.onerror = reject;
  });
}

async function processStreamedResponse(response) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let result = "";
  llmResponse.classList.remove("d-none");
  llmResponse.textContent = "";
  const renderer = smd.default_renderer(llmResponse);
  const parser = smd.parser(renderer);

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    result += decoder.decode(value, { stream: true });
    let parts = result.split("<|end_of_chunk|>");
    for (let i = 0; i < parts.length - 1; i++) {
      let jsonString = parts[i].trim();
      if (jsonString === "") continue;
      try {
        let json = JSON.parse(jsonString);
        if (json.text) {
          renderMarkdown(parser, json.text);
        }
        if (json.audio) {
          audioQueue.push(json.audio);
          if (!isPlaying) {
            playNextAudio();
          }
        }
      } catch (error) {
        console.error("Erreur lors du parsing JSON :", error);
      }
    }
    result = parts[parts.length - 1];
  }
}

function renderMarkdown(parser, text) {
  smd.parser_write(parser, text);
  scrollToBottom();
}

async function ask() {
  const question = questionInput.value;
  questionInput.value = "";
  llmResponse.classList.add("d-none");
  try {
    const response = await fetch("./llm", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });
    if (parseInt(response.status) === 200) {
      await processStreamedResponse(response);
    }
  } catch (error) {
    console.error("Error asking LLM:", error);
  }
}

async function handleRecording() {
  let mediaRecorder;
  let audioChunks = [];

  const start = () => {
    transcription.textContent = "";
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();
        mediaRecorder.ondataavailable = (event) => {
          audioChunks.push(event.data);
        };
        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
          audioChunks = [];
          const formData = new FormData();
          formData.append("file", audioBlob, "audio.webm");
          transcription.classList.remove("d-none");
          transcription.classList.remove("alert-danger");
          transcription.classList.remove("alert-success");
          transcription.classList.add("alert-info");
          transcription.textContent = "Transcription en cours...";
          try {
            const response = await fetch("./transcribe", {
              method: "POST",
              body: formData,
            });
            if (response.status >= 300) {
              transcription.classList.remove("alert-info");
              transcription.classList.add("alert-danger");
              transcription.textContent = "Erreur lors de la transcription.";
            } else {
              const data = await response.json();
              transcription.classList.remove("alert-info");
              transcription.classList.add("alert-success");
              transcription.textContent = "Transcription réalisée avec succès.";
              questionInput.value = data.transcription;
            }
          } catch (error) {
            console.error("Error transcribing audio:", error);
            transcription.textContent = "Erreur lors de la transcription.";
          } finally {
            setTimeout(() => {
              transcription.classList.add("d-none");
            }, 3000);
          }
        };
      })
      .catch((error) => {
        console.error("Error accessing audio stream:", error);
      });
  };

  startRecording.addEventListener("click", () => {
    startRecording.disabled = true;
    stopRecording.disabled = false;
    start();
  });
  stopRecording.addEventListener("click", () => {
    mediaRecorder.stop();
    startRecording.disabled = false;
    stopRecording.disabled = true;
  });
}

function attachEventListener(buttonElement, handlerFunction) {
  if (buttonElement) {
    buttonElement.addEventListener("click", handlerFunction);
  }
}

attachEventListener(getLocation, () => fetchLocationData("./wikipedia"));
attachEventListener(getRestaurants, () => fetchLocationData("./restaurant"));
attachEventListener(getAccomodations, () =>
  fetchLocationData("./accommodations")
);
attachEventListener(getCulturals, () => {
  fetchLocationData("./culturals");
});
attachEventListener(getEvents, () => {
  fetchLocationData("./events");
});
attachEventListener(askQuestion, () => {
  ask();
});

if (muteButton) {
  muteButton.addEventListener("click", () => {
    if (audioElement.muted) {
      audioElement.muted = false;
      muteButton.innerHTML = `<i id="muteIcon" class="bi bi-volume-up"></i> Désactiver le son`;
    } else {
      audioElement.muted = true;
      muteButton.innerHTML = `<i id="muteIcon" class="bi bi-volume-mute"></i> Activer le son`;
    }
  });
}

if (volumeSlider) {
  volumeSlider.addEventListener("input", (event) => {
    audioElement.volume = event.target.value;
  });
}

if (startRecording && stopRecording) {
  handleRecording();
}

window.addEventListener("scroll", checkScrollPosition);
