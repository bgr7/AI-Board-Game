#Bugra Baygul 20190705005-072
import pygame
import sys
import copy
import os
import random
from button import Button
from scoreboard import Scoreboard
from sound_manager import SoundManager


class Game:
    def __init__(self, difficulty_mode='normal'):

        pygame.init()
        self.sound_manager = SoundManager(muted=False)

        self.screen = pygame.display.set_mode((700, 750))
        pygame.display.set_caption("Bugra Baygul's Board Game")
        self.clock = pygame.time.Clock()

        self.state = "main_menu"  # state vars
        self.difficulty_mode = difficulty_mode
        self.difficulty_depth = self.depth_m(self.difficulty_mode)
        self.scoreboard = Scoreboard()
        self.nickname_input = ""

        self.current_music = "background_music.mp3"
        self.sound_manager.playmusic(self.current_music)
        self.gameReset()
        self.font = pygame.font.SysFont(None, 30)
        self.title_font = pygame.font.SysFont(None, 50)

        self.rule_loader()

        self.transposition_table = {}
        self.hashing_keys = self.create_key()

    def rule_loader(self):

        self.rule_pages = []
        for i in range(1, 6):  # from p1.png to p5.png
            filename = f"p{i}.png"
            if os.path.exists(filename):
                img = pygame.image.load(filename)
                self.rule_pages.append(img)
            else:
                break
        self.current_rule_page = 0

    def gameReset(self):

        self.board = [[' ' for _ in range(7)] for _ in range(7)]
        self.initialize_board()
        self.current_player = 'P1'  # I made AI starts first as mentioned in manual
        self.move_count = 0
        self.selected_piece = None
        self.valid_moves = []
        self.moves_made = 0
        self.moves_needed = self.needMove_calc('P2')
        self.running = True
        # self.player_nickname = ""  # denemee

        self.piece_id_counter = 1
        self.positions_to_ids = {}
        self.ids_to_positions = {}
        self.moved_piece_ids = set()
        self.pieceId_determine()

        # thetransposition table cleared when reset game
        self.transposition_table = {}

    def depth_m(self, mode):

        if mode == 'easy':
            return 1
        elif mode == 'hard':  # I changed depth according to game mode which determines ai move on minimax_ab algo.
            return 3
        else:
            return 2

    def initialize_board(self):

        self.board[0][0] = 'P1'
        self.board[2][0] = 'P1'
        self.board[4][6] = 'P1'
        self.board[6][6] = 'P1'
        self.board[0][6] = 'P2'
        self.board[2][6] = 'P2'
        self.board[4][0] = 'P2'
        self.board[6][0] = 'P2'

    def pieceId_determine(self):

        for i in range(7):
            for j in range(7):
                if self.board[i][j] in ['P1', 'P2']:
                    self.positions_to_ids[(i, j)] = self.piece_id_counter  # I assigned unique id's for each piece
                    self.ids_to_positions[self.piece_id_counter] = (i, j)
                    self.piece_id_counter += 1

    def menu_Render(self):

        self.screen.fill((200, 200, 200))
        title = self.title_font.render("Bugra Baygul's Board Game", True, (0, 0, 0))
        self.screen.blit(title, (150, 200))

        # creating and drawing buttons here
        start_button = Button(250, 300, 200, 50, "Start", font_size=28)
        settings_button = Button(250, 370, 200, 50, "Settings", font_size=28)
        rules_button = Button(250, 440, 200, 50, "Rules", font_size=28)
        scoreboard_button = Button(250, 510, 200, 50, "Scoreboard", font_size=28)
        quit_button = Button(250, 580, 200, 50, "Quit", font_size=28)

        start_button.render(self.screen)
        settings_button.render(self.screen)
        rules_button.render(self.screen)
        scoreboard_button.render(self.screen)
        quit_button.render(self.screen)

    def settings_render(self):

        self.screen.fill((200, 200, 200))
        title = self.title_font.render("Settings", True, (0, 0, 0))
        self.screen.blit(title, (280, 200))

        easy_button = Button(250, 300, 200, 50, "Easy", highlighted=(self.difficulty_mode == 'easy'), font_size=28)
        normal_button = Button(250, 370, 200, 50, "Normal", highlighted=(self.difficulty_mode == 'normal'),
                               font_size=28)
        hard_button = Button(250, 440, 200, 50, "Hard", highlighted=(self.difficulty_mode == 'hard'), font_size=28)
        mute_text = "Unmute" if self.sound_manager.muted else "Mute"
        mute_button = Button(250, 510, 200, 50, mute_text, font_size=28)
        back_button = Button(250, 580, 200, 50, "Back", font_size=28)

        easy_button.render(self.screen)
        normal_button.render(self.screen)
        hard_button.render(self.screen)
        mute_button.render(self.screen)
        back_button.render(self.screen)

    def scoreboard_render(self):

        self.screen.fill((200, 200, 200))
        title = self.title_font.render("Scoreboard", True, (0, 0, 0))
        self.screen.blit(title, (280, 50))

        modes = ['easy', 'normal', 'hard']
        start_y = 100
        for mode in modes:
            mode_title = self.font.render(f"Mode: {mode.capitalize()}", True, (0, 0, 0))
            self.screen.blit(mode_title, (50, start_y))
            start_y = start_y + 30
            for idx, (name, piece_count) in enumerate(self.scoreboard.scoreboard.get(mode, [])):
                record_text = f"{idx + 1}. {name} - {piece_count} pieces"
                txt = self.font.render(record_text, True, (0, 0, 0))
                self.screen.blit(txt, (70, start_y))
                start_y = start_y+ 25
            start_y =start_y + 10

        back_button = Button(250, 680, 200, 50, "Back", font_size=28)
        back_button.render(self.screen)

    def rules_render(self):

        self.screen.fill((200, 200, 200))
        title = self.title_font.render("Rules", True, (0, 0, 0))
        self.screen.blit(title, (300, 50))

        if self.rule_pages:
            page_img = self.rule_pages[self.current_rule_page]
            rect = page_img.get_rect(center=(350, 350))
            self.screen.blit(page_img, rect)

            # I did it for multiple pages to show prev and next buttons appear
            if self.current_rule_page > 0:
                prev_button = Button(100, 680, 100, 50, "Prev", font_size=28)
                prev_button.render(self.screen)
            if self.current_rule_page < len(self.rule_pages) - 1:
                next_button = Button(500, 680, 100, 50, "Next", font_size=28)
                next_button.render(self.screen)

        back_button = Button(250, 680, 200, 50, "Back", font_size=28)
        back_button.render(self.screen)

    def gameOver_rendr(self, winner):

        self.board_render()
        message = "Game Over! "
        if winner == 'Draw':
            message += "Draw !"
        elif winner == 'P1':
            message += "You Lost!"
        else:
            message += "You Win!"
        text = self.font.render(message, True, (0, 0, 0))
        self.screen.blit(text, (250, 350))

        restart_button = Button(250, 400, 200, 50, "Restart", font_size=28)
        main_menu_button = Button(250, 470, 200, 50, "Main Menu", font_size=28)
        restart_button.render(self.screen)
        main_menu_button.render(self.screen)

    def board_render(self):

        self.screen.fill((255, 255, 255))
        #to draw grid lines on boqrd
        for x in range(0, 700, 100):
            pygame.draw.line(self.screen, (0, 0, 0), (x, 0), (x, 700), 2)
        for y in range(0, 700, 100):
            pygame.draw.line(self.screen, (0, 0, 0), (0, y), (700, y), 2)

        #to draw pieces
        for i in range(7):
            for j in range(7):
                cell = self.board[i][j]
                x = j * 100 + 50
                y = i * 100 + 50
                if cell == 'P1':
                    pygame.draw.polygon(self.screen, (255, 0, 0),
                                        [(x, y - 30), (x - 25, y + 20), (x + 25, y + 20)])
                elif cell == 'P2':
                    pygame.draw.circle(self.screen, (0, 255, 0), (x, y), 30)

        #to highlight selected piece
        if self.selected_piece:
            i, j = self.selected_piece
            pygame.draw.rect(self.screen, (100, 255, 0), (j * 100, i * 100, 100, 100), 3)

        #highlighting valid moves cells
        for move in self.valid_moves:
            i, j = move
            pygame.draw.rect(self.screen, (0, 255, 0), (j * 100, i * 100, 100, 100), 3)

        # to display how much moves left
        moves_left_text = self.font.render(f"Moves Left: {50 - self.move_count}", True, (0, 0, 0))
        self.screen.blit(moves_left_text, (10, 720))
        difficulty_text = self.font.render(f"Mode: {self.difficulty_mode.capitalize()}", True, (0, 0, 0))
        self.screen.blit(difficulty_text, (500, 720))

        menu_button = Button(190, 710, 100, 30, "Menu", font_size=20)
        restart_button = Button(300, 710, 100, 30, "Restart", font_size=20)
        menu_button.render(self.screen)
        restart_button.render(self.screen)

    def nickname_area(self):

        self.screen.fill((200, 200, 200))
        prompt = self.title_font.render("Enter your nickname:", True, (0, 0, 0))
        self.screen.blit(prompt, (200, 200))

        txt_surface = self.font.render(self.nickname_input, True, (0, 0, 0))
        input_rect = pygame.Rect(200, 300, 300, 50)
        pygame.draw.rect(self.screen, (255, 255, 255), input_rect)
        self.screen.blit(txt_surface, (input_rect.x + 5, input_rect.y + 10))

        instructions = self.font.render("Press Enter to start", True, (0, 0, 0))
        self.screen.blit(instructions, (200, 360))

    def mainmenu_handler(self, pos):

        start_button = Button(250, 300, 200, 50, "Start")
        settings_button = Button(250, 370, 200, 50, "Settings")  # buttons defined here
        rules_button = Button(250, 440, 200, 50, "Rules")
        scoreboard_button = Button(250, 510, 200, 50, "Scoreboard")
        quit_button = Button(250, 580, 200, 50, "Quit")

        if start_button.click_handler(pos):
            self.sound_manager.playsound(self.sound_manager.rotate_sound)
            self.state = "nickname"
            self.nickname_input = ""
        elif settings_button.click_handler(pos):
            self.sound_manager.playsound(self.sound_manager.rotate_sound)
            self.state = "settings"
        elif rules_button.click_handler(pos):
            self.sound_manager.playsound(self.sound_manager.rotate_sound)
            self.state = "rules"
            self.current_rule_page = 0
        elif scoreboard_button.click_handler(pos):
            self.sound_manager.playsound(self.sound_manager.rotate_sound)
            self.state = "scoreboard"
        elif quit_button.click_handler(pos):
            self.sound_manager.playsound(self.sound_manager.rotate_sound)
            self.running = False

    def settings_handler(self, pos):

        easy_button = Button(250, 300, 200, 50, "Easy")
        normal_button = Button(250, 370, 200, 50, "Normal")
        hard_button = Button(250, 440, 200, 50, "Hard")
        mute_text = "Unmute" if self.sound_manager.muted else "Mute"
        mute_button = Button(250, 510, 200, 50, mute_text)
        back_button = Button(250, 580, 200, 50, "Back")

        if easy_button.click_handler(pos):
            self.sound_manager.playsound(self.sound_manager.rotate_sound)
            if self.difficulty_mode == 'hard':
                self.sound_manager.playmusic("background_music.mp3")
            self.difficulty_mode = 'easy'
            self.difficulty_depth = self.depth_m('easy')
        elif normal_button.click_handler(pos):
            self.sound_manager.playsound(self.sound_manager.rotate_sound)
            if self.difficulty_mode == 'hard':
                self.sound_manager.playmusic("background_music.mp3")
            self.difficulty_mode = 'normal'
            self.difficulty_depth = self.depth_m('normal')
        elif hard_button.click_handler(pos):
            self.sound_manager.playsound(self.sound_manager.rotate_sound)
            if self.difficulty_mode != 'hard':
                self.sound_manager.playmusic("hard.mp3")
            self.difficulty_mode = 'hard'
            self.difficulty_depth = self.depth_m('hard')
        elif mute_button.click_handler(pos):
            self.sound_manager.mute()
        elif back_button.click_handler(pos):
            self.sound_manager.playsound(self.sound_manager.rotate_sound)
            self.state = "main_menu"

    def scoreboard_handler(self, pos):

        back_button = Button(250, 680, 200, 50, "Back")
        if back_button.click_handler(pos):
            self.sound_manager.playsound(self.sound_manager.rotate_sound)
            self.state = "main_menu"

    def rules_handler(self, pos):

        back_button = Button(250, 680, 200, 50, "Back")
        if back_button.click_handler(pos):
            self.sound_manager.playsound(self.sound_manager.rotate_sound)
            self.state = "main_menu"
            return

        if self.rule_pages and self.current_rule_page > 0:
            prev_button = Button(100, 680, 100, 50, "Prev")  # to show previous rule photo
            if prev_button.click_handler(pos):
                self.sound_manager.playsound(self.sound_manager.rotate_sound)
                self.current_rule_page -= 1

        # Next page
        if self.rule_pages and self.current_rule_page < len(self.rule_pages) - 1:
            next_button = Button(500, 680, 100, 50, "Next")
            if next_button.click_handler(pos):
                self.sound_manager.playsound(self.sound_manager.rotate_sound)
                self.current_rule_page += 1

    def gameOver_func(self, pos, winner):

        restart_button = Button(250, 400, 200, 50, "Restart")
        main_menu_button = Button(250, 470, 200, 50, "Main Menu")
        if restart_button.click_handler(pos):
            self.sound_manager.playsound(self.sound_manager.rotate_sound)
            pygame.mixer.stop()
            self.gameReset()
            self.music_mode()
            self.state = "game"
        elif main_menu_button.click_handler(pos):
            self.sound_manager.playsound(self.sound_manager.rotate_sound)
            pygame.mixer.stop()
            self.music_mode()
            self.state = "main_menu"

    def music_mode(self):

        if self.difficulty_mode == 'hard':
            self.sound_manager.playmusic("hard.mp3")
        else:
            self.sound_manager.playmusic("background_music.mp3")

    def game_handle(self, pos):

        menu_button = Button(190, 710, 100, 30, "Menu", font_size=20)
        restart_button = Button(300, 710, 100, 30, "Restart", font_size=20)

        if menu_button.click_handler(pos):
            self.sound_manager.playsound(self.sound_manager.rotate_sound)
            pygame.mixer.stop()
            self.state = "main_menu"
            return

        if restart_button.click_handler(pos):
            self.sound_manager.playsound(self.sound_manager.rotate_sound)
            pygame.mixer.stop()
            self.gameReset()
            self.music_mode()
            self.state = "game"
            return

        if self.current_player == 'P2':
            x, y = pos
            if y > 700:
                return
            j = x // 100
            i = y // 100

            if self.selected_piece:
                if (i, j) in self.valid_moves:
                    from_pos = self.selected_piece
                    to_pos = (i, j)
                    piece_id = self.positions_to_ids[from_pos]
                    if piece_id in self.moved_piece_ids:
                        self.selected_piece = None
                        self.valid_moves = []
                        return

                    p1_before = sum(row.count('P1') for row in self.board)

                    self.board = self.movemaker(self.board, (from_pos, to_pos), 'P2')
                    self.move_count += 1
                    self.moves_made += 1
                    self.moved_piece_ids.add(piece_id)
                    self.update_positions(from_pos, to_pos, piece_id)
                    print(f"{self.player_nickname} moves from {from_pos} to {to_pos}")

                    self.selected_piece = None
                    self.valid_moves = []

                    self.runcaptures()

                    p1_after = sum(row.count('P1') for row in self.board)
                    if p1_after < p1_before:
                        self.sound_manager.playsound(self.sound_manager.clear_sound)

                    if self.moves_made >= self.moves_needed:
                        self.current_player = 'P1'
                        self.moves_made = 0
                        self.moved_piece_ids = set()
                else:
                    self.selected_piece = None
                    self.valid_moves = []
            else:
                if 0 <= i < 7 and 0 <= j < 7 and self.board[i][j] == 'P2':
                    piece_id = self.positions_to_ids.get((i, j))
                    if piece_id not in self.moved_piece_ids:
                        self.selected_piece = (i, j)
                        self.valid_moves = self.getter_validmoves(i, j)

    def nickname_handle_in(self, event):

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.nickname_input.strip():
                    self.player_nickname = self.nickname_input.strip()
                    self.gameReset()
                    self.music_mode()
                    self.state = "game"
                else:
                    pass
            elif event.key == pygame.K_BACKSPACE:
                self.nickname_input = self.nickname_input[:-1]
            else:
                if len(self.nickname_input) < 15:
                    self.nickname_input += event.unicode

    def update_positions(self, from_pos, to_pos, piece_id):

        # internal mapping updated when pieces moved

        del self.positions_to_ids[from_pos] #representing the original position (i, j).
        self.positions_to_ids[to_pos] = piece_id #unique ID of the moved piece.
        self.ids_to_positions[piece_id] = to_pos #representing the new position (i, j).

    def getter_validmoves(self, i, j):

        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for d in directions:
            ni, nj = i + d[0], j + d[1]
            if 0 <= ni < 7 and 0 <= nj < 7 and self.board[ni][nj] == ' ':
                moves.append((ni, nj))
        return moves

    def movemaker(self, board, move, player):

        (i1, j1), (i2, j2) = move
        board[i1][j1] = ' '
        board[i2][j2] = player
        return board

    def captures(self, board, player):

        opponent = 'P2' if player == 'P1' else 'P1'
        to_capture = set()
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for i, j in [(x, y) for x in range(7) for y in range(7) if board[x][y] == player]:
            for d in directions:
                captures = []
                ni, nj = i + d[0], j + d[1]
                while 0 <= ni < 7 and 0 <= nj < 7:
                    cell = board[ni][nj]
                    if cell == opponent:
                        captures.append((ni, nj))
                        ni += d[0]
                        nj += d[1]
                    elif cell == player:
                        if captures:
                            for ci, cj in captures:
                                to_capture.add((ci, cj))
                        break
                    else:
                        break
                else:
                    if captures:
                        for ci, cj in captures:
                            to_capture.add((ci, cj))

        return to_capture

    def runcaptures(self):

        opponent = 'P2' if self.current_player == 'P1' else 'P1'
        p2_before = sum(row.count('P2') for row in self.board)

        current_captures = self.captures(self.board,
                                         self.current_player)  # all possible captures for both players.
        opponent_captures = self.captures(self.board, opponent)
        all_captures = current_captures.union(opponent_captures)
        for (x, y) in all_captures:
            self.board[x][y] = ' '

        p2_after = sum(row.count('P2') for row in self.board)
        if self.current_player == 'P1' and p2_after < p2_before:
            self.sound_manager.playsound(self.sound_manager.aiate_sound)

    def checkgameover(self):

        p1_pieces = sum(row.count('P1') for row in self.board)
        p2_pieces = sum(row.count('P2') for row in self.board)

        if p1_pieces == 0 and p2_pieces == 0:
            return True, 'Draw'
        if p1_pieces == 1 and p2_pieces == 1:
            return True, 'Draw'
        if p1_pieces > 0 and p2_pieces == 0:
            return True, 'P1'
        if p1_pieces == 0 and p2_pieces > 0:
            return True, 'P2'
        if self.move_count >= 50:
            if p1_pieces == p2_pieces:
                return True, 'Draw'
            elif p1_pieces > p2_pieces:
                return True, 'P1'
            else:
                return True, 'P2'
        return False, None

    def create_key(self):

        piece_symbols = [' ', 'P1', 'P2']
        keys = {}
        for i in range(7):
            for j in range(7):  # creating hashing keys for hashing board states.
                for symbol in piece_symbols:
                    keys[(i, j, symbol)] = random.getrandbits(64)
        return keys

    def hash_board(self, board):

        h = 0
        for i in range(7):
            for j in range(7):
                piece = board[i][j]
                if piece != ' ':
                    h ^= self.hashing_keys[(i, j, piece)]
        return h

    def evaluate(self, board):

        center_positions = {(3, 3), (3, 2), (3, 4), (2, 3),
                            (4, 3)}  # I made it since I recognized centered squares are important for game
        p1_score = 0
        p2_score = 0

        for i in range(7):
            for j in range(7):
                cell = board[i][j]
                if cell == 'P1':
                    p1_score = p1_score+1
                    if (i, j) in center_positions:
                        p1_score =p1_score + 0.2
                elif cell == 'P2':
                    p2_score =p2_score+ 1
                    if (i, j) in center_positions:
                        p2_score =p2_score+ 0.2

        p1_capturable = len(self.captures(board, 'P1'))  # for potential captures
        p2_capturable = len(self.captures(board, 'P2'))

        captures_diff = (p2_capturable - p1_capturable) * 0.1

        return (p1_score - p2_score) - captures_diff

    def order_move(self, board, moves, player):

        def heuristic(move_seq):
            temp_board = copy.deepcopy(board)
            for m in move_seq:
                temp_board = self.movemaker(temp_board, m, player)
            temp_board = self.simulatenous_capture(temp_board)

            opponent = 'P2' if player == 'P1' else 'P1'
            opp_before = sum(row.count(opponent) for row in board)
            opp_after = sum(row.count(opponent) for row in temp_board)

            return (opp_before - opp_after)  #high one is better since capture more

        moves.sort(key=heuristic, reverse=True)  #descending order so best capturing moves appear first
        return moves

    def minimax_ab(self, board, depth, maxplayer, alpha, beta):

        keyfor_board = self.hash_board(board)  #hash done for the current board
        if keyfor_board in self.transposition_table:  # transposition table checked
            cscore, cdepth = self.transposition_table[keyfor_board]
            if cdepth >= depth:
                return cscore, None
        #checkingterminal states
        is_over, winner = self.checkgameover()
        if depth == 0 or is_over:
            val = self.evaluate(board)
            # Store in transposition table
            self.transposition_table[keyfor_board] = (val, depth)
            return val, None
        if maxplayer:
            calcMax = float('-inf')
            bestmove_order = None

            # order all successors for player1(ai)
            all_moves = self.successor_getter(board, 'P1')
            all_moves = self.order_move(board, all_moves, 'P1')

            for move_seq in all_moves:
                new_board = copy.deepcopy(board)
                for move in move_seq:
                    new_board = self.movemaker(new_board, move, 'P1')
                new_board = self.simulatenous_capture(new_board)

                score_calcd, _ = self.minimax_ab(new_board, depth - 1, False, alpha, beta)
                if score_calcd > calcMax:
                    calcMax = score_calcd
                    bestmove_order = move_seq
                alpha = max(alpha, score_calcd)
                if beta <= alpha:
                    break
            # store best result
            self.transposition_table[keyfor_board] = (calcMax, depth)
            return calcMax, bestmove_order  # containing the evaluation score and the best move sequence.

        else:
            minEval = float('inf')
            bestmove_order = None
            # order all successors for plyer
            all_moves = self.successor_getter(board, 'P2')
            all_moves = self.order_move(board, all_moves, 'P2')

            for move_seq in all_moves:
                new_board = copy.deepcopy(board)
                for move in move_seq:
                    new_board = self.movemaker(new_board, move, 'P2')
                new_board = self.simulatenous_capture(new_board)
                score_calcd, _ = self.minimax_ab(new_board, depth - 1, True, alpha, beta)
                if score_calcd < minEval:
                    minEval = score_calcd
                    bestmove_order = move_seq
                beta = min(beta, score_calcd)
                if beta <= alpha:
                    break

            self.transposition_table[keyfor_board] = (minEval, depth)  # best result
            return minEval, bestmove_order

    def simulatenous_capture(self, board):

        p1_captures = self.captures(board, 'P1')
        p2_captures = self.captures(board, 'P2')
        all_captures = p1_captures.union(p2_captures)
        new_board = copy.deepcopy(board)
        for (x, y) in all_captures:
            new_board[x][y] = ' '
        return new_board

    def successor_getter(self, board, player):

        successors = []
        positions = [(i, j) for i in range(7) for j in range(7) if board[i][j] == player]
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        # generate possible move orderds for a player.
        single_moves = []
        for pos in positions:
            i, j = pos
            for d in directions:
                ni, nj = i + d[0], j + d[1]
                if 0 <= ni < 7 and 0 <= nj < 7 and board[ni][nj] == ' ':
                    single_moves.append((pos, (ni, nj)))

        # if the player has more than one piece two moves required
        if len(positions) > 1:
            for m1 in single_moves:
                for m2 in single_moves:
                    if m1[0] != m2[0]:  # different pieces
                        successors.append([m1, m2])
        else:
            for move in single_moves:
                successors.append([move])

        return successors

    def needMove_calc(self, player):

        num_pieces = sum(row.count(player) for row in self.board)
        return 2 if num_pieces > 1 else 1

    def moveAi(self):

        depth = self.difficulty_depth
        # minimax_ab search applied only required data taken
        _, best_moves = self.minimax_ab(self.board, depth, True, float('-inf'), float('inf'))

        if best_moves:
            for move in best_moves:
                from_pos, to_pos = move
                piece_id = self.positions_to_ids[from_pos]  # ai player's move using the minimax_ab algorithm.
                if piece_id in self.moved_piece_ids:
                    continue
                self.board = self.movemaker(self.board, move, 'P1')
                self.move_count += 1
                self.update_positions(from_pos, to_pos, piece_id)
                self.moved_piece_ids.add(piece_id)
                print(f"ai moves from {from_pos} to {to_pos}") #debugg

                self.runcaptures()
            print(f"Ai's moves: {best_moves}")
        else:
            print("Ai hasn't got valid moves!")

        self.current_player = 'P2'
        self.moves_made = 0
        self.moves_needed = self.needMove_calc('P2')
        self.moved_piece_ids = set()

    def check_player_win(self, winner):

        if winner == 'P2':
            # player's pieces count
            player_pieces = sum(row.count('P2') for row in self.board)
            self.scoreboard.add_record(self.difficulty_mode, self.player_nickname, player_pieces)

    def run(self):

        winner = None
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                elif self.state == "nickname":
                    self.nickname_handle_in(event)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    if self.state == "main_menu":
                        self.mainmenu_handler(pos)
                    elif self.state == "settings":
                        self.settings_handler(pos)
                    elif self.state == "scoreboard":
                        self.scoreboard_handler(pos)
                    elif self.state == "rules":
                        self.rules_handler(pos)
                    elif self.state == "game":
                        self.game_handle(pos)
                    elif self.state == "game_over":
                        self.gameOver_func(pos, winner)

            if self.state == "game":
                if self.current_player == 'P1':
                    self.moveAi()

                is_over, winner = self.checkgameover()
                if is_over:
                    pygame.mixer.music.stop()
                    if winner == 'Draw':
                        self.sound_manager.playsound(self.sound_manager.draw_sound)
                    elif winner == 'P1':
                        self.sound_manager.playsound(self.sound_manager.gameover_sound)
                    elif winner == 'P2':
                        self.sound_manager.playsound(self.sound_manager.win_sound)

                    self.check_player_win(winner)
                    self.state = "game_over"

            if self.state == "main_menu":
                self.menu_Render()
            elif self.state == "settings":
                self.settings_render()
            elif self.state == "scoreboard":
                self.scoreboard_render()
            elif self.state == "rules":
                self.rules_render()
            elif self.state == "game":
                self.board_render()
            elif self.state == "game_over":
                self.gameOver_rendr(winner)
            elif self.state == "nickname":
                self.nickname_area()

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Game(difficulty_mode='normal')
    game.run()
