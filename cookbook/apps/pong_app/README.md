# Pong Game

This is a multiplayer Pong game built with `streamlit`, `fastapi`, and `agno`.

## Features

*   1v1 Matchmaking
*   Bet points on games (Coming soon!)
*   Game Lobby (Coming soon!)
*   Practice with an AI (Coming soon!)

This project is currently under construction.

## Installation and Setup

To run the Pong game, you need to have Python 3 installed.

### 1. Set up a virtual environment

It's recommended to use a virtual environment to manage the project's dependencies.

```shell
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

Install the required Python packages using pip:

```shell
pip install streamlit fastapi "uvicorn[standard]" requests
```

### 3. Run the backend server

The backend is a FastAPI application that manages the game state. Run the following command in your terminal:

```shell
python cookbook/apps/pong_app/backend.py
```

The backend server will start on `http://127.0.0.1:8000`.

### 4. Run the frontend application

The frontend is a Streamlit application. Open a new terminal window (and activate the virtual environment) and run the following command:

```shell
streamlit run cookbook/apps/pong_app/app.py
```

The frontend will be available at `http://localhost:8501`. You can now open this URL in your web browser to play the game.
