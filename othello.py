import tkinter as tk
from tkinter import messagebox
import numpy as np
from typing import Tuple, List

class Othello:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("オセロ")
        self.window.configure(bg='#1B5E20')  # より深い緑色の背景
        
        # メインフレームを作成（ボード用）
        self.main_frame = tk.Frame(
            self.window,
            bg='#1B5E20',
            padx=20,
            pady=20
        )
        self.main_frame.pack(expand=True)
        
        self.size = 8
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.current_player = 1  # 1: 黒, -1: 白
        self.directions = [(0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)]
        
        # 初期配置
        self.board[3][3] = self.board[4][4] = -1
        self.board[3][4] = self.board[4][3] = 1
        
        # ステータス表示用のラベル
        self.status_label = tk.Label(
            self.window,
            text="あなたの番です",
            font=('Helvetica', 14, 'bold'),
            bg='#1B5E20',
            fg='white',
            pady=10
        )
        self.status_label.pack()
        
        self.buttons = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.create_board()
        self.update_board()
        
    def create_board(self):
        for i in range(self.size):
            frame = tk.Frame(self.main_frame, bg='#1B5E20')
            frame.pack()
            for j in range(self.size):
                self.buttons[i][j] = tk.Button(
                    frame,
                    width=4,
                    height=2,
                    command=lambda x=i, y=j: self.handle_click(x, y),
                    bg='#2E7D32',  # マスの色
                    relief=tk.RAISED,  # 立体的な外観
                    borderwidth=1,
                    highlightthickness=1,
                    highlightbackground='black'  # マスの境界線
                )
                self.buttons[i][j].pack(side=tk.LEFT, padx=1, pady=1)

    def update_board(self):
        for i in range(self.size):
            for j in range(self.size):
                # デフォルトの背景色を設定
                bg = '#2E7D32'
                
                if self.board[i][j] == 1:
                    text = "⬤"  # 黒石
                    fg = 'black'
                elif self.board[i][j] == -1:
                    text = "⬤"  # 白石
                    fg = 'white'
                else:
                    # 空のマス
                    text = ""
                    fg = 'black'  # デフォルトの文字色
                
                self.buttons[i][j].config(
                    text=text,
                    fg=fg,
                    bg=bg,
                    font=('Helvetica', 20, 'bold'),
                    activebackground=bg,
                    activeforeground=fg
                )

    def is_valid_move(self, row: int, col: int, player: int) -> bool:
        if self.board[row][col] != 0:
            return False
            
        for dx, dy in self.directions:
            x, y = row + dx, col + dy
            if not self.is_within_bounds(x, y) or self.board[x][y] != -player:
                continue
                
            x, y = x + dx, y + dy
            while self.is_within_bounds(x, y):
                if self.board[x][y] == 0:
                    break
                if self.board[x][y] == player:
                    return True
                x, y = x + dx, y + dy
        return False

    def get_valid_moves(self, player: int) -> List[Tuple[int, int]]:
        valid_moves = []
        for i in range(self.size):
            for j in range(self.size):
                if self.is_valid_move(i, j, player):
                    valid_moves.append((i, j))
        return valid_moves

    def make_move(self, row: int, col: int, player: int) -> None:
        self.board[row][col] = player
        for dx, dy in self.directions:
            x, y = row + dx, col + dy
            to_flip = []
            
            while self.is_within_bounds(x, y) and self.board[x][y] == -player:
                to_flip.append((x, y))
                x, y = x + dx, y + dy
                
            if self.is_within_bounds(x, y) and self.board[x][y] == player:
                for flip_x, flip_y in to_flip:
                    self.board[flip_x][flip_y] = player

    def is_within_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.size and 0 <= col < self.size

    def negamax(self, depth: int, alpha: float, beta: float, player: int) -> Tuple[float, Tuple[int, int]]:
        if depth == 0:
            return self.evaluate() * player, None

        valid_moves = self.get_valid_moves(player)
        if not valid_moves:
            if not self.get_valid_moves(-player):
                return self.evaluate() * player, None
            score, _ = self.negamax(depth-1, -beta, -alpha, -player)
            return -score, None

        best_score = float('-inf')
        best_move = valid_moves[0]
        
        for move in valid_moves:
            board_backup = self.board.copy()
            self.make_move(move[0], move[1], player)
            score, _ = self.negamax(depth-1, -beta, -alpha, -player)
            score = -score
            self.board = board_backup
            
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, score)
            if alpha >= beta:
                break
                
        return best_score, best_move

    def evaluate(self) -> float:
        # 評価関数
        corner_weight = 100
        edge_weight = 10
        mobility_weight = 1
        
        value = 0
        # コーナーの評価
        corners = [(0,0), (0,7), (7,0), (7,7)]
        for x, y in corners:
            value += corner_weight * self.board[x][y]
            
        # エッジの評価
        for i in range(self.size):
            value += edge_weight * self.board[0][i]
            value += edge_weight * self.board[7][i]
            value += edge_weight * self.board[i][0]
            value += edge_weight * self.board[i][7]
            
        # 機動力（有効手の数）の評価
        value += mobility_weight * (len(self.get_valid_moves(1)) - len(self.get_valid_moves(-1)))
        
        return value

    def handle_click(self, row: int, col: int):
        if not self.is_valid_move(row, col, self.current_player):
            return

        self.make_move(row, col, self.current_player)
        self.update_board()
        self.current_player = -self.current_player
        
        # ステータス更新
        self.status_label.config(text="AI が考えています...")
        self.window.update()

        # AIの手番（1秒後に実行）
        if self.current_player == -1:
            self.window.after(1000, self.ai_move)

    def ai_move(self):
        _, move = self.negamax(4, float('-inf'), float('inf'), -1)
        if move:
            self.make_move(move[0], move[1], -1)
            self.update_board()
            self.current_player = 1
            self.status_label.config(text="あなたの番です")

        if not self.get_valid_moves(1):
            if not self.get_valid_moves(-1):
                self.game_over()
            else:
                self.status_label.config(text="パスです。AI の番です")
                self.window.after(1000, self.ai_move)

    def game_over(self):
        black_count = np.count_nonzero(self.board == 1)
        white_count = np.count_nonzero(self.board == -1)
        
        if black_count > white_count:
            message = "あなたの勝利！"
        elif white_count > black_count:
            message = "AI の勝利！"
        else:
            message = "引き分け！"
        
        # メッセージボックスのスタイルをカスタマイズ
        self.window.option_add('*Dialog.msg.font', 'Helvetica 12')
        messagebox.showinfo("ゲーム終了", 
                          f"{message}\n\n黒(あなた): {black_count}枚\n白(AI): {white_count}枚")
        self.window.quit()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    game = Othello()
    game.run() 