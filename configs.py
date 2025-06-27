
"""主程序"""
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


"""登录注册"""

LOGIN_STATE = 0
REGISTER_STATE = 1
GAME_STATE = 2
GAME_OVER_STATE = 3


"""棋子积分"""

PIECES_SCORE = {
    '卒': 10,
    '士': 20,
    '象': 20,
    '马': 30,
    '炮': 30,
    '车': 40,
    '将': 50,
}

UPLOAD_SCORE = "http://127.0.0.1:80/rank/"
LOGIN_URL = 'http://127.0.0.1:80/user/login/'
REGISTER_URL = 'http://127.0.0.1:80/user/register/'

MINIMUM_PASSWD_LEN = 4
MAXIMUM_PASSWD_LEN = 12


