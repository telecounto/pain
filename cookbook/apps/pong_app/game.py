# Game constants
GAME_WIDTH = 800
GAME_HEIGHT = 600
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100
BALL_SIZE = 20
PADDLE_SPEED = 20
BALL_SPEED_X = 10
BALL_SPEED_Y = 10

# Initial positions
INITIAL_PADDLE_1_POS = (GAME_HEIGHT - PADDLE_HEIGHT) / 2
INITIAL_PADDLE_2_POS = (GAME_HEIGHT - PADDLE_HEIGHT) / 2
INITIAL_BALL_POS = ((GAME_WIDTH - BALL_SIZE) / 2, (GAME_HEIGHT - BALL_SIZE) / 2)
INITIAL_BALL_VEL = (BALL_SPEED_X, BALL_SPEED_Y)

def get_initial_state():
    return {
        "paddle1_pos": INITIAL_PADDLE_1_POS,
        "paddle2_pos": INITIAL_PADDLE_2_POS,
        "ball_pos": INITIAL_BALL_POS,
        "ball_vel": INITIAL_BALL_VEL,
        "score1": 0,
        "score2": 0,
    }

def update_game_state(game_state):
    ball_x, ball_y = game_state["ball_pos"]
    vx, vy = game_state["ball_vel"]
    paddle1_pos = game_state["paddle1_pos"]
    paddle2_pos = game_state["paddle2_pos"]
    score1 = game_state["score1"]
    score2 = game_state["score2"]

    # Move the ball
    ball_x += vx
    ball_y += vy

    # Wall collision (top/bottom)
    if ball_y <= 0 or ball_y >= GAME_HEIGHT - BALL_SIZE:
        vy = -vy

    # Paddle collision
    if (
        ball_x <= PADDLE_WIDTH
        and paddle1_pos <= ball_y <= paddle1_pos + PADDLE_HEIGHT
    ):
        vx = -vx
    if (
        ball_x >= GAME_WIDTH - PADDLE_WIDTH - BALL_SIZE
        and paddle2_pos <= ball_y <= paddle2_pos + PADDLE_HEIGHT
    ):
        vx = -vx

    # Wall collision (left/right) - scoring
    if ball_x <= 0:
        score2 += 1
        ball_x, ball_y = INITIAL_BALL_POS
        # vx, vy will be reset in the next lines
    if ball_x >= GAME_WIDTH - BALL_SIZE:
        score1 += 1
        ball_x, ball_y = INITIAL_BALL_POS
        # vx, vy will be reset in the next lines

    game_state["ball_pos"] = (ball_x, ball_y)
    game_state["ball_vel"] = (vx, vy)
    game_state["score1"] = score1
    game_state["score2"] = score2

    return game_state

def move_paddle(game_state, player, direction):
    if player == 1:
        paddle_pos = game_state["paddle1_pos"]
    else:
        paddle_pos = game_state["paddle2_pos"]

    if direction == "up":
        paddle_pos -= PADDLE_SPEED
    elif direction == "down":
        paddle_pos += PADDLE_SPEED

    # Constrain the paddle to the game board
    if paddle_pos < 0:
        paddle_pos = 0
    if paddle_pos > GAME_HEIGHT - PADDLE_HEIGHT:
        paddle_pos = GAME_HEIGHT - PADDLE_HEIGHT

    if player == 1:
        game_state["paddle1_pos"] = paddle_pos
    else:
        game_state["paddle2_pos"] = paddle_pos

    return game_state
