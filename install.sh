#!/bin/bash

DIRECTORY="env"

if [ ! -d "$DIRECTORY" ]; then
  python -m venv "$DIRECTORY"
fi

source env/Scripts/activate

export CMAKE_ARGS=-DGGML_CUBLAS=on
export FORCE_CMAKE=1

pip install llama-cpp-python --force-reinstall --upgrade --no-cache-dir
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt --no-cache-dir
