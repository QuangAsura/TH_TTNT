import tkinter as tk
from tkinter import ttk
import copy
import math
import threading

BG         = "#0f0f13"
PANEL_BG   = "#1a1a24"
CELL_BG    = "#22223a"
CELL_HVR   = "#2e2e4a"
CELL_WIN   = "#1a3a2a"
BORDER_CLR = "#3a3a5c"
X_COLOR    = "#5eead4"
O_COLOR    = "#f97316"
TXT_MAIN   = "#e2e8f0"
TXT_SUB    = "#94a3b8"
BTN_BG     = "#2e2e4a"
BTN_ACT    = "#3a3a5c"
STATUS_WIN = "#4ade80"
STATUS_LOSE= "#f87171"
STATUS_TIE = "#fbbf24"

EMPTY = None
X = "X"
O = "O"

def check_winner(board, k):
    n = len(board)
    dirs = [(0,1),(1,0),(1,1),(1,-1)]
    for r in range(n):
        for c in range(n):
            val = board[r][c]
            if val is None:
                continue
            for dr, dc in dirs:
                cells = []
                for d in range(k):
                    nr, nc = r+dr*d, c+dc*d
                    if 0 <= nr < n and 0 <= nc < n and board[nr][nc] == val:
                        cells.append((nr, nc))
                    else:
                        break
                if len(cells) == k:
                    return val, cells
    return None, []

def terminal(board, k):
    w, _ = check_winner(board, k)
    if w:
        return True
    return all(cell is not EMPTY for row in board for cell in row)

def evaluate(board, k, ai_p, hum_p):
    n = len(board)
    score = 0
    dirs = [(0,1),(1,0),(1,1),(1,-1)]
    for r in range(n):
        for c in range(n):
            for dr, dc in dirs:
                line = []
                for d in range(k):
                    nr, nc = r+dr*d, c+dc*d
                    if 0 <= nr < n and 0 <= nc < n:
                        line.append(board[nr][nc])
                    else:
                        break
                if len(line) < k:
                    continue
                ai_cnt  = line.count(ai_p)
                hum_cnt = line.count(hum_p)
                if hum_cnt == 0 and ai_cnt > 0:
                    score += 10 ** ai_cnt
                elif ai_cnt == 0 and hum_cnt > 0:
                    score -= 10 ** hum_cnt
    return score

def actions(board):
    return [(i, j) for i, row in enumerate(board)
            for j, cell in enumerate(row) if cell is EMPTY]

def order_moves(moves, n):
    mid = (n-1) / 2
    return sorted(moves, key=lambda m: abs(m[0]-mid)+abs(m[1]-mid))

def alphabeta(board, depth, alpha, beta, is_max, k, ai_p, hum_p):
    w, _ = check_winner(board, k)
    if w == ai_p:  return 100000 + depth
    if w == hum_p: return -100000 - depth
    if terminal(board, k): return 0
    if depth == 0: return evaluate(board, k, ai_p, hum_p)

    n = len(board)
    moves = order_moves(actions(board), n)

    if is_max:
        v = -math.inf
        for r, c in moves:
            board[r][c] = ai_p
            v = max(v, alphabeta(board, depth-1, alpha, beta, False, k, ai_p, hum_p))
            board[r][c] = EMPTY
            alpha = max(alpha, v)
            if beta <= alpha: break
        return v
    else:
        v = math.inf
        for r, c in moves:
            board[r][c] = hum_p
            v = min(v, alphabeta(board, depth-1, alpha, beta, True, k, ai_p, hum_p))
            board[r][c] = EMPTY
            beta = min(beta, v)
            if beta <= alpha: break
        return v

