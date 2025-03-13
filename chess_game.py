import pygame
import chess
import chess.engine
import time

pygame.init()

WIDTH, HEIGHT = 600, 600
SQUARE_SIZE = WIDTH // 8
HIGHLIGHT_COLOR = (173, 216, 230)
LEGAL_MOVE_COLOR = (255, 228, 181)  

background = pygame.image.load('images/wood.jpg')  
background = pygame.transform.scale(background, (WIDTH, HEIGHT))  

board = chess.Board()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

piece_name_map = {
    'r': 'Black_Rook',
    'n': 'Black_Knight',
    'b': 'Black_Bishop',
    'q': 'Black_Queen',
    'k': 'Black_King',
    'p': 'Black_Pawn',
    'R': 'White_Rook',
    'N': 'White_Knight',
    'B': 'White_Bishop',
    'Q': 'White_Queen',
    'K': 'White_King',
    'P': 'White_Pawn'
}

pieces = {
    name: pygame.transform.scale(pygame.image.load(f'images/{name}.png'), (SQUARE_SIZE, SQUARE_SIZE))
    for name in piece_name_map.values()
}

selected_piece = None

# AI settings
ai_mode = None  
engine_path = r"C:\Users\Djaunathan Albert\Desktop\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"
engine = chess.engine.SimpleEngine.popen_uci(engine_path)

difficulty_levels = {
    "Easy": {"Level 1": 1, "Level 2": 2, "Level 3": 3},
    "Medium": {"Level 1": 4, "Level 2": 6, "Level 3": 8},
    "Hard": {"Level 1": 10, "Level 2": 12, "Level 3": 15}
}

engine = chess.engine.SimpleEngine.popen_uci(engine_path)
engine.configure({"Skill Level": 1}) 

