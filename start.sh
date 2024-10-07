#!/bin/bash

export $(grep -v '^#' .env | xargs)

if [ "$FLASK_ENV" == "development" ]; then
    echo "Starting the application in development mode..."
    flask run --host=127.0.0.1 --port=5000
else
    echo "Starting the application in production mode..."
    waitress-serve --listen=127.0.0.1:5000 app:app
fi

