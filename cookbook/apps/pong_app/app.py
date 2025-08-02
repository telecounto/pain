import streamlit as st
import time
import requests
from utils import (
    GAME_WIDTH,
    GAME_HEIGHT,
    PADDLE_WIDTH,
    PADDLE_HEIGHT,
    BALL_SIZE,
)

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

def main():
    st.title("Pong Game")

    # Matchmaking UI
    if "game_id" not in st.session_state:
        st.header("Matchmaking")
        if st.button("Create New Game"):
            response = requests.post(f"{BACKEND_URL}/games")
            data = response.json()
            st.session_state.game_id = data["game_id"]
            st.session_state.player_id = data["player_id"]
            st.rerun()

        join_game_id = st.text_input("Enter Game ID to Join")
        if st.button("Join Game"):
            if join_game_id:
                response = requests.post(f"{BACKEND_URL}/games/{join_game_id}/join")
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.game_id = data["game_id"]
                    st.session_state.player_id = data["player_id"]
                    st.rerun()
                else:
                    st.error("Game not found or unable to join.")
            else:
                st.error("Please enter a Game ID.")
        return

    # In a game
    game_id = st.session_state.game_id
    player_id = st.session_state.player_id
    st.write(f"Game ID: {game_id} | You are Player {player_id}")

    # Get game state from backend
    try:
        response = requests.get(f"{BACKEND_URL}/games/{game_id}/state")
        if response.status_code != 200:
            st.error("Could not get game state.")
            return
        game_state = response.json()
    except requests.exceptions.ConnectionError:
        st.error("Connection to backend failed. Make sure the backend is running.")
        return

    # CSS for game elements
    game_css = f"""
        <style>
            .game-board {{
                width: {GAME_WIDTH}px;
                height: {GAME_HEIGHT}px;
                background-color: #000;
                border: 2px solid #fff;
                position: relative;
            }}
            .paddle {{
                width: {PADDLE_WIDTH}px;
                height: {PADDLE_HEIGHT}px;
                background-color: #fff;
                position: absolute;
            }}
            #paddle1 {{
                left: 0;
                top: {game_state["paddle1_pos"]}px;
            }}
            #paddle2 {{
                right: 0;
                top: {game_state["paddle2_pos"]}px;
            }}
            .ball {{
                width: {BALL_SIZE}px;
                height: {BALL_SIZE}px;
                background-color: #fff;
                position: absolute;
                left: {game_state["ball_pos"][0]}px;
                top: {game_state["ball_pos"][1]}px;
            }}
        </style>
    """

    # HTML for game board
    game_html = """
        <div class="game-board">
            <div id="paddle1" class="paddle"></div>
            <div id="paddle2" class="paddle"></div>
            <div class="ball"></div>
        </div>
    """

    # Render game
    st.markdown(game_css, unsafe_allow_html=True)
    st.markdown(game_html, unsafe_allow_html=True)

    # Display score
    st.write(f"Player 1: {game_state['score1']} | Player 2: {game_state['score2']}")

    # Game controls
    with st.sidebar:
        st.header("Controls")
        if st.button("Up"):
            requests.post(f"{BACKEND_URL}/games/{game_id}/input", json={"player": player_id, "direction": "up"})
        if st.button("Down"):
            requests.post(f"{BACKEND_URL}/games/{game_id}/input", json={"player": player_id, "direction": "down"})

    # Frontend refresh loop
    time.sleep(0.05)
    st.rerun()

if __name__ == "__main__":
    main()
