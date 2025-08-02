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

    # Login UI
    if "jwt" not in st.session_state:
        st.header("Login")
        public_key = st.text_input("Enter your Solana Public Key to Login (for testing)")
        if st.button("Login"):
            if public_key:
                # This is a dummy signature for now. In a real app, this would be a real signature from the user's wallet.
                dummy_signature = "dummy_signature"
                response = requests.post(f"{BACKEND_URL}/login", json={"public_key": public_key, "signature": dummy_signature})
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.jwt = data["access_token"]
                    st.rerun()
                else:
                    st.error("Login failed.")
            else:
                st.error("Please enter a public key.")
        return

    # Logged in user info
    headers = {"Authorization": f"Bearer {st.session_state.jwt}"}
    try:
        response = requests.get(f"{BACKEND_URL}/points", headers=headers)
        if response.status_code == 200:
            points = response.json()["points"]
            st.write(f"Your points: {points}")
        else:
            st.error("Could not get points balance.")
    except requests.exceptions.ConnectionError:
        st.error("Connection to backend failed.")
        return

    with st.sidebar:
        st.header("Buy Points")
        amount_to_buy = st.number_input("Amount", min_value=1, step=1)
        if st.button("Buy"):
            response = requests.post(f"{BACKEND_URL}/buy_points", json={"amount": amount_to_buy}, headers=headers)
            if response.status_code == 200:
                st.success("Points purchased successfully!")
                st.rerun()
            else:
                st.error("Purchase failed.")

    # Matchmaking UI
    if "game_id" not in st.session_state:
        st.header("Game Lobby")
        headers = {"Authorization": f"Bearer {st.session_state.jwt}"}

        try:
            response = requests.get(f"{BACKEND_URL}/games")
            if response.status_code == 200:
                available_games = response.json()
                if not available_games:
                    st.write("No available games. Create a new one!")
                else:
                    st.write("Available Games:")
                    for game in available_games:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.text(f"ID: {game['game_id']}")
                        with col2:
                            st.text(f"Bet: {game['bet_amount']}")
                        with col3:
                            if st.button("Join", key=f"join_{game['game_id']}"):
                                join_response = requests.post(f"{BACKEND_URL}/games/{game['game_id']}/join", headers=headers)
                                if join_response.status_code == 200:
                                    data = join_response.json()
                                    st.session_state.game_id = data["game_id"]
                                    st.session_state.player_id = data["player_id"]
                                    st.rerun()
                                else:
                                    st.error("Could not join game.")
            else:
                st.error("Could not fetch available games.")
        except requests.exceptions.ConnectionError:
            st.error("Connection to backend failed.")

        st.header("Create New Game")
        bet_amount = st.number_input("Set Bet Amount", min_value=1, step=1)
        if st.button("Create Game"):
            create_response = requests.post(f"{BACKEND_URL}/games", json={"bet_amount": bet_amount}, headers=headers)
            if create_response.status_code == 200:
                data = create_response.json()
                st.session_state.game_id = data["game_id"]
                st.session_state.player_id = data["player_id"]
                st.rerun()
            else:
                st.error("Could not create game.")
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

    # Game controls & Betting
    with st.sidebar:
        if not game_state.get("game_over"):
            st.header("Controls")
            headers = {"Authorization": f"Bearer {st.session_state.jwt}"}
            if st.button("Up"):
                requests.post(f"{BACKEND_URL}/games/{game_id}/input", json={"player": player_id, "direction": "up"}, headers=headers)
            if st.button("Down"):
                requests.post(f"{BACKEND_URL}/games/{game_id}/input", json={"player": player_id, "direction": "down"}, headers=headers)

            st.header("Betting")
            bet_amount = st.number_input("Bet Amount", min_value=1, step=1)
            if st.button("Place Bet"):
                response = requests.post(f"{BACKEND_URL}/games/{game_id}/bet", json={"amount": bet_amount}, headers=headers)
                if response.status_code == 200:
                    st.success("Bet placed successfully!")
                    st.rerun()
                else:
                    st.error(f"Bet failed: {response.text}")

    # Display game over
    if game_state.get("game_over"):
        winner = game_state.get("winner")
        if winner:
            st.success(f"Game Over! Winner is Player {winner}")
        else:
            st.info("Game Over!")

    # Frontend refresh loop
    time.sleep(0.05)
    st.rerun()

if __name__ == "__main__":
    main()
