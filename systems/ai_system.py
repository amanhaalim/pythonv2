# systems/ai_system.py
import math
import random


class AISystem:
    """Rule-based + Minimax AI for puzzle opponents and enemies."""

    # ── TIC TAC TOE ──────────────────────────────────────────────────────────

    def ttt_best_move(self, board):
        """Return best move for AI (O=2) using minimax."""
        best_score = -math.inf
        best_move = None
        for r in range(3):
            for c in range(3):
                if board[r][c] == 0:
                    board[r][c] = 2
                    score = self._ttt_minimax(board, False, -math.inf, math.inf, 0)
                    board[r][c] = 0
                    if score > best_score:
                        best_score = score
                        best_move = (r, c)
        return best_move

    def _ttt_minimax(self, board, is_max, alpha, beta, depth):
        winner = self._ttt_check_winner(board)
        if winner == 2:
            return 10 - depth
        if winner == 1:
            return depth - 10
        if all(board[r][c] != 0 for r in range(3) for c in range(3)):
            return 0

        if is_max:
            best = -math.inf
            for r in range(3):
                for c in range(3):
                    if board[r][c] == 0:
                        board[r][c] = 2
                        best = max(best, self._ttt_minimax(board, False, alpha, beta, depth + 1))
                        board[r][c] = 0
                        alpha = max(alpha, best)
                        if beta <= alpha:
                            break
            return best
        else:
            best = math.inf
            for r in range(3):
                for c in range(3):
                    if board[r][c] == 0:
                        board[r][c] = 1
                        best = min(best, self._ttt_minimax(board, True, alpha, beta, depth + 1))
                        board[r][c] = 0
                        beta = min(beta, best)
                        if beta <= alpha:
                            break
            return best

    def _ttt_check_winner(self, board):
        for row in board:
            if row[0] == row[1] == row[2] != 0:
                return row[0]
        for c in range(3):
            if board[0][c] == board[1][c] == board[2][c] != 0:
                return board[0][c]
        if board[0][0] == board[1][1] == board[2][2] != 0:
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != 0:
            return board[0][2]
        return 0

    def ttt_get_winner(self, board):
        return self._ttt_check_winner(board)

    # ── CONNECT FOUR ─────────────────────────────────────────────────────────

    ROWS = 6
    COLS = 7

    def c4_best_move(self, board):
        """Return best column for AI (player=2) using minimax depth 4."""
        best_score = -math.inf
        best_col = None
        valid = [c for c in range(self.COLS) if board[0][c] == 0]
        random.shuffle(valid)
        for col in valid:
            temp = [row[:] for row in board]
            self._c4_drop(temp, col, 2)
            score = self._c4_minimax(temp, 4, -math.inf, math.inf, False)
            if score > best_score:
                best_score = score
                best_col = col
        return best_col

    def _c4_drop(self, board, col, player):
        for r in range(self.ROWS - 1, -1, -1):
            if board[r][col] == 0:
                board[r][col] = player
                return r
        return -1

    def _c4_minimax(self, board, depth, alpha, beta, is_max):
        w = self._c4_check_winner(board)
        if w == 2:
            return 1000 + depth
        if w == 1:
            return -(1000 + depth)
        if depth == 0 or all(board[0][c] != 0 for c in range(self.COLS)):
            return self._c4_score_board(board, 2)

        valid = [c for c in range(self.COLS) if board[0][c] == 0]
        if is_max:
            best = -math.inf
            for col in valid:
                temp = [row[:] for row in board]
                self._c4_drop(temp, col, 2)
                best = max(best, self._c4_minimax(temp, depth - 1, alpha, beta, False))
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
            return best
        else:
            best = math.inf
            for col in valid:
                temp = [row[:] for row in board]
                self._c4_drop(temp, col, 1)
                best = min(best, self._c4_minimax(temp, depth - 1, alpha, beta, True))
                beta = min(beta, best)
                if beta <= alpha:
                    break
            return best

    def _c4_score_board(self, board, player):
        score = 0
        # Center column preference
        center = [board[r][self.COLS // 2] for r in range(self.ROWS)]
        score += center.count(player) * 3

        # Horizontal
        for r in range(self.ROWS):
            for c in range(self.COLS - 3):
                window = [board[r][c + i] for i in range(4)]
                score += self._c4_score_window(window, player)
        # Vertical
        for c in range(self.COLS):
            for r in range(self.ROWS - 3):
                window = [board[r + i][c] for i in range(4)]
                score += self._c4_score_window(window, player)
        # Diagonal
        for r in range(self.ROWS - 3):
            for c in range(self.COLS - 3):
                window = [board[r + i][c + i] for i in range(4)]
                score += self._c4_score_window(window, player)
            for c in range(3, self.COLS):
                window = [board[r + i][c - i] for i in range(4)]
                score += self._c4_score_window(window, player)
        return score

    def _c4_score_window(self, window, player):
        opp = 1 if player == 2 else 2
        if window.count(player) == 4:
            return 100
        if window.count(player) == 3 and window.count(0) == 1:
            return 5
        if window.count(player) == 2 and window.count(0) == 2:
            return 2
        if window.count(opp) == 3 and window.count(0) == 1:
            return -4
        return 0

    def _c4_check_winner(self, board):
        for player in [1, 2]:
            for r in range(self.ROWS):
                for c in range(self.COLS - 3):
                    if all(board[r][c + i] == player for i in range(4)):
                        return player
            for c in range(self.COLS):
                for r in range(self.ROWS - 3):
                    if all(board[r + i][c] == player for i in range(4)):
                        return player
            for r in range(self.ROWS - 3):
                for c in range(self.COLS - 3):
                    if all(board[r + i][c + i] == player for i in range(4)):
                        return player
                for c in range(3, self.COLS):
                    if all(board[r + i][c - i] == player for i in range(4)):
                        return player
        return 0

    def c4_drop(self, board, col, player):
        return self._c4_drop(board, col, player)

    def c4_get_winner(self, board):
        return self._c4_check_winner(board)

    def c4_is_valid(self, board, col):
        return 0 <= col < self.COLS and board[0][col] == 0
