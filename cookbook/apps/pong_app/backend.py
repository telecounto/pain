import asyncio
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from game import get_initial_state, update_game_state, move_paddle

class PlayerInput(BaseModel):
    player: int
    direction: str  # "up" or "down"

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

async def game_loop(game_id: str):
    """The main game loop that updates the game state for a specific game."""
    while game_id in game_sessions:
        if game_id in game_sessions:
            game_sessions[game_id] = update_game_state(game_sessions[game_id])
            await asyncio.sleep(0.05)
        else:
            break

@app.post("/games")
async def create_game():
    game_id = str(uuid.uuid4())
    game_sessions[game_id] = get_initial_state()
    asyncio.create_task(game_loop(game_id))
    return {"game_id": game_id, "player_id": 1}

@app.post("/games/{game_id}/join")
async def join_game(game_id: str):
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")
    # In a real app, we would handle multiple players joining, but for now this is simple
    return {"game_id": game_id, "player_id": 2}

@app.get("/games/{game_id}/state", response_model=GameState)
async def get_game_state(game_id: str):
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")
    return game_sessions[game_id]

@app.post("/games/{game_id}/input")
async def player_input(game_id: str, player_input: PlayerInput):
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")
    game_sessions[game_id] = move_paddle(game_sessions[game_id], player_input.player, player_input.direction)
    return {"message": "Input received"}

# A simple way to run this for testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
