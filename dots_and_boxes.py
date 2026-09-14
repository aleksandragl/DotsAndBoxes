"""
Dots and Boxes (Punktid ja kastid) täisversioon.

Mängulaud:
- 6 punkti (2 rida, 3 veergu)
- 7 joont (2 kasti)
- Mängijad: A (inimene) ja B (arvuti - Minimax või Greedy)
- Seis salvestatakse kujul: "0000000.A"
"""

import time
import tkinter as tk
from tkinter import messagebox

# 7 joone indeksid ja nende ühendatud punktid:
# Punktid:
# (0,0)=0   (0,1)=1   (0,2)=2
# (1,0)=3   (1,1)=4   (1,2)=5
#
# Jooned:
# 0: horisontaalne (0,0)-(0,1)
# 1: horisontaalne (0,1)-(0,2)
# 2: vertikaalne   (0,0)-(1,0)
# 3: vertikaalne   (0,1)-(1,1) [ühine joon mõlemale kastile]
# 4: vertikaalne   (0,2)-(1,2)
# 5: horisontaalne (1,0)-(1,1)
# 6: horisontaalne (1,1)-(1,2)

BOXES = [
    (0, 2, 3, 5),  # Kast 0 (vasakpoolne kast)
    (1, 3, 4, 6),  # Kast 1 (parempoolne kast)
]

INITIAL_STATE = "0000000.A"

# Jõudlustesti sõlmede loendur
_node_count = 0


def reset_node_count() -> None:
    """Lähtestab Minimaxi külastatud sõlmede loenduri."""
    global _node_count
    _node_count = 0


def get_node_count() -> int:
    """Tagastab Minimaxi külastatud sõlmede arvu."""
    global _node_count
    return _node_count


def get_completed_boxes(lines_str: str) -> list[int]:
    """Tagastab lõpetatud (kõik 4 joont tõmmatud) kastide indeksid."""
    completed = []
    for box_idx, lines in enumerate(BOXES):
        if all(lines_str[line_idx] == "1" for line_idx in lines):
            completed.append(box_idx)
    return completed


def get_available_moves(lines_str: str) -> list[int]:
    """Tagastab vabade joonte indeksid (kus väärtus on '0')."""
    return [i for i, val in enumerate(lines_str) if val == "0"]


def apply_move(state: str, move: int) -> str:
    """
    Rakendab käigu antud seisule ja tagastab uue seisu stringina.

    Parameetrid:
        state (str): Seis formaadis "0000000.A" (7 numbrit, punkt, mängija 'A' või 'B')
        move (int): Joone indeks (0..6)

    Tagastab:
        str: Uus seis samas formaadis (nt "1000000.B")
    """
    if not (0 <= move <= 6):
        raise ValueError(f"Vigane käik: {move}. Lubatud on 0..6.")

    lines_str, current_player = state.split(".")
    if lines_str[move] == "1":
        raise ValueError(f"Joon {move} on juba tõmmatud!")

    old_completed = get_completed_boxes(lines_str)

    # Tõmbame joone
    new_lines = list(lines_str)
    new_lines[move] = "1"
    new_lines_str = "".join(new_lines)

    new_completed = get_completed_boxes(new_lines_str)
    boxes_made = len(new_completed) - len(old_completed)

    # Kui mängija lõpetab kasti, saab ta uue käigu (jääb samaks)
    if boxes_made > 0:
        next_player = current_player
    else:
        next_player = "B" if current_player == "A" else "A"

    return f"{new_lines_str}.{next_player}"


def evaluate_state(state: str) -> float:
    """
    Hindab seisu vastavalt etteantud reeglitele:
    3 joont = +5, 2 joont = +2, 1 joon = +0.5 iga kasti kohta.
    """
    lines_str = state.split(".")[0]
    score = 0.0
    for box in BOXES:
        drawn = sum(1 for line_idx in box if lines_str[line_idx] == "1")
        if drawn == 3:
            score += 5.0
        elif drawn == 2:
            score += 2.0
        elif drawn == 1:
            score += 0.5
    return score


