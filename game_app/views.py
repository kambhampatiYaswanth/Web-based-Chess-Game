from django.shortcuts import render, redirect
from chess_engine import piece
from chess_engine import game
from chess_engine.game import Game
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

PIECE_SYMBOLS = {
    "P": "♙", "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔",
    "p": "♟", "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚",
}


@login_required
def home(request):
    logger.debug(f"Session keys: {list(request.session.keys())}")
    logger.debug(f"Game mode: {request.session.get('game_mode')}")
    logger.debug(f"User: {request.user.username}")

    # 🎮 GAME MODE SELECTION
    if "game_mode" not in request.session:
        if request.method == "POST" and "mode" in request.POST:
            request.session["game_mode"] = request.POST["mode"]
            # Initialize new game when mode is selected
            request.session["board"] = None
            request.session["turn"] = "WHITE"
            request.session["selected"] = None
            request.session["checkmate"] = False
            request.session["winner"] = ""
            request.session["resigned"] = False
            request.session["promotion"] = None
            request.session["move_history"] = []
            request.session["ai_difficulty"] = request.POST.get("difficulty", "medium")
            request.session["ai_should_move"] = False
            return redirect("/")
        
        # Pass user to template
        return render(request, "game_app/mode_select.html", {
            "user": request.user
        })
    
    # ... rest of your home function ...
    # RESTART GAME
    if request.method == "POST" and "restart" in request.POST:
        keys_to_remove = [
            "board", "turn", "selected", "checkmate", "winner",
            "resigned", "promotion", "promotion_pos", "promotion_color",
            "move_history", "game_mode", "ai_should_move",
        ]
        for key in keys_to_remove:
            request.session.pop(key, None)
        return redirect("/")

    # RESIGN GAME
    if request.method == "POST" and "resign" in request.POST:
        current_turn = request.session.get("turn", "WHITE")
        request.session["checkmate"] = True
        request.session["winner"] = "BLACK" if current_turn == "WHITE" else "WHITE"
        request.session["resigned"] = True
        return redirect("/")

    # Initialize game
    game_obj = Game()
    
    # Restore game from session or start new
    if "board" in request.session and request.session["board"]:
        deserialize_board(request.session["board"], game_obj)
    game_obj.turn = request.session.get("turn", "WHITE")
    game_obj.move_history = request.session.get("move_history", [])

    selected = request.session.get("selected")
    checkmate = request.session.get("checkmate", False)
    winner = request.session.get("winner", "")
    legal_moves = []

    if selected:
        piece = game_obj.board.get_piece(*selected)
        if piece and piece.color == game_obj.turn:
            legal_moves = piece.get_legal_moves(game_obj.board, tuple(selected))

    # Detect king in check
    check_king_pos = None
    if game_obj.board.is_king_in_check(game_obj.turn):
        check_king_pos = game_obj.board.find_king(game_obj.turn)

    # CHECKMATE DETECTION
    if not checkmate and game_obj.board.is_king_in_check(game_obj.turn) and not game_obj.has_any_legal_move(game_obj.turn):
        request.session["checkmate"] = True
        request.session["winner"] = "WHITE" if game_obj.turn == "BLACK" else "BLACK"
        checkmate = True

    # Handle POST requests (HUMAN MOVES)
    if request.method == "POST":
        # Skip if checkmate
        if checkmate:
            request.session["board"] = serialize_board(game_obj.board)
            return redirect("/")

        # Handle pawn promotion
        promotion = request.session.get("promotion")
        if promotion and "promote_to" in request.POST:
            piece_type = request.POST["promote_to"]
            r = promotion["row"]
            c = promotion["col"]
            color = promotion["color"]

            from chess_engine.queen import Queen
            from chess_engine.rook import Rook
            from chess_engine.bishop import Bishop
            from chess_engine.knight import Knight

            piece_map = {
                "Q": Queen,
                "R": Rook,
                "B": Bishop,
                "N": Knight
            }

            game_obj.board.grid[r][c] = piece_map[piece_type](color)
            request.session["promotion"] = None
            
            # Switch turn after promotion
            game_obj.switch_turn()
            request.session["turn"] = game_obj.turn
            
            # **SET AI TO MOVE NEXT IF IT'S AI MODE AND BLACK'S TURN**
            game_mode = request.session.get("game_mode")
            if game_mode == "ai" and game_obj.turn == "BLACK":
                request.session["ai_should_move"] = True
            
            # Save board state
            request.session["board"] = serialize_board(game_obj.board)
            return redirect("/")

        # Handle board clicks
        if "square" in request.POST:
            r, c = map(int, request.POST["square"].split(","))

            # First click → select piece
            if not selected:
                piece = game_obj.board.get_piece(r, c)
                if piece and piece.color == game_obj.turn:
                    request.session["selected"] = [r, c]
                return redirect("/")

            # Second click → move
            start = tuple(selected)
            end = (r, c)

            try:
                mover = game_obj.turn
                result = game_obj.make_move(start, end)
                
                # Handle pawn promotion
                if result == "PROMOTION":
                    request.session["promotion"] = {
                        "row": end[0],
                        "col": end[1],
                        "color": game_obj.turn  # pawn color BEFORE switch
                    }
                    request.session["board"] = serialize_board(game_obj.board)
                    request.session["selected"] = None
                    return redirect("/")

                # Checkmate detection
                opponent = "BLACK" if mover == "WHITE" else "WHITE"
                if game_obj.is_checkmate(opponent):
                    request.session["checkmate"] = True
                    request.session["winner"] = mover

                request.session["selected"] = None
                
                # Save state
                request.session["board"] = serialize_board(game_obj.board)
                request.session["turn"] = game_obj.turn
                request.session["move_history"] = game_obj.move_history
                
                # **SET AI TO MOVE NEXT IF IT'S AI MODE AND BLACK'S TURN**
                game_mode = request.session.get("game_mode")
                if game_mode == "ai" and game_obj.turn == "BLACK":
                    request.session["ai_should_move"] = True

            except Exception as e:
                request.session["error"] = str(e)
                request.session["selected"] = None
                return redirect("/")
    
    # **FIXED AI MOVE HANDLING**
    game_mode = request.session.get("game_mode")
    
    # AI should move if:
    # 1. It's AI mode
    # 2. Black's turn (AI plays as black)
    # 3. Not in checkmate
    # 4. Not in promotion
    # 5. We've flagged that AI should move
    if (game_mode == "ai" and 
        game_obj.turn == "BLACK" and 
        not checkmate and 
        not request.session.get("promotion") and
        request.session.get("ai_should_move", False)):
        
        logger.debug(f"Triggering AI move. Turn: {game_obj.turn}")
        
        try:
            # Make AI move
            ai_moved = game_obj.make_ai_move()
            
            if ai_moved:
                logger.debug("AI moved successfully")
                
                # **CLEAR THE FLAG** so AI doesn't move again
                request.session["ai_should_move"] = False
                
                # Update session after AI move
                request.session["board"] = serialize_board(game_obj.board)
                request.session["turn"] = game_obj.turn  # Should now be WHITE
                request.session["move_history"] = game_obj.move_history
                
                # Check if AI move caused checkmate
                if game_obj.is_checkmate("WHITE"):
                    request.session["checkmate"] = True
                    request.session["winner"] = "BLACK"
                
                # Save and redirect to refresh
                request.session.modified = True
                return redirect("/")
            else:
                logger.debug("AI failed to move")
                # Still clear the flag to avoid infinite loop
                request.session["ai_should_move"] = False
                
        except Exception as e:
            logger.error(f"AI move error: {e}")
            import traceback
            traceback.print_exc()
            # Clear the flag on error too
            request.session["ai_should_move"] = False
    
    # 🧱 Build board for template
    board = []
    for r in range(8):
        row = []
        for c in range(8):
            piece = game_obj.board.get_piece(r, c)
            square_color = "white" if (r + c) % 2 == 0 else "black"
            symbol = PIECE_SYMBOLS[piece.symbol()] if piece else ""
            is_king_in_check = (check_king_pos == (r, c))

            row.append({
                "row": r,
                "col": c,
                "color": square_color,
                "piece": symbol,
                "selected": selected == [r, c],
                "is_legal": (r, c) in legal_moves,
                "king_in_check": is_king_in_check,
            })
        board.append(row)

    # Save state (important for persistence)
    request.session["board"] = serialize_board(game_obj.board)
    request.session["turn"] = game_obj.turn
    request.session["move_history"] = game_obj.move_history

    error = request.session.pop("error", None)
    promotion = request.session.get("promotion")

    return render(request, "game_app/board.html", {
        "board": board,
        "turn": game_obj.turn,
        "error": error,
        "checkmate": checkmate,
        "winner": winner,
        "resigned": request.session.get("resigned", False),
        "move_history": game_obj.move_history,
        "check_king_pos": check_king_pos,
        "promotion": promotion,
        "game_mode": game_mode,
    })