def draw_welcome():
    background = pygame.image.load('images/welcome_background.jpg')  
    background = pygame.transform.scale(background, (WIDTH, HEIGHT)) 
    screen.blit(background, (0, 0))  

    font = pygame.font.SysFont('Arial', 60, bold=True)
    title = font.render('Welcome to Chess', True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    button_font = pygame.font.SysFont('Arial', 40, bold=True)
    play_button = pygame.Rect(WIDTH // 2 - 100, 350, 200, 70)
    pygame.draw.rect(screen, (0, 180, 0), play_button, border_radius=15)
    pygame.draw.rect(screen, (255, 255, 255), play_button, 3, border_radius=15)
    play_text = button_font.render('Play', True, (0, 0, 0))
    screen.blit(play_text, (WIDTH // 2 - play_text.get_width() // 2, 365))

    pygame.display.flip()
    return play_button

def draw_menu(hovered_button=None):
    screen.fill((30, 30, 30))  
    font = pygame.font.SysFont('Arial', 50, bold=True)
    title = font.render('Choose Difficulty', True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

    button_font = pygame.font.SysFont('Arial', 30, bold=True)
    buttons = {
        "Back": pygame.Rect(15, 15, 100, 40),  
        "Easy": pygame.Rect(WIDTH // 2 - 100, 200, 200, 60),
        "Medium": pygame.Rect(WIDTH // 2 - 100, 280, 200, 60),
        "Hard": pygame.Rect(WIDTH // 2 - 100, 360, 200, 60),
        "Player vs Player": pygame.Rect(WIDTH // 2 - 100, 440, 200, 60)
    }

    base_colors = {
        "Back": (180, 180, 180),
        "Easy": (0, 180, 0),
        "Medium": (200, 180, 0),
        "Hard": (180, 0, 0),
        "Player vs Player": (100, 149, 237)
    }
    hover_colors = {
        "Back": (200, 200, 200),
        "Easy": (0, 255, 0),
        "Medium": (255, 220, 0),
        "Hard": (255, 50, 50),
        "Player vs Player": (135, 206, 250)
    }

    for text, rect in buttons.items():
        color = hover_colors[text] if hovered_button == text else base_colors[text]
        pygame.draw.rect(screen, color, rect, border_radius=15)  
        pygame.draw.rect(screen, (255, 255, 255), rect, 3, border_radius=15)  
        text_surface = button_font.render(text, True, (0, 0, 0))
        if text == "Back":  
            screen.blit(text_surface, (rect.x + (rect.width - text_surface.get_width()) // 2,  
                                        rect.y + (rect.height - text_surface.get_height()) // 2))
        else:
            screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, rect.y + 15))

    pygame.display.flip()
    return buttons

def handle_menu_click(mouse_pos, buttons):
    global ai_mode
    for mode, rect in buttons.items():
        if rect.collidepoint(mouse_pos):
            ai_mode = mode
            return True
    return False

def show_result(message):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont('Arial', 50, bold=True)
    text = font.render(message, True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 25))
    pygame.display.flip()
    pygame.time.delay(3000)  

def is_about_to_checkmate(board, move):
    temp_board = board.copy()
    temp_board.push(move)
    return temp_board.is_checkmate()    

def reset_game():
    global board, selected_piece, in_menu, ai_mode
    board = chess.Board()
    selected_piece = None
    in_menu = True
    ai_mode = None    

def get_ai_move():
    depth = {"Easy": 1, "Medium": 3, "Hard": 5}.get(ai_mode, 3)
    skill = 0 if ai_mode == "Easy" else 20
    
    engine.configure({"Skill Level": skill})
    result = engine.play(board, chess.engine.Limit(depth=depth))
    
    return result.move

def draw_board():
    screen.blit(background, (0, 0))  
    if selected_piece is not None:
        col, row = chess.square_file(selected_piece), chess.square_rank(selected_piece)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, (col * SQUARE_SIZE, (7 - row) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 5)

def draw_pieces():
    for row in range(8):
        for col in range(8):
            piece = board.piece_at(chess.square(col, 7 - row))
            if piece:
                piece_name = piece_name_map.get(piece.symbol())
                if piece_name:
                    screen.blit(pieces[piece_name], (col * SQUARE_SIZE, row * SQUARE_SIZE))                 

def draw_legal_moves():
    if selected_piece is not None:
        legal_moves = [move.to_square for move in board.legal_moves if move.from_square == selected_piece]
        for move in legal_moves:
            col, row = chess.square_file(move), chess.square_rank(move)
            pygame.draw.rect(screen, LEGAL_MOVE_COLOR, (col * SQUARE_SIZE, (7 - row) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

def get_square_from_mouse(pos):
    col, row = pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE
    return chess.square(col, 7 - row)

running = True
in_welcome = True
in_menu = True
buttons = draw_menu()
board = chess.Board()
selected_piece = None
ai_mode = None

while running:
    screen.fill((0, 0, 0))

    if in_welcome:
        play_button = draw_welcome()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(pygame.mouse.get_pos()):
                    in_welcome = False
                    in_menu = True
    
    elif in_menu:
        mouse_pos = pygame.mouse.get_pos()
        hovered_button = next((text for text, rect in buttons.items() if rect.collidepoint(mouse_pos)), None)
        buttons = draw_menu(hovered_button)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for mode, rect in buttons.items():
                    if rect.collidepoint(mouse_pos):
                        if mode == "Back":
                            in_welcome = True 
                            in_menu = False
                        else:
                            ai_mode = mode
                            in_menu = False  

    else:
        draw_board()
        draw_pieces()
        draw_legal_moves()
        pygame.display.flip()

        if board.is_game_over():
            result = board.result()
            if result == "1-0":
                show_result("You Win!")
            elif result == "0-1":
                show_result("You Lose!")
            else:
                show_result("Draw!")
            reset_game()
            in_welcome = True  
            continue

        if ai_mode == "Player vs Player":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    square = get_square_from_mouse(mouse_pos)

                    if selected_piece is None:
                        piece = board.piece_at(square)
                        if piece and piece.color == board.turn: 
                            selected_piece = square
                    else:
                        move = chess.Move(selected_piece, square)
                        if move in board.legal_moves:
                            if move in board.legal_moves:
                                if is_about_to_checkmate(board, move):
                                    board.push(move)
                                    draw_board()
                                    draw_pieces()
                                    pygame.display.flip()
                                    time.sleep(5)  
                                    show_result("You Win!")
                                    reset_game()
                                    in_welcome = True
                                    continue
                        
                            board.push(move)
                            selected_piece = None
                            
                        else:
                            piece = board.piece_at(square)
                            if piece and piece.color == board.turn:
                                selected_piece = square  

        else:
            if board.turn == chess.WHITE:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        square = get_square_from_mouse(mouse_pos)
    
                        if selected_piece is None:
                            piece = board.piece_at(square)
                            if piece and piece.color == chess.WHITE:
                                selected_piece = square
                        else:
                            move = chess.Move(selected_piece, square)
                            if move in board.legal_moves:
                                if is_about_to_checkmate(board, move):
                                    board.push(move)
                                    draw_board()
                                    draw_pieces()
                                    pygame.display.flip()
                                    time.sleep(5)  
                                    show_result("You Win!")
                                    reset_game()
                                    in_welcome = True
                                    continue
                                
                                board.push(move)
                                selected_piece = None
                            else:
                                piece = board.piece_at(square)
                                if piece and piece.color == chess.WHITE:
                                    selected_piece = square  
            else:
                pygame.time.delay(500)  
                move = get_ai_move()

                if is_about_to_checkmate(board, move):
                    board.push(move)
                    draw_board()
                    draw_pieces()
                    pygame.display.flip()
                    time.sleep(5)  
                    show_result("You Lose!")
                    reset_game()
                    in_welcome = True
                    continue
                
                board.push(move)
                selected_piece = None
    pygame.display.flip()        
pygame.quit()