# Eelgenereeritud üleminekute ja heuristiliste väärtuste tabel (256 seisu)
_TRANSITIONS: dict[str, dict[int, tuple[str, float, str]]] = {}
_EVAL_TABLE: dict[str, float] = {}


def _init_lookup_tables() -> None:
    """Genereerib ühekordselt kõigi 256 võimaliku seisu üleminekud ja hinnangud."""
    for i in range(128):
        lines_str = f"{i:07b}"
        _EVAL_TABLE[lines_str] = evaluate_state(lines_str + ".A")
        avail = [idx for idx, c in enumerate(lines_str) if c == "0"]
        old_comp = len(get_completed_boxes(lines_str))
        for p in ("A", "B"):
            st = f"{lines_str}.{p}"
            tr = {}
            for m in avail:
                ns = apply_move(st, m)
                nl, np = ns.split(".")
                pts = (len(get_completed_boxes(nl)) - old_comp) * 10.0
                tr[m] = (ns, pts, np)
            _TRANSITIONS[st] = tr


_init_lookup_tables()


def minimax(
    state: str, depth: int = 4, is_maximizing: bool = True
) -> tuple[float, int | None]:
    """
    Optimeeritud Minimax algoritm etteantud sügavusega (vaikimisi depth=4).
    Arvestab boonuskäike (kasti sulgemisel käib sama mängija uuesti).
    Mängija B on maksimeerija (arvuti), Mängija A on minimeerija (inimene).

    Tagastab:
        (hinnang, parim_käik)
    """
    global _node_count
    _node_count += 1

    trans = _TRANSITIONS.get(state)
    if trans is None:
        lines_str, current_player = state.split(".")
        avail = get_available_moves(lines_str)
        old_comp = len(get_completed_boxes(lines_str))
        trans = {}
        for m in avail:
            ns = apply_move(state, m)
            nl, np = ns.split(".")
            pts = (len(get_completed_boxes(nl)) - old_comp) * 10.0
            trans[m] = (ns, pts, np)

    # Baasjuht 1: mäng on läbi (vabu käike pole)
    if not trans:
        return 0.0, None

    # Baasjuht 2: sügavuspiirang saavutatud, kasutame evaluate_state heuristikat
    if depth == 0:
        base_eval = _EVAL_TABLE.get(state[:7], evaluate_state(state))
        val = base_eval if is_maximizing else -base_eval
        return val, None

    if is_maximizing:
        best_val = -float("inf")
        best_move = next(iter(trans.keys()))
        for move, (next_state, pts, next_player) in trans.items():
            val, _ = minimax(next_state, depth - 1, is_maximizing=(next_player == "B"))
            total_val = pts + val
            if total_val > best_val:
                best_val = total_val
                best_move = move
        return best_val, best_move
    else:
        best_val = float("inf")
        best_move = next(iter(trans.keys()))
        for move, (next_state, pts, next_player) in trans.items():
            val, _ = minimax(next_state, depth - 1, is_maximizing=(next_player == "B"))
            total_val = -pts + val
            if total_val < best_val:
                best_val = total_val
                best_move = move
        return best_val, best_move


def computer_move_minimax(state: str, depth: int = 4) -> int:
    """Arvuti (B) parima käigu leidmine Minimaxi abil (depth=4)."""
    _, move = minimax(state, depth=depth, is_maximizing=True)
    if move is None:
        available = get_available_moves(state.split(".")[0])
        if not available:
            raise ValueError("Käike pole enam saadaval!")
        return available[0]
    return move