def best_move(board, k, ai_p, hum_p, max_depth):
    n = len(board)
    moves = order_moves(actions(board), n)
    if not moves:
        return None
    if all(cell is EMPTY for row in board for cell in row):
        return (n//2, n//2)
    best_val, best_act = -math.inf, moves[0]
    for r, c in moves:
        board[r][c] = ai_p
        val = alphabeta(board, max_depth-1, -math.inf, math.inf, False, k, ai_p, hum_p)
        board[r][c] = EMPTY
        if val > best_val:
            best_val, best_act = val, (r, c)
    return best_act


class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe AI")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.n = 3
        self.k = 3
        self.human = X
        self.ai    = O
        self.depth = 3
        self.board = []
        self.game_over   = False
        self.ai_thinking = False
        self.human_turn  = False   # <-- cờ rõ ràng: đến lượt human chưa
        self.scores = {X: 0, "Hòa": 0, O: 0}
        self.buttons = []
        self.status_label = None

        self._build_ui()
        self.new_game()

    def _build_ui(self):
        tk.Label(self.root, text="TIC-TAC-TOE", font=("Courier", 22, "bold"),
                 bg=BG, fg=X_COLOR).pack(pady=(18, 0))
        tk.Label(self.root, text="Alpha-Beta AI", font=("Courier", 10),
                 bg=BG, fg=TXT_SUB).pack(pady=(0, 12))

        cfg = tk.Frame(self.root, bg=PANEL_BG, padx=16, pady=10)
        cfg.pack(padx=20, pady=(0, 10), fill="x")

        def lbl(parent, text):
            return tk.Label(parent, text=text, bg=PANEL_BG, fg=TXT_SUB,
                            font=("Courier", 9))

        def combo(parent, values, default, width=6):
            v = tk.StringVar(value=default)
            cb = ttk.Combobox(parent, textvariable=v, values=values,
                              width=width, state="readonly", font=("Courier", 9))
            return cb, v

        row0 = tk.Frame(cfg, bg=PANEL_BG)
        row0.pack(fill="x", pady=2)

        lbl(row0, "Bàn cờ:").grid(row=0, column=0, padx=(0,4), sticky="w")
        self.cb_size, self.v_size = combo(row0, ["3","4","5","6","7","10"], "3")
        self.cb_size.grid(row=0, column=1, padx=(0,16))

        lbl(row0, "Thắng khi:").grid(row=0, column=2, padx=(0,4), sticky="w")
        self.cb_win, self.v_win = combo(row0, ["3","4","5"], "3")
        self.cb_win.grid(row=0, column=3, padx=(0,16))

        lbl(row0, "Bạn là:").grid(row=0, column=4, padx=(0,4), sticky="w")
        self.cb_player, self.v_player = combo(row0, ["X (đi trước)","O (đi sau)"],
                                              "X (đi trước)", 12)
        self.cb_player.grid(row=0, column=5, padx=(0,16))

        lbl(row0, "Độ sâu AI:").grid(row=0, column=6, padx=(0,4), sticky="w")
        self.cb_depth, self.v_depth = combo(row0, ["2","3","4","5"], "3")
        self.cb_depth.grid(row=0, column=7)

        btn_row = tk.Frame(self.root, bg=BG)
        btn_row.pack(pady=(0, 8))
        tk.Button(btn_row, text="▶  Ván mới", command=self.new_game,
                  bg=BTN_BG, fg=X_COLOR, activebackground=BTN_ACT,
                  activeforeground=X_COLOR, relief="flat",
                  font=("Courier", 10, "bold"), padx=14, pady=6,
                  cursor="hand2", bd=0).pack(side="left", padx=6)
        tk.Button(btn_row, text="↺  Xóa điểm", command=self.reset_scores,
                  bg=BTN_BG, fg=TXT_MAIN, activebackground=BTN_ACT,
                  activeforeground=TXT_MAIN, relief="flat",
                  font=("Courier", 10, "bold"), padx=14, pady=6,
                  cursor="hand2", bd=0).pack(side="left", padx=6)

        sc = tk.Frame(self.root, bg=BG)
        sc.pack(pady=(0, 8))
        self.lbl_score_x   = self._score_card(sc, "X thắng", X_COLOR)
        self.lbl_score_tie = self._score_card(sc, "Hòa",     STATUS_TIE)
        self.lbl_score_o   = self._score_card(sc, "O thắng", O_COLOR)

        self.status_label = tk.Label(self.root, text="",
                 font=("Courier", 11, "bold"), bg=BG, fg=TXT_MAIN, height=2)
        self.status_label.pack()

        self.board_frame = tk.Frame(self.root, bg=BG)
        self.board_frame.pack(padx=20, pady=(0, 20))

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TCombobox",
            fieldbackground=CELL_BG, background=CELL_BG,
            foreground=TXT_MAIN, selectbackground=CELL_HVR,
            bordercolor=BORDER_CLR, arrowcolor=TXT_SUB)

    def _score_card(self, parent, label, color):
        f = tk.Frame(parent, bg=PANEL_BG, padx=20, pady=8)
        f.pack(side="left", padx=8)
        tk.Label(f, text=label, font=("Courier", 8), bg=PANEL_BG, fg=TXT_SUB).pack()
        lbl = tk.Label(f, text="0", font=("Courier", 20, "bold"), bg=PANEL_BG, fg=color)
        lbl.pack()
        return lbl

    def new_game(self):
        if self.ai_thinking:
            return

        self.n     = int(self.v_size.get())
        self.k     = min(int(self.v_win.get()), self.n)
        self.human = X if "X" in self.v_player.get() else O
        self.ai    = O if self.human == X else X
        self.depth = int(self.v_depth.get())
        self.board = [[EMPTY]*self.n for _ in range(self.n)]
        self.game_over   = False
        self.ai_thinking = False

        # X luôn đi trước — xác định ngay lượt đầu
        self.human_turn = (self.human == X)

        self._draw_board()
        self._set_status(f"Ván mới!  Bạn={self.human}  AI={self.ai}  |  {self.k} liên tiếp thắng", TXT_MAIN)

        # Nếu AI là X → AI đi trước
        if self.ai == X:
            self.root.after(400, self._ai_turn)

    def _draw_board(self):
        for w in self.board_frame.winfo_children():
            w.destroy()
        self.buttons = []

        cell_px = max(48, min(80, 480 // self.n))
        font_sz = max(14, cell_px // 2)

        for i in range(self.n):
            row_btns = []
            for j in range(self.n):
                frame = tk.Frame(self.board_frame, bg=BORDER_CLR, padx=1, pady=1)
                frame.grid(row=i, column=j, padx=2, pady=2)
                btn = tk.Button(
                    frame,
                    text="",
                    font=("Courier", font_sz, "bold"),
                    bg=CELL_BG, fg=TXT_MAIN,
                    activebackground=CELL_HVR,
                    relief="flat", bd=0,
                    width=max(2, cell_px//16),
                    height=1,
                    cursor="hand2",
                    command=lambda r=i, c=j: self._human_click(r, c)
                )
                btn.pack(fill="both", expand=True,
                         ipadx=cell_px//6, ipady=cell_px//8)
                row_btns.append(btn)
            self.buttons.append(row_btns)

    def _human_click(self, r, c):
        # Chặn nếu: game kết thúc, AI đang nghĩ, không phải lượt human, ô đã đánh
        if self.game_over:
            return
        if self.ai_thinking:
            return
        if not self.human_turn:
            return
        if self.board[r][c] is not EMPTY:
            return

        # Đánh quân
        self.board[r][c] = self.human
        self._render_cell(r, c, self.human)
        self.human_turn = False   # hết lượt human

        # Kiểm tra kết thúc
        w, win_cells = check_winner(self.board, self.k)
        if w:
            self._end_game(w, win_cells)
            return
        if terminal(self.board, self.k):
            self._end_game(None, [])
            return

        # Sang lượt AI
        self._set_status("AI đang suy nghĩ...", TXT_SUB)
        self.root.after(150, self._ai_turn)

    def _ai_turn(self):
        self.ai_thinking = True

        def run():
            board_copy = copy.deepcopy(self.board)
            move = best_move(board_copy, self.k, self.ai, self.human, self.depth)
            self.root.after(0, lambda: self._apply_ai_move(move))

        threading.Thread(target=run, daemon=True).start()

    def _apply_ai_move(self, move):
        self.ai_thinking = False
        if self.game_over:
            return
        if move is None:
            return

        r, c = move
        self.board[r][c] = self.ai
        self._render_cell(r, c, self.ai)
        self._flash_cell(r, c)

        # Kiểm tra kết thúc
        w, win_cells = check_winner(self.board, self.k)
        if w:
            self._end_game(w, win_cells)
            return
        if terminal(self.board, self.k):
            self._end_game(None, [])
            return

        # Trả lượt lại cho human
        self.human_turn = True
        self._set_status(f"Lượt của bạn ({self.human}) — click vào ô trống", TXT_MAIN)

    def _render_cell(self, r, c, val):
        btn = self.buttons[r][c]
        color = X_COLOR if val == X else O_COLOR
        btn.configure(text=val, fg=color, disabledforeground=color,
                      state="disabled", cursor="arrow")

    def _flash_cell(self, r, c):
        btn = self.buttons[r][c]
        def toggle(times, bright):
            if times <= 0:
                btn.configure(bg=CELL_BG)
                return
            btn.configure(bg=CELL_HVR if bright else CELL_BG)
            self.root.after(90, lambda: toggle(times-1, not bright))
        toggle(4, True)

    def _end_game(self, w, win_cells):
        self.game_over  = True
        self.human_turn = False

        for r, c in win_cells:
            self.buttons[r][c].configure(bg=CELL_WIN)

        if w is None:
            self.scores["Hòa"] += 1
            self._set_status("HÒA! Bàn cờ đầy.", STATUS_TIE)
        elif w == self.human:
            self.scores[w] += 1
            self._set_status(f"🎉  Bạn THẮNG!  ({w})", STATUS_WIN)
        else:
            self.scores[w] += 1
            self._set_status(f"AI THẮNG!  ({w})", STATUS_LOSE)

        self._update_score_ui()

    def _update_score_ui(self):
        self.lbl_score_x.configure(text=str(self.scores[X]))
        self.lbl_score_o.configure(text=str(self.scores[O]))
        self.lbl_score_tie.configure(text=str(self.scores["Hòa"]))

    def reset_scores(self):
        self.scores = {X: 0, "Hòa": 0, O: 0}
        self._update_score_ui()

    def _set_status(self, msg, color=TXT_MAIN):
        if self.status_label:
            self.status_label.configure(text=msg, fg=color)


if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg=BG)
    app = TicTacToeApp(root)
    root.mainloop()
