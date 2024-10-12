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
const stopGeneration = document.getElementById("stopGeneration");
const loadingSpinner = document.getElementById("loadingSpinner");

let controller = new AbortController();
let autoScrollEnabled = true;
let audioQueue = [];
let isPlaying = false;
let buttonStates = [];
let audioElement = new Audio();

audioElement.muted = true;

function saveButtonStates() {
  const buttons = document.querySelectorAll("button");
  buttonStates = [];
  buttons.forEach((button) => {
    buttonStates.push({
      element: button,
      isDisabled: button.disabled,
    });
  });
}

function restoreButtonStates() {
  buttonStates.forEach((state) => {
    state.element.disabled = state.isDisabled;
  });
}

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
    saveButtonStates();
    setButtonsDisabled(true);
    loadingSpinner.classList.remove("d-none");
    llmResponse.classList.add("d-none");
    loadingSpinner.classList.add("text-primary");
    loadingSpinner.classList.remove("text-danger");
    questionInput.value = "";
    const position = await getCurrentPosition();
    const { latitude, longitude } = position.coords;
    controller = new AbortController();
    const signal = controller.signal;
    const response = await fetch(url, {
      signal: signal,
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
  } finally {
    loadingSpinner.classList.add("d-none");
    restoreButtonStates();
    stopGeneration.classList.add("d-none");
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

function setButtonsDisabled(disabled) {
  const buttons = document.querySelectorAll("button");
  buttons.forEach((button) => {
    if (button !== muteButton && button != stopGeneration) {
      button.disabled = disabled;
    }
  });
}

async function processStreamedResponse(response) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let result = "";
  stopGeneration.classList.remove("d-none");
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
  saveButtonStates();
  setButtonsDisabled(true);
  loadingSpinner.classList.remove("d-none");
  loadingSpinner.classList.add("text-primary");
  loadingSpinner.classList.remove("text-danger");
  controller = new AbortController();
  const signal = controller.signal;
  try {
    const response = await fetch("./llm", {
      signal: signal,
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
  } finally {
    loadingSpinner.classList.add("d-none");
    stopGeneration.classList.add("d-none");
    restoreButtonStates();
  }
}

async function handleRecording() {
  let mediaRecorder;
  let audioChunks = [];
  let stream;

  const start = () => {
    transcription.textContent = "";
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((audioStream) => {
        stream = audioStream;
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
          stream.getTracks().forEach((track) => track.stop());
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

function adjustInput(questionInput) {
  questionInput.style.height = "auto";
  const maxHeight = 180;
  const borderTopWidth = parseFloat(
    window.getComputedStyle(questionInput).getPropertyValue("border-top-width")
  );
  const borderBottomWidth = parseFloat(
    window
      .getComputedStyle(questionInput)
      .getPropertyValue("border-bottom-width")
  );
  const totalHeight =
    questionInput.scrollHeight + borderTopWidth + borderBottomWidth;
  if (totalHeight > maxHeight) {
    questionInput.style.height = maxHeight + "px";
    questionInput.style.overflowY = "scroll";
  } else {
    questionInput.style.height = totalHeight + "px";
    questionInput.style.overflowY = "hidden";
  }
}

function attachEventListener(buttonElement, eventType, handlerFunction) {
  if (buttonElement) {
    buttonElement.addEventListener(eventType, handlerFunction);
  }
}

attachEventListener(getLocation, "click", () =>
  fetchLocationData("./wikipedia")
);
attachEventListener(getRestaurants, "click", () =>
  fetchLocationData("./restaurant")
);
attachEventListener(getAccomodations, "click", () =>
  fetchLocationData("./accommodations")
);
attachEventListener(getCulturals, "click", () => {
  fetchLocationData("./culturals");
});
attachEventListener(getEvents, "click", () => {
  fetchLocationData("./events");
});
attachEventListener(askQuestion, "click", () => {
  ask();
});
attachEventListener(questionInput, "input", () => {
  adjustInput(questionInput);
});
attachEventListener(stopGeneration, "click", () => {
  controller.abort();
  audioElement.pause();
  audioElement.currentTime = 0;
  loadingSpinner.classList.remove("text-primary");
  loadingSpinner.classList.add("text-danger");
});

attachEventListener(muteButton, "click", () => {
  if (audioElement.muted) {
    audioElement.muted = false;
    muteButton.innerHTML = `<i id="muteIcon" class="bi bi-volume-up-fill text-success fs-2"></i>`;
  } else {
    audioElement.muted = true;
    muteButton.innerHTML = `<i id="muteIcon" class="bi bi-volume-mute-fill text-danger fs-2"></i>`;
  }
});

attachEventListener(volumeSlider, "input", (event) => {
  audioElement.volume = event.target.value;
});

if (startRecording && stopRecording) {
  handleRecording();
}

window.addEventListener("scroll", checkScrollPosition);