def computer_move_greedy(state: str) -> int:
    """
    Arvuti käik Greedy (ahne) algoritmiga:
    1. Kui leidub käik, mis sulgeb kasti (saab kohe punkti), valib selle.
    2. Kui kasti sulgeda ei saa, valib käigu, mis ei tekita vastasele 3. joont (ohutu käik).
    3. Kui ohutuid käike pole, teeb esimese vaba käigu.
    """
    lines_str = state.split(".")[0]
    available = get_available_moves(lines_str)
    if not available:
        raise ValueError("Käike pole enam saadaval!")

    old_completed = len(get_completed_boxes(lines_str))

    # 1. Kontrollime, kas mõni käik sulgeb kohe kasti
    best_box_move = None
    max_boxes = 0
    for move in available:
        next_state = apply_move(state, move)
        next_lines = next_state.split(".")[0]
        boxes = len(get_completed_boxes(next_lines)) - old_completed
        if boxes > max_boxes:
            max_boxes = boxes
            best_box_move = move

    if best_box_move is not None:
        return best_box_move

    # 2. Otsime käiku, mis ei tekitaks vastasele kuskil 3. joont
    safe_moves = []
    for move in available:
        next_state = apply_move(state, move)
        next_lines = next_state.split(".")[0]
        creates_3_lines = any(
            sum(1 for idx in box if next_lines[idx] == "1") == 3 for box in BOXES
        )
        if not creates_3_lines:
            safe_moves.append(move)

    if safe_moves:
        return safe_moves[0]

    # 3. Kui ohutuid käike pole, teeme esimese vaba käigu
    return available[0]


def get_best_move(state: str) -> int:
    """Tagasiühilduv abifunktsioon arvuti parima käigu saamiseks."""
    return computer_move_minimax(state, depth=4)


def measure_performance(state: str = INITIAL_STATE) -> list[dict]:
    """
    Performance test: mõõdab Minimaxi kiirust sügavustel 1 kuni 6.
    Loendab külastatud sõlmed ja mõõdab kulunud aega.
    Prindib tabeli ja tagastab tulemused listina.
    """
    results = []
    header = f"{'Sügavus (Depth)':^16} | {'Sõlmed (Nodes)':^16} | {'Aeg (sek)':^14} | {'Nodes/min':^16}"
    sep = "-" * len(header)
    print("\n" + sep)
    print(header)
    print(sep)

    for depth in range(1, 7):
        reset_node_count()
        start_time = time.perf_counter()
        minimax(state, depth=depth, is_maximizing=True)
        elapsed = time.perf_counter() - start_time
        nodes = get_node_count()
        nodes_per_min = (nodes / elapsed) * 60 if elapsed > 0 else 0.0

        entry = {
            "depth": depth,
            "nodes": nodes,
            "time": elapsed,
            "nodes_per_min": nodes_per_min,
        }
        results.append(entry)
        print(f"{depth:^16} | {nodes:^16} | {elapsed:^14.6f} | {nodes_per_min:^16.0f}")

    print(sep + "\n")
    return results


