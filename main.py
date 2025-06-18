import random
import sys
import time
from copy import copy
import bisect
import pygame
from pygame.locals import *

# 初始化pygame
pygame.init()
pygame.mixer.init(frequency=44100)

# 常量定义
BOARD_SIZE = 9  # 9x9棋盘
GRID_SIZE = 60  # 每个格子的像素大小
WINDOW_WIDTH = BOARD_SIZE * GRID_SIZE
WINDOW_HEIGHT = BOARD_SIZE * GRID_SIZE + 100  # 增加顶部信息栏高度
BACKGROUND_COLOR = (238, 203, 173)  # 象棋底色(浅棕色)
LINE_COLOR = (220, 20, 20)  # 红色线条
RED_PIECE_COLOR = (220, 20, 20)  # 红色棋子
BLACK_PIECE_COLOR = (20, 20, 20)  # 黑色棋子
HIGHLIGHT_COLOR = (20, 220, 20, 180)  # 高亮颜色
INFO_BG_COLOR = (230, 230, 230)  # 信息栏背景色
DIALOG_BG_COLOR = (240, 240, 240)  # 对话框背景色
RED_WINNER_ROUND = 199

# 创建游戏窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Variant Chess Game')


# 棋子类
class Piece:
    def __init__(self, piece_type, color, position):
        self.piece_type = piece_type
        self.color = color
        self.position = position
        self.selected = False

    def draw(self, surface, offset_y=0):
        x, y = self.position
        center_x = x * GRID_SIZE + GRID_SIZE // 2
        center_y = y * GRID_SIZE + GRID_SIZE // 2 + offset_y
        radius = GRID_SIZE // 2 - 5

        # 绘制棋子圆形
        color = RED_PIECE_COLOR if self.color == 'red' else BLACK_PIECE_COLOR
        pygame.draw.circle(surface, color, (center_x, center_y), radius)
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), radius, 2)

        # 绘制棋子文字
        font = pygame.font.SysFont('SimHei', 24)
        text = font.render(self.piece_type, True, (255, 255, 255))
        text_rect = text.get_rect(center=(center_x, center_y))
        surface.blit(text, text_rect)

        # 如果被选中，绘制高亮边框
        if self.selected:
            pygame.draw.circle(surface, HIGHLIGHT_COLOR, (center_x, center_y), radius + 3, 3)


