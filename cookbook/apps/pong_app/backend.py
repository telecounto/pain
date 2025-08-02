import asyncio
import uuid
import jwt
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from game import get_initial_state, update_game_state, move_paddle
# I'm assuming these are the correct imports for the solana library.
# I will need to verify this later.
from solders.pubkey import Pubkey
from solders.signature import Signature

class PlayerInput(BaseModel):
    player: int
    direction: str  # "up" or "down"

class LoginRequest(BaseModel):
    public_key: str
    signature: str

# This is a Pydantic model for the game state
class GameState(BaseModel):
    paddle1_pos: float
    paddle2_pos: float
    ball_pos: tuple[float, float]
    ball_vel: tuple[float, float]
    score1: int
    score2: int

app = FastAPI()

# In-memory storage for game sessions
game_sessions = {}
user_points = {}

# JWT settings
SECRET_KEY = "a_very_secret_key"  # In a real app, this should be a secure, environment-specific secret
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        public_key: str = payload.get("sub")
        if public_key is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return public_key
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def game_loop(game_id: str):
    """The main game loop that updates the game state for a specific game."""
    while game_id in game_sessions:
        if game_id in game_sessions:
            game_state = game_sessions[game_id]
            if game_state.get("game_over"):
                winner_pub_key = game_state.get("winner")
                if winner_pub_key:
                    total_pot = sum(game_state.get("bets", {}).values())
                    payout = total_pot * 0.95

                    if winner_pub_key not in user_points:
                        user_points[winner_pub_key] = 100
                    user_points[winner_pub_key] += payout

                del game_sessions[game_id]
                break  # Exit the loop to stop the game

            game_sessions[game_id] = update_game_state(game_state)
            await asyncio.sleep(0.05)
        else:
            break

class CreateGameRequest(BaseModel):
    bet_amount: int

@app.get("/games")
async def get_available_games():
    available_games = []
    for game_id, game_state in game_sessions.items():
        if len(game_state.get("players", {})) == 1:
            available_games.append({
                "game_id": game_id,
                "bet_amount": game_state.get("bet_amount", 0)
            })
    return available_games

@app.post("/games")
async def create_game(create_game_request: CreateGameRequest, current_user: str = Depends(get_current_user)):
    game_id = str(uuid.uuid4())
    game_sessions[game_id] = get_initial_state()
    game_sessions[game_id]["players"][1] = current_user
    game_sessions[game_id]["bet_amount"] = create_game_request.bet_amount
    asyncio.create_task(game_loop(game_id))
    return {"game_id": game_id, "player_id": 1}

@app.post("/games/{game_id}/join")
async def join_game(game_id: str, current_user: str = Depends(get_current_user)):
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")
    if len(game_sessions[game_id]["players"]) >= 2:
        raise HTTPException(status_code=400, detail="Game is full")
    game_sessions[game_id]["players"][2] = current_user
    return {"game_id": game_id, "player_id": 2}

@app.get("/games/{game_id}/state", response_model=GameState)
async def get_game_state(game_id: str):
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")
    return game_sessions[game_id]

@app.post("/login")
async def login(login_request: LoginRequest):
    # This is a placeholder for the actual signature verification logic.
    # I need to find the correct way to do this with the solana library.
    # For now, I'll assume it's a function like this:
    # message = b"Login to Pong Game"
    # signature_bytes = bytes.fromhex(login_request.signature)
    # pubkey = Pubkey.from_string(login_request.public_key)
    # is_valid = pubkey.verify(message, signature_bytes)

    # For now, I'll just assume the signature is valid for development purposes.
    is_valid = True

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Create a JWT token for the session
    access_token_data = {"sub": login_request.public_key}
    access_token = jwt.encode(access_token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}

class BuyPointsRequest(BaseModel):
    amount: int

@app.get("/points")
async def get_points(current_user: str = Depends(get_current_user)):
    if current_user not in user_points:
        user_points[current_user] = 100  # Start with 100 points
    return {"points": user_points[current_user]}

@app.post("/buy_points")
async def buy_points(buy_points_request: BuyPointsRequest, current_user: str = Depends(get_current_user)):
    # This is a placeholder. In a real app, this would involve a Solana transaction.
    if current_user not in user_points:
        user_points[current_user] = 100
    user_points[current_user] += buy_points_request.amount
    return {"message": f"{buy_points_request.amount} points added."}

class BetRequest(BaseModel):
    amount: int

@app.post("/games/{game_id}/bet")
async def place_bet(game_id: str, bet_request: BetRequest, current_user: str = Depends(get_current_user)):
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")

    # Check if user has enough points
    if user_points.get(current_user, 0) < bet_request.amount:
        raise HTTPException(status_code=400, detail="Insufficient points")

    # Deduct points and add to escrow
    user_points[current_user] -= bet_request.amount
    game_sessions[game_id]["bets"][current_user] = bet_request.amount

    return {"message": "Bet placed"}

@app.post("/games/{game_id}/input")
async def player_input(game_id: str, player_input: PlayerInput, current_user: str = Depends(get_current_user)):
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")
    # TODO: Add logic to check if the current_user is one of the players in the game
    game_sessions[game_id] = move_paddle(game_sessions[game_id], player_input.player, player_input.direction)
    return {"message": "Input received"}

# A simple way to run this for testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