class DotsAndBoxesGUI:
    """Dots and Boxes graafiline kasutajaliides (Tkinter)."""

    DOT_COORDS = [
        (130, 120),  # (0,0)
        (280, 120),  # (0,1)
        (430, 120),  # (0,2)
        (130, 260),  # (1,0)
        (280, 260),  # (1,1)
        (430, 260),  # (1,2)
    ]

    LINE_DOTS = [
        (0, 1),  # Joon 0: horisontaalne ülemine vasak
        (1, 2),  # Joon 1: horisontaalne ülemine parem
        (0, 3),  # Joon 2: vertikaalne vasak
        (1, 4),  # Joon 3: vertikaalne keskmine
        (2, 5),  # Joon 4: vertikaalne parem
        (3, 4),  # Joon 5: horisontaalne alumine vasak
        (4, 5),  # Joon 6: horisontaalne alumine parem
    ]

    BOX_CENTERS = [
        (205, 190),  # Kast 0
        (355, 190),  # Kast 1
    ]

    COLOR_DEFAULT_LINE = "#D6DBDF"
    COLOR_HOVER_LINE = "#AED6F1"
    COLOR_PLAYER_A = "#1E88E5"  # Sinine (Inimene)
    COLOR_PLAYER_B = "#E53935"  # Punane (Arvuti)

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Dots and Boxes (Punktid ja kastid)")
        self.root.resizable(False, False)

        self.state = INITIAL_STATE
        self.box_owners = [None, None]
        self.scores = {"A": 0, "B": 0}
        self.ai_mode = "Minimax"  # "Minimax" või "Greedy"
        self.is_ai_thinking = False

        self._setup_ui()
        self.update_view()

    def _setup_ui(self):
        # 1. Ülemine juhtpaneel: AI valikunupud ja Jõudlustest
        self.top_control_frame = tk.Frame(self.root, bg="#ECEFF1", padx=10, pady=8)
        self.top_control_frame.pack(fill=tk.X)

        tk.Label(
            self.top_control_frame,
            text="AI Režiim:",
            font=("Helvetica", 10, "bold"),
            bg="#ECEFF1",
        ).pack(side=tk.LEFT, padx=(0, 6))

        self.btn_ai_minimax = tk.Button(
            self.top_control_frame,
            text="AI: Minimax (Depth 4)",
            font=("Helvetica", 9, "bold"),
            command=lambda: self.set_ai_mode("Minimax"),
            relief=tk.SUNKEN,
            bg="#BBDEFB",
            padx=8,
            pady=2,
        )
        self.btn_ai_minimax.pack(side=tk.LEFT, padx=3)

        self.btn_ai_greedy = tk.Button(
            self.top_control_frame,
            text="AI: Greedy",
            font=("Helvetica", 9),
            command=lambda: self.set_ai_mode("Greedy"),
            relief=tk.RAISED,
            bg="#E0E0E0",
            padx=8,
            pady=2,
        )
        self.btn_ai_greedy.pack(side=tk.LEFT, padx=3)

        self.btn_perf = tk.Button(
            self.top_control_frame,
            text="Jõudlustest",
            font=("Helvetica", 9),
            command=self.show_performance_window,
            bg="#FFE082",
            padx=8,
            pady=2,
        )
        self.btn_perf.pack(side=tk.RIGHT, padx=5)

        # 2. Skooritabel ja käigu info
        self.scoreboard_frame = tk.Frame(self.root, bg="#37474F", padx=15, pady=8)
        self.scoreboard_frame.pack(fill=tk.X)

        self.lbl_score_table = tk.Label(
            self.scoreboard_frame,
            text="Skoor | Mängija A (Inimene): 0   vs   Arvuti B (Minimax): 0",
            font=("Helvetica", 11, "bold"),
            bg="#37474F",
            fg="#ECEFF1",
        )
        self.lbl_score_table.pack(side=tk.LEFT)

        self.lbl_turn = tk.Label(
            self.scoreboard_frame,
            text="Käik: Mängija A",
            font=("Helvetica", 11, "bold"),
            bg="#37474F",
            fg="#64B5F6",
        )
        self.lbl_turn.pack(side=tk.RIGHT)

        # 3. Seisukoodi kuvamine
        self.state_frame = tk.Frame(self.root, bg="#CFD8DC", pady=3)
        self.state_frame.pack(fill=tk.X)
        self.lbl_state = tk.Label(
            self.state_frame,
            text=f"Seis: {self.state}",
            font=("Courier", 10, "bold"),
            bg="#CFD8DC",
            fg="#263238",
        )
        self.lbl_state.pack()

        # 4. Mängulaua lõuend (Canvas)
        self.canvas = tk.Canvas(
            self.root, width=560, height=360, bg="#FAFAFA", highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=6)

        self.line_item_ids: dict[int, int] = {}
        self.box_text_ids: dict[int, int] = {}

        self._draw_board()

        # 5. Alumine paneel
        self.footer_frame = tk.Frame(self.root, pady=8)
        self.footer_frame.pack(fill=tk.X)

        self.btn_reset = tk.Button(
            self.footer_frame,
            text="Uus mäng",
            font=("Helvetica", 11),
            command=self.reset_game,
            padx=12,
            pady=3,
        )
        self.btn_reset.pack()

    def set_ai_mode(self, mode: str):
        """Vahetab aktiivset AI režiimi (Minimax või Greedy)."""
        self.ai_mode = mode
        if mode == "Minimax":
            self.btn_ai_minimax.config(relief=tk.SUNKEN, bg="#BBDEFB", font=("Helvetica", 9, "bold"))
            self.btn_ai_greedy.config(relief=tk.RAISED, bg="#E0E0E0", font=("Helvetica", 9))
        else:
            self.btn_ai_greedy.config(relief=tk.SUNKEN, bg="#C8E6C9", font=("Helvetica", 9, "bold"))
            self.btn_ai_minimax.config(relief=tk.RAISED, bg="#E0E0E0", font=("Helvetica", 9))
        self.update_view()

    def show_performance_window(self):
        """Käivitab performance testi ja kuvab tulemused aknas."""
        results = measure_performance(self.state)

        win = tk.Toplevel(self.root)
        win.title("Minimax Jõudlustest (Depth 1-6)")
        win.resizable(False, False)

        tk.Label(
            win,
            text="Minimax jõudlustesti tulemused",
            font=("Helvetica", 12, "bold"),
            pady=10,
        ).pack()

        text_frame = tk.Frame(win, padx=15, pady=10)
        text_frame.pack()

        table_header = f"{'Sügavus (Depth)':^16} | {'Sõlmed (Nodes)':^16} | {'Aeg (sek)':^14} | {'Nodes/min':^16}\n"
        table_sep = "-" * len(table_header.strip()) + "\n"
        table_content = table_header + table_sep

        for r in results:
            table_content += (
                f"{r['depth']:^16} | {r['nodes']:^16} | {r['time']:^14.6f} | {r.get('nodes_per_min', 0.0):^16.0f}\n"
            )
        table_content += table_sep

        lbl_table = tk.Label(
            text_frame,
            text=table_content,
            font=("Courier", 10),
            justify=tk.LEFT,
            bg="#263238",
            fg="#ECEFF1",
            padx=10,
            pady=10,
        )
        lbl_table.pack()

        tk.Button(win, text="Sulge", command=win.destroy, padx=10, pady=3).pack(pady=(0, 10))

    def _draw_board(self):
        self.canvas.delete("all")
        self.line_item_ids.clear()
        self.box_text_ids.clear()

        # 1. Kastide tekstikohad
        for box_idx, (cx, cy) in enumerate(self.BOX_CENTERS):
            owner = self.box_owners[box_idx]
            text = owner if owner else ""
            color = self.COLOR_PLAYER_A if owner == "A" else self.COLOR_PLAYER_B
            tid = self.canvas.create_text(
                cx, cy, text=text, font=("Helvetica", 28, "bold"), fill=color
            )
            self.box_text_ids[box_idx] = tid

        # 2. 7 joont
        lines_str = self.state.split(".")[0]
        for line_idx, (dot1, dot2) in enumerate(self.LINE_DOTS):
            x1, y1 = self.DOT_COORDS[dot1]
            x2, y2 = self.DOT_COORDS[dot2]

            is_drawn = lines_str[line_idx] == "1"
            color = "#455A64" if is_drawn else self.COLOR_DEFAULT_LINE
            width = 6

            line_id = self.canvas.create_line(
                x1, y1, x2, y2, fill=color, width=width, capstyle=tk.ROUND
            )
            self.line_item_ids[line_idx] = line_id

            if not is_drawn:
                self.canvas.tag_bind(
                    line_id, "<Button-1>", lambda e, idx=line_idx: self.on_line_click(idx)
                )
                self.canvas.tag_bind(
                    line_id, "<Enter>", lambda e, lid=line_id: self._on_hover(lid, True)
                )
                self.canvas.tag_bind(
                    line_id, "<Leave>", lambda e, lid=line_id: self._on_hover(lid, False)
                )

        # 3. 6 punkti
        dot_radius = 8
        for x, y in self.DOT_COORDS:
            self.canvas.create_oval(
                x - dot_radius,
                y - dot_radius,
                x + dot_radius,
                y + dot_radius,
                fill="#263238",
                outline="#FFFFFF",
                width=2,
            )

    def _on_hover(self, line_id: int, entering: bool):
        current_turn = self.state.split(".")[1]
        if current_turn == "A" and not self.is_ai_thinking:
            new_color = self.COLOR_HOVER_LINE if entering else self.COLOR_DEFAULT_LINE
            self.canvas.itemconfig(line_id, fill=new_color)
            self.canvas.config(cursor="hand2" if entering else "")

    def on_line_click(self, move: int):
        """Mängija A (inimene) teeb käigu."""
        current_turn = self.state.split(".")[1]
        if current_turn != "A" or self.is_ai_thinking:
            return

        lines_str = self.state.split(".")[0]
        if lines_str[move] == "1":
            return

        self._execute_move(move, player="A")

    def _execute_move(self, move: int, player: str):
        old_state = self.state
        old_completed = get_completed_boxes(old_state.split(".")[0])

        new_state = apply_move(old_state, move)
        self.state = new_state

        line_color = self.COLOR_PLAYER_A if player == "A" else self.COLOR_PLAYER_B
        line_id = self.line_item_ids[move]
        self.canvas.itemconfig(line_id, fill=line_color, width=6)
        self.canvas.tag_unbind(line_id, "<Button-1>")
        self.canvas.tag_unbind(line_id, "<Enter>")
        self.canvas.tag_unbind(line_id, "<Leave>")
        self.canvas.config(cursor="")

        new_lines = new_state.split(".")[0]
        new_completed = get_completed_boxes(new_lines)
        newly_closed = [b for b in new_completed if b not in old_completed]

        for b in newly_closed:
            self.box_owners[b] = player
            self.scores[player] += 1
            tid = self.box_text_ids[b]
            self.canvas.itemconfig(tid, text=player, fill=line_color)

        self.update_view()

        if self._check_game_over():
            return

        next_turn = self.state.split(".")[1]
        if next_turn == "B":
            self.is_ai_thinking = True
            self.root.after(450, self._ai_move)

    def _ai_move(self):
        """Arvuti (B) teeb käigu valitud AI režiimiga (Minimax või Greedy)."""
        if self._check_game_over():
            self.is_ai_thinking = False
            return

        next_turn = self.state.split(".")[1]
        if next_turn != "B":
            self.is_ai_thinking = False
            return

        if self.ai_mode == "Minimax":
            best_move = computer_move_minimax(self.state, depth=4)
        else:
            best_move = computer_move_greedy(self.state)

        self._execute_move(best_move, player="B")
        self.is_ai_thinking = False

    def _check_game_over(self) -> bool:
        lines_str = self.state.split(".")[0]
        if "0" not in lines_str:
            self._handle_game_over()
            return True
        return False

    def _handle_game_over(self):
        score_a = self.scores["A"]
        score_b = self.scores["B"]

        if score_a > score_b:
            msg = f"Mäng läbi! Võitis Mängija A ({score_a} vs {score_b})!"
        elif score_b > score_a:
            msg = f"Mäng läbi! Võitis Arvuti B [{self.ai_mode}] ({score_b} vs {score_a})!"
        else:
            msg = f"Mäng läbi! Viik ({score_a} vs {score_b})!"

        self.lbl_turn.config(text=msg, fg="#81C784")
        messagebox.showinfo("Mäng läbi", msg)

    def update_view(self):
        current_turn = self.state.split(".")[1]
        lines_str = self.state.split(".")[0]

        self.lbl_state.config(text=f"Seis: {self.state}")
        self.lbl_score_table.config(
            text=f"Skoor | Mängija A: {self.scores['A']}   vs   Arvuti B ({self.ai_mode}): {self.scores['B']}"
        )

        if "0" in lines_str:
            if current_turn == "A":
                self.lbl_turn.config(text="Käik: Mängija A (Sina)", fg="#64B5F6")
            else:
                self.lbl_turn.config(
                    text=f"Käik: Arvuti B ({self.ai_mode} mõtleb...)", fg="#EF5350"
                )

    def reset_game(self):
        """Alustab uut mängu."""
        self.state = INITIAL_STATE
        self.box_owners = [None, None]
        self.scores = {"A": 0, "B": 0}
        self.is_ai_thinking = False
        self._draw_board()
        self.update_view()


def main():
    root = tk.Tk()
    app = DotsAndBoxesGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