# 游戏类
class ChessGame:
    def __init__(self):

        self.super_move = False
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.red_piece = None
        self.black_pieces = []
        self.selected_piece = None
        self.turn = 'red'  # 玩家先走
        self.round_count = 0
        self.piece_sequence = ['卒', '士', '象', '马', '炮', '车']  # 黑色棋子出现顺序
        self.piece_sequence_en = {'卒': 'Zu', '士': 'Shi', '象': 'Xiang', '马': 'Ma', '炮': 'Pao', '车': 'Ju'}
        self.current_piece_index = 0  # 当前应出现的棋子索引
        self.piece_appearance_interval = 3  # 每3回合出现新棋子
        self.appearance_count = 0  # 新增棋子次数计数器
        self.game_over = False
        self.winner = None
        self.occur_index = [0, 10, 30, 50, 70, 100]
        self.choice_weight = [20, 15, 10, 10, 10, 5]

        self.new_pieces_count = None
        self.occur_pieces = None
        self.reset_game()
        self.control_refresh()

    def reset_game(self):
        """重置游戏状态"""
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.red_piece = None
        self.black_pieces = []
        self.selected_piece = None
        self.turn = 'red'
        self.round_count = 0
        self.current_piece_index = 0
        self.appearance_count = 0
        self.game_over = False
        self.winner = None

        # 初始化棋子
        self.initialize_pieces()

    def initialize_pieces(self):
        # 创建玩家的红车
        red_rook = Piece('车', 'red', (4, 5))
        self.place_piece(red_rook, (4, 5))
        self.red_piece = red_rook

        # 创建三个黑卒
        for i in range(4, 9, 2):
            bing = Piece('卒', 'black', (i, 2))
            self.place_piece(bing, (i, 2))
            self.black_pieces.append(bing)

    def control_refresh(self):
        """控制棋子出现的刷新时机"""

        # 刚开始时刷新一次，随后每三回合刷新一次
        if self.round_count == 0:
            self.refresh_probability()
        elif self.round_count % self.piece_appearance_interval == 0:
            self.refresh_probability()
        else:
            ...

    def refresh_probability(self):
        """刷新棋子出现概率"""

        """
        前50回车 每三回合出现生成一起棋子，后
        """

        # 50关之内，随机出现一到三个棋子
        if self.round_count < 50:
            self.new_pieces_count = random.choices([1, 2, 3], [10, 20, 5])[0]
        else:
            # 50关之后，棋盘棋子数量小于五，一次出现五个，小于十一次出现4个，否则保持随机
            if len(self.black_pieces) < 5:
                self.new_pieces_count = 5
            elif len(self.black_pieces) < 10:
                self.new_pieces_count = 4
            else:
                self.new_pieces_count = random.choices([1, 2, 3], [10, 20, 5])[0]
        piece_slice = bisect.bisect_right(self.occur_index, self.round_count)
        occur_piece_list = self.piece_sequence[:piece_slice]
        occur_piece_wight_list = self.choice_weight[:piece_slice]
        self.occur_pieces = random.choices(occur_piece_list, occur_piece_wight_list, k=self.new_pieces_count)

        if self.round_count > 30:
            self.piece_appearance_interval = min(5, self.round_count // 30 + 3)

        if self.round_count > 100:
            self.choice_weight = [20, 15, 15, 15, 15, 10]

    def place_piece(self, piece, position):
        """将棋子放在指定位置"""
        x, y = position
        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
            self.board[y][x] = piece
            piece.position = (x, y)
            return True
        return False

    def is_position_empty(self, position):
        """检查位置是否为空"""
        x, y = position
        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
            return self.board[y][x] is None
        return False

    def is_position_red_piece(self, position):
        """检查位置是否有红棋"""
        x, y = position
        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
            piece = self.board[y][x]
            return piece and piece.color == 'red'
        return False

    def add_black_piece(self, piece_type, count=1):
        """添加指定数量的黑色棋子到随机空位"""
        for _ in range(count):
            empty_positions = [
                (x, y)
                for y in range(BOARD_SIZE)
                for x in range(BOARD_SIZE)
                if self.is_position_empty((x, y)) and not self.is_position_red_piece((x, y))
            ]
            if empty_positions:
                position = random.choice(empty_positions)
                new_piece = Piece(piece_type, 'black', position)
                self.place_piece(new_piece, position)
                self.black_pieces.append(new_piece)

    def add_general_with_guards(self):
        """添加将和两个士（特殊规则）"""
        possible_positions = []

        # 寻找适合将和士的位置（）
        for y in range(0, BOARD_SIZE):  # 底部区域
            for x in range(0, BOARD_SIZE):  # 中间区域
                # 检查将的位置是否为空
                if self.is_position_empty((x, y)) and not self.is_position_red_piece((x, y)):
                    # 检查可能的士位置（对角线方向）
                    guard_positions = [
                        (x - 1, y - 1), (x + 1, y - 1),
                        (x - 1, y + 1), (x + 1, y + 1)
                    ]

                    # 寻找两个有效士位置
                    valid_guards = [pos for pos in guard_positions
                                    if self.is_position_empty(pos) and
                                    0 <= pos[0] < BOARD_SIZE and
                                    0 <= pos[1] < BOARD_SIZE and
                                    not self.is_position_red_piece(pos)]

                    if len(valid_guards) >= 2:
                        possible_positions.append((x, y, valid_guards))

        if possible_positions:
            # 随机选择一个合适的位置组合
            general_x, general_y, guard_options = random.choice(possible_positions)

            # 添加将
            general = Piece('将', 'black', (general_x, general_y))
            self.place_piece(general, (general_x, general_y))
            self.black_pieces.append(general)

            # 添加两个士
            guard1_pos, guard2_pos = random.sample(guard_options, 2)
            guard1 = Piece('士', 'black', guard1_pos)
            guard2 = Piece('士', 'black', guard2_pos)

            self.place_piece(guard1, guard1_pos)
            self.place_piece(guard2, guard2_pos)
            self.black_pieces.extend([guard1, guard2])
            return True
        else:
            # 没有合适位置，随机添加
            self.add_black_piece('将')
            self.add_black_piece('士', 2)

    @staticmethod
    def positions_threatened_by_red_piece(piece):
        """"""
        moves = []
        x, y = piece.position

        # 向右
        for dx in range(1, BOARD_SIZE - x):
            moves.append((x + dx, y))

        # 向左移动
        for dx in range(1, x + 1):
            moves.append((x - dx, y))

        # 向下移动
        for dy in range(1, BOARD_SIZE - y):
            moves.append((x, y + dy))

        # 向上移动
        for dy in range(1, y + 1):
            moves.append((x, y - dy))

        return moves

    def get_valid_moves(self, piece):
        """根据棋子类型获取合法移动（修复了吃子逻辑）"""
        moves = []
        x, y = piece.position

        # 车的移动规则（直线移动）
        if piece.piece_type == '车':
            # 向右移动
            for dx in range(1, BOARD_SIZE - x):
                target = (x + dx, y)
                if not self.is_position_empty(target):
                    # 如果是敌方棋子，可以吃子
                    if self.board[y][x + dx].color != piece.color:
                        moves.append(target)
                    break  # 遇到任何棋子都停止扫描
                moves.append(target)

            # 向左移动
            for dx in range(1, x + 1):
                target = (x - dx, y)
                if not self.is_position_empty(target):
                    if self.board[y][x - dx].color != piece.color:
                        moves.append(target)
                    break
                moves.append(target)

            # 向下移动
            for dy in range(1, BOARD_SIZE - y):
                target = (x, y + dy)
                if not self.is_position_empty(target):
                    if self.board[y + dy][x].color != piece.color:
                        moves.append(target)
                    break
                moves.append(target)

            # 向上移动
            for dy in range(1, y + 1):
                target = (x, y - dy)
                if not self.is_position_empty(target):
                    if self.board[y - dy][x].color != piece.color:
                        moves.append(target)
                    break
                moves.append(target)

        # 卒的移动规则（可上下左右移动一格）
        elif piece.piece_type == '卒':
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # 下、右、上、左
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < BOARD_SIZE and 0 <= new_y < BOARD_SIZE:
                    if self.is_position_empty((new_x, new_y)) or self.board[new_y][new_x].color != piece.color:
                        moves.append((new_x, new_y))

        # 士的移动规则（对角线一格）
        elif piece.piece_type == '士':
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < BOARD_SIZE and 0 <= new_y < BOARD_SIZE:
                    if self.is_position_empty((new_x, new_y)) or self.board[new_y][new_x].color != piece.color:
                        moves.append((new_x, new_y))

        # 象的移动规则（田字）
        elif piece.piece_type == '象':
            for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                new_x, new_y = x + dx, y + dy
                # 检查象眼是否被堵
                block_x, block_y = x + dx // 2, y + dy // 2
                if (0 <= new_x < BOARD_SIZE and 0 <= new_y < BOARD_SIZE and
                    (self.is_position_empty((new_x, new_y)) or
                     self.board[new_y][new_x].color != piece.color) and
                    self.is_position_empty((block_x, block_y))):
                    moves.append((new_x, new_y))

        # 马的移动规则（日字）
        elif piece.piece_type == '马':
            for dx, dy in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
                new_x, new_y = x + dx, y + dy
                # 检查马腿是否被堵
                block_x, block_y = x + dx // 2, y + dy // 2
                if (0 <= new_x < BOARD_SIZE and 0 <= new_y < BOARD_SIZE and
                    (self.is_position_empty((new_x, new_y)) or
                     self.board[new_y][new_x].color != piece.color) and
                    self.is_position_empty((block_x, block_y))):
                    moves.append((new_x, new_y))

        # 炮的移动规则（直线移动，吃子需跳棋）
        elif piece.piece_type == '炮':
            # 向右移动
            obstacle = False
            for dx in range(1, BOARD_SIZE - x):
                target = (x + dx, y)
                if not self.is_position_empty(target):
                    if not obstacle:
                        obstacle = True
                    else:
                        # 遇到第二个棋子，如果是敌方则可以吃
                        if self.board[y][x + dx].color != piece.color:
                            moves.append(target)
                        break
                elif not obstacle:  # 无障碍物时可以直接移动
                    moves.append(target)

            # 向左移动
            obstacle = False
            for dx in range(1, x + 1):
                target = (x - dx, y)
                if not self.is_position_empty(target):
                    if not obstacle:
                        obstacle = True
                    else:
                        if self.board[y][x - dx].color != piece.color:
                            moves.append(target)
                        break
                elif not obstacle:
                    moves.append(target)

            # 向下移动
            obstacle = False
            for dy in range(1, BOARD_SIZE - y):
                target = (x, y + dy)
                if not self.is_position_empty(target):
                    if not obstacle:
                        obstacle = True
                    else:
                        if self.board[y + dy][x].color != piece.color:
                            moves.append(target)
                        break
                elif not obstacle:
                    moves.append(target)

            # 向上移动
            obstacle = False
            for dy in range(1, y + 1):
                target = (x, y - dy)
                if not self.is_position_empty(target):
                    if not obstacle:
                        obstacle = True
                    else:
                        if self.board[y - dy][x].color != piece.color:
                            moves.append(target)
                        break
                elif not obstacle:
                    moves.append(target)

        # 将的移动规则（横竖一格）
        elif piece.piece_type == '将':
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < BOARD_SIZE and 0 <= new_y < BOARD_SIZE:
                    if self.is_position_empty((new_x, new_y)) or self.board[new_y][new_x].color != piece.color:
                        moves.append((new_x, new_y))

        return moves

    def move_piece(self, piece, new_position):
        """移动棋子到新位置"""
        old_x, old_y = piece.position
        new_x, new_y = new_position

        if self.turn == 'red':
            self.super_move = False

        # 检查是否吃子
        target_piece = self.board[new_y][new_x]
        if target_piece:
            print(target_piece.piece_type)
            if target_piece.color == 'red':
                # self.red_piece.remove(target_piece)
                self.game_over = True
                self.winner = 'black'
                # # 检查是否红车被吃

            else:
                if target_piece.piece_type == '将':
                    self.super_move = True
                self.black_pieces.remove(target_piece)

        # 更新棋盘
        self.board[old_y][old_x] = None
        self.board[new_y][new_x] = piece
        piece.position = (new_x, new_y)
        piece.selected = False

        # 切换回合
        self.turn = 'black' if self.turn == 'red' else 'red'

    def is_red_rook_threatened(self):
        """检查红车是否被任意黑棋威胁"""

        rook_x, rook_y = self.red_piece.position

        for piece in self.black_pieces:
            if piece.position == (rook_x, rook_y):
                continue

            valid_moves = self.get_valid_moves(piece)
            if (rook_x, rook_y) in valid_moves:
                return True
        return False

    def handle_click(self, position):
        """处理鼠标点击"""
        if self.game_over:
            return

        grid_x, grid_y = position[0] // GRID_SIZE, (position[1] - 100) // GRID_SIZE

        # 确保点击在棋盘范围内
        if 0 <= grid_x < BOARD_SIZE and 0 <= grid_y < BOARD_SIZE:
            clicked_piece = self.board[grid_y][grid_x]

            # 玩家回合（红方）
            if self.turn == 'red':
                # 如果点击了自己的棋子
                if clicked_piece and clicked_piece.color == 'red':
                    # 取消之前的选择
                    if self.selected_piece:
                        self.selected_piece.selected = False

                    # 选择新棋子
                    clicked_piece.selected = True
                    self.selected_piece = clicked_piece

                # 如果点击了空位置或敌方棋子，且有选中的棋子
                elif self.selected_piece:
                    # 获取合法移动
                    valid_moves = self.get_valid_moves(self.selected_piece)

                    # 如果点击位置是合法移动
                    if (grid_x, grid_y) in valid_moves:

                        # 吃掉将后第二回合是超级移动，横竖通杀
                        super_move = True if self.super_move else False

                        self.move_piece(self.selected_piece, (grid_x, grid_y))
                        self.selected_piece = None
                        if super_move:
                            x_pos, y_pos = self.red_piece.position
                            for black_piece in copy(self.black_pieces):
                                black_x_pos, black_y_pos = black_piece.position
                                if black_x_pos == x_pos or black_y_pos == y_pos:
                                    if black_piece.piece_type == '将':
                                        self.super_move = True
                                    self.black_pieces.remove(self.board[black_y_pos][black_x_pos])
                                    self.board[black_y_pos][black_x_pos] = None

                        # 检查红车是否被威胁
                        if self.is_red_rook_threatened():
                            self.game_over = True
                            self.winner = 'black'

                        # 切换到AI回合
                        if not self.game_over:
                            self.ai_move()

    def ai_move(self):
        """AI移动（系统控制的黑棋）优先躲避威胁"""

        # if self.round_count == RED_WINNER_ROUND:  # 暂定两百关通关
        #     self.game_over = True
        #     self.winner = 'red'

        # 1. 优先处理被威胁的黑棋
        threatened_pieces = []
        for piece in self.black_pieces:
            # 检查红车是否能吃这个棋子

            valid_moves = self.get_valid_moves(self.red_piece)
            if piece.position in valid_moves:  # 棋子位置在红车的移动路线上
                threatened_pieces.append(piece)
                break

        # 尝试移动被威胁的棋子
        moved = False
        if threatened_pieces:
            random.shuffle(threatened_pieces)

            red_moves = self.positions_threatened_by_red_piece(self.red_piece)
            for piece in threatened_pieces:
                valid_moves = self.get_valid_moves(piece)  # 获取被威胁棋子的所有移动位置
                safe_moves = []
                # 寻找安全移动（不被红车攻击）
                for move in valid_moves:
                    if move in red_moves:
                        continue
                    else:
                        safe_moves.append(move)
                # 优先选择安全移动，如果没有安全移动则随机选择
                if safe_moves:
                    new_position = random.choice(safe_moves)
                elif valid_moves:
                    new_position = random.choice(valid_moves)
                else:
                    continue

                self.move_piece(piece, new_position)
                moved = True
                break

        # 2. 如果没有被威胁的棋子或无法移动被威胁的棋子，随机移动其他棋子
        if not moved:
            movable_pieces = [p for p in self.black_pieces if p not in threatened_pieces]
            if not movable_pieces:
                movable_pieces = self.black_pieces

            random.shuffle(movable_pieces)
            for piece in movable_pieces:
                # 不往红棋可以吃的位置移动
                valid_moves = set(self.get_valid_moves(piece)) - set(self.get_valid_moves(self.red_piece))
                if valid_moves:
                    new_position = random.choice(list(valid_moves))
                    self.move_piece(piece, new_position)
                    moved = True
                    break

        # 3. 如果没有任何棋子可以移动，直接切换回合
        if not moved:
            self.turn = 'red'

        self.round_count += 1  # 回合数加1
        self.control_refresh()
        # 检查是否需要添加新棋子（每3回合）
        if self.round_count % self.piece_appearance_interval == 0:
            self.appearance_count += 1
            # 第十次新增优先出将
            pygame.time.delay(100)
            if self.appearance_count % 10 == 0:
                self.add_general_with_guards()
            else:
                for piece_type in self.occur_pieces:
                    self.add_black_piece(piece_type)

    def show_game_over_dialog(self):
        """显示透明游戏结束对话框"""
        # 创建带透明通道的 Surface
        dialog_surface = pygame.Surface((300, 160), pygame.SRCALPHA)  # SRCALPHA 标志启用透明通道[1z](@ref)
        dialog_rect = dialog_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        # 绘制半透明对话框背景
        pygame.draw.rect(dialog_surface, (*DIALOG_BG_COLOR, 180), dialog_surface.get_rect())  # 180 是透明度值[7](@ref)
        pygame.draw.rect(dialog_surface, (0, 0, 0, 255), dialog_surface.get_rect(), 2)  # 黑色边框

        # 添加文本
        font = pygame.font.SysFont(None, 36)
        text = font.render("Game Over", True, (255, 0, 0))
        dialog_surface.blit(text, (100, 20))

        winner_text = font.render(f"Winner: {'System' if self.winner == 'black' else 'Player'}", True, (0, 0, 0))
        dialog_surface.blit(winner_text, (60, 60))

        # 添加按钮
        restart_btn = pygame.Rect(30, 110, 100, 30)
        quit_btn = pygame.Rect(170, 110, 100, 30)

        pygame.draw.rect(dialog_surface, (0, 200, 0, 255), restart_btn)  # 按钮完全不透明
        pygame.draw.rect(dialog_surface, (200, 0, 0, 255), quit_btn)

        font = pygame.font.SysFont(None, 24)
        restart_text = font.render("Restart", True, (255, 255, 255))
        quit_text = font.render("Quit", True, (255, 255, 255))
        dialog_surface.blit(restart_text, (restart_btn.x + 15, restart_btn.y + 5))
        dialog_surface.blit(quit_text, (quit_btn.x + 30, quit_btn.y + 5))

        # 将对话框Surface绘制到主屏幕上
        screen.blit(dialog_surface, dialog_rect.topleft)

        # 返回按钮位置（需要调整坐标）
        return pygame.Rect(dialog_rect.x + 30, dialog_rect.y + 110, 100, 30), \
            pygame.Rect(dialog_rect.x + 170, dialog_rect.y + 110, 100, 30)

    def draw_chess_board_pieces(self, surface):
        """绘制棋盘和棋子"""
        # 绘制信息栏
        info_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 100)
        pygame.draw.rect(surface, INFO_BG_COLOR, info_rect)

        # 绘制棋盘背景
        pygame.draw.rect(surface, BACKGROUND_COLOR, (0, 100, WINDOW_WIDTH, WINDOW_HEIGHT - 100))

        # 绘制网格线（确保不超出棋盘边界）
        for i in range(BOARD_SIZE):
            # 横线（从第1格中心到倒数第1格中心）
            pygame.draw.line(surface, LINE_COLOR,
                             (GRID_SIZE // 2, i * GRID_SIZE + GRID_SIZE // 2 + 100),
                             (WINDOW_WIDTH - GRID_SIZE // 2, i * GRID_SIZE + GRID_SIZE // 2 + 100), 2)

            # 竖线（从第1格中心到倒数第1格中心）
            pygame.draw.line(surface, LINE_COLOR,
                             (i * GRID_SIZE + GRID_SIZE // 2, 100 + GRID_SIZE // 2),
                             (i * GRID_SIZE + GRID_SIZE // 2, WINDOW_HEIGHT - GRID_SIZE // 2), 2)

        # 绘制棋子（偏移100像素）
        for row in self.board:
            for piece in row:
                if piece:
                    piece.draw(surface, 100)

        # 显示回合信息
        font = pygame.font.SysFont(None, 24)
        turn_text = f"Round: {self.round_count} | {'Player turn (Red)' if self.turn == 'red' else 'System turn (Black)'}"
        text_surface = font.render(turn_text, True, (0, 0, 0))
        surface.blit(text_surface, (10, 10))

        # 显示下一个将出现的棋子
        rounds_left = self.piece_appearance_interval - (self.round_count % self.piece_appearance_interval)

        next_pieces = ','.join([self.piece_sequence_en[i] for i in self.occur_pieces])
        next_text = f"Next piece: {next_pieces} (in {rounds_left} rounds)"
        next_surface = font.render(next_text, True, (0, 0, 0))
        surface.blit(next_surface, (10, 40))

        # 显示新增棋子次数
        count_text = f"Appearance count: {self.appearance_count}"
        count_surface = font.render(count_text, True, (0, 0, 0))
        surface.blit(count_surface, (10, 70))


def main():
    # 创建游戏实例
    game = ChessGame()
    pygame.mixer.music.load("vedio/im_dead.wav")
    # dead_sound = pygame.mixer.Sound("vedio/im_dead.wav")
    # 游戏主循环
    clock = pygame.time.Clock()
    running = True
    restart_btn = None
    quit_btn = None

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    if game.game_over and restart_btn and quit_btn:
                        if restart_btn.collidepoint(event.pos):
                            game = ChessGame()  # 重新开始游戏
                        elif quit_btn.collidepoint(event.pos):
                            running = False
                    else:
                        game.handle_click(event.pos)

        # 绘制游戏
        screen.fill((0, 0, 0))
        game.draw_chess_board_pieces(screen)

        # 如果游戏结束，显示对话框
        if game.game_over:
            if not hasattr(game, 'death_sound_played'):
                pygame.mixer.music.play()
                game.death_sound_played = True
            restart_btn, quit_btn = game.show_game_over_dialog()

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