def serialize_board(board):
    data = []
    for r in range(8):
        row = []
        for c in range(8):
            piece = board.get_piece(r, c)
            row.append(piece.symbol() if piece else "")
        data.append(row)
    return data


def deserialize_board(board_data, game):
    from chess_engine.pawn import Pawn
    from chess_engine.rook import Rook
    from chess_engine.knight import Knight
    from chess_engine.bishop import Bishop
    from chess_engine.queen import Queen
    from chess_engine.king import King

    piece_map = {
        "P": Pawn,   "p": Pawn,
        "R": Rook,   "r": Rook,
        "N": Knight, "n": Knight,
        "B": Bishop, "b": Bishop,
        "Q": Queen,  "q": Queen,
        "K": King,   "k": King,
    }

    game.board.grid = [[None for _ in range(8)] for _ in range(8)]

    for r in range(8):
        for c in range(8):
            symbol = board_data[r][c]
            if symbol:
                color = "WHITE" if symbol.isupper() else "BLACK"
                game.board.grid[r][c] = piece_map[symbol](color)

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("/")  # → mode selection
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "game_app/login.html")
# In views.py - Add this function with your other auth functions

def logout_view(request):
    """Handle user logout with debugging"""
    print(f"\n{'='*50}")
    print("LOGOUT VIEW CALLED")
    print(f"User: {request.user}")
    print(f"Session keys before: {list(request.session.keys())}")
    print(f"{'='*50}\n")
    
    # Clear all game session data
    game_keys = [
        'board', 'turn', 'selected', 'checkmate', 'winner',
        'resigned', 'promotion', 'move_history', 'game_mode',
        'ai_difficulty', 'ai_should_move'
    ]
    
    for key in game_keys:
        if key in request.session:
            print(f"Removing session key: {key}")
            del request.session[key]
    
    # Logout the user
    from django.contrib.auth import logout as auth_logout
    auth_logout(request)
    
    # Add success message
    from django.contrib import messages
    messages.success(request, "You have been successfully logged out.")
    
    print(f"\n{'='*50}")
    print("LOGOUT COMPLETE")
    print(f"User after logout: {request.user}")
    print(f"Session keys after: {list(request.session.keys())}")
    print(f"{'='*50}\n")
    
    return redirect('login')

def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirm = request.POST["confirm"]

        if password != confirm:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, "Account created successfully")
            return redirect("/login")

    return render(request, "game_app/register.html")
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()      # 🔥 THIS creates the user in DB
            login(request, user)    # auto-login after register
            return redirect("/")    # go to mode selection / game
        else:
            print(form.errors)      # 🔴 IMPORTANT: shows WHY it failed

    else:
        form = UserCreationForm()

    return render(request, "game_app/register.html", {"form": form})