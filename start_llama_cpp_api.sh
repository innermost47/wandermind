#!/bin/bash

./llama.cpp/llama-server.exe --model ./model/llama-3.2.gguf --ctx-size 32000 --n-gpu-layers 17 --parallel 1 --cont-batching --batch-size 256 --host localhost --port 8080
