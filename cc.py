"""
作者：it專案例項網
網址：www.itprojects.cn
"""

import sys

import pygame

# 要顯示的視窗的寬、高
WIDTH, HEIGHT = 750, 667


class ClickBox(pygame.sprite.Sprite):
    """
    選中棋子物件
    """
    singleton = None

    def __new__(cls, *args, **kwargs):
        if cls.singleton is None:
            cls.singleton = super().__new__(cls)
        return cls.singleton

    def __init__(self, screen, row, col, team):
        super().__init__()
        self.image = pygame.image.load("images/r_box.png")
        self.rect = self.image.get_rect()
        self.row, self.col = row, col
        self.rect.topleft = (50 + self.col * 57, 50 + self.row * 57)
        self.screen = screen
        self.team = team

    @classmethod
    def show(cls):
        if cls.singleton:
            cls.singleton.screen.blit(cls.singleton.image, cls.singleton.rect)

    @classmethod
    def clean(cls):
        """
        清理上次的物件
        """
        cls.singleton = None


class Dot(pygame.sprite.Sprite):
    """
    可落棋子類
    """
    group = list()

    def __init__(self, screen, position):
        super().__init__()
        self.image = pygame.image.load("images/dot2.png")
        self.rect = self.image.get_rect()
        self.row, self.col = position  # 將元組拆包
        self.rect.topleft = (60 + self.col * 57, 60 + self.row * 57)
        self.group.append(self)
        self.screen = screen

    @classmethod
    def show(cls):
        for dot in cls.group:
            dot.screen.blit(dot.image, dot.rect)

    @classmethod
    def clean_last_postion(cls):
        """
        清除上次落子位置
        """
        cls.group.clear()

    @classmethod
    def click(cls):
        """
        點選棋子
        """
        for dot in cls.group:
            if pygame.mouse.get_pressed()[0] and dot.rect.collidepoint(pygame.mouse.get_pos()):
                print("被點選了「可落子」物件")
                return dot


class Chess(pygame.sprite.Sprite):
    """
    棋子類
    """

    def __init__(self, screen, chess_name, row, col):
        self.screen = screen
        self.image = pygame.image.load("images/" + chess_name + ".png")
        self.rect = self.image.get_rect()
        self.rect.topleft = (50 + col * 57, 50 + row * 57)
        self.team = chess_name[0]  # 隊伍（紅方 r、黑方b）
        self.name = chess_name[2]  # 名字（炮p、馬m等）
        self.row = row
        self.col = col

    def show(self):
        self.screen.blit(self.image, self.rect)

    @staticmethod
    def click(player, chesses):
        """
        點選棋子
        """
        for chess in chesses:
            if pygame.mouse.get_pressed()[0] and chess.rect.collidepoint(pygame.mouse.get_pos()):
                if player == chess.team:
                    print("被點選了")
                    return chess

    def update_postion(self, new_row, new_col):
        """
        更新要顯示的圖片的座標
        """
        self.row = new_row
        self.col = new_col
        self.rect.topleft = (50 + new_col * 57, 50 + new_row * 57)


class ChessBoard(object):
    """
    棋盤類
    """

    def __init__(self, screen):
        self.screen = screen
        self.image = pygame.image.load("images/bg.png")
        self.topleft = (50, 50)
        self.__create_default_chess()

    def __create_default_chess(self):
        """
        建立預設棋子
        """
        self.map = [
            ["b_c", "b_m", "b_x", "b_s", "b_j", "b_s", "b_x", "b_m", "b_c"],
            ["", "", "", "", "", "", "", "", ""],
            ["", "b_p", "", "", "", "", "", "b_p", ""],
            ["b_z", "", "b_z", "", "b_z", "", "b_z", "", "b_z"],
            ["", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", ""],
            ["r_z", "", "r_z", "", "r_z", "", "r_z", "", "r_z"],
            ["", "r_p", "", "", "", "", "", "r_p", ""],
            ["", "", "", "", "", "", "", "", ""],
            ["r_c", "r_m", "r_x", "r_s", "r_j", "r_s", "r_x", "r_m", "r_c"],
        ]
        for row, line in enumerate(self.map):
            for col, chess_name in enumerate(line):
                if chess_name:
                    # 將建立的棋子新增到屬性map中
                    self.map[row][col] = Chess(self.screen, chess_name, row, col)
                else:
                    self.map[row][col] = None

    def show(self):
        # 顯示棋盤
        self.screen.blit(self.image, self.topleft)
        # 顯示棋盤上的所有棋子
        for line_chess in self.map:
            for chess in line_chess:
                if chess:
                    chess.show()

    def get_put_down_postion(self, clicked_chess):
        """
        計算當前棋子可以移動的位置
        """
        # 儲存當前棋子可以落子的位置
        all_position = list()
        # 拿到當前棋子的行、列
        row, col = clicked_chess.row, clicked_chess.col
        # 拿到當前棋子的team，即時紅方r還是黑方b
        team = clicked_chess.team

        # 計算當前選中棋子的所有可以落子位置
        if clicked_chess.name == "p":  # 炮
            # 一行
            direction_left_chess_num = 0
            direction_right_chess_num = 0
            for i in range(1, 9):
                # 計算當前行中，棋子左邊與右邊可以落子的位置
                # 左邊位置沒有越界
                if direction_left_chess_num >= 0 and col - i >= 0:
                    if not self.map[row][col - i] and direction_left_chess_num == 0:
                        # 如果沒有棋子,則將當前位置組成一個元組，新增到列表
                        all_position.append((row, col - i))
                    elif self.map[row][col - i]:
                        # 如果當前位置有棋子，那麼就判斷是否能夠吃掉它
                        direction_left_chess_num += 1
                        if direction_left_chess_num == 2 and self.map[row][col - i].team != team:
                            all_position.append((row, col - i))
                            direction_left_chess_num = -1  # 讓其不能夠在下次for迴圈時再次判斷
                # 右邊位置沒有越界
                if direction_right_chess_num >= 0 and col + i <= 8:
                    if not self.map[row][col + i] and direction_right_chess_num == 0:
                        # 如果沒有棋子,則將當前位置組成一個元組，新增到列表
                        all_position.append((row, col + i))
                    elif self.map[row][col + i]:
                        # 如果當前位置有棋子，那麼就判斷是否能夠吃掉它
                        direction_right_chess_num += 1
                        if direction_right_chess_num == 2 and self.map[row][col + i].team != team:
                            all_position.append((row, col + i))
                            direction_right_chess_num = -1
            # 一列
            direction_up_chess_num = 0
            direction_down_chess_num = 0
            for i in range(1, 10):  # 這樣就讓i從1開始，而不是從0
                # 計算當前列中，棋子上邊與下邊可以落子的位置
                # 上邊位置沒有越界
                if direction_up_chess_num >= 0 and row - i >= 0:
                    if not self.map[row - i][col] and direction_up_chess_num == 0:
                        # 如果沒有棋子,則將當前位置組成一個元組，新增到列表
                        all_position.append((row - i, col))
                    elif self.map[row - i][col]:
                        # 如果當前位置有棋子，那麼就判斷是否能夠吃掉它
                        direction_up_chess_num += 1
                        if direction_up_chess_num == 2 and self.map[row - i][col].team != team:
                            all_position.append((row - i, col))
                            direction_up_chess_num = -1

                # 下邊位置沒有越界
                if direction_down_chess_num >= 0 and row + i <= 9:
                    if not self.map[row + i][col] and direction_down_chess_num == 0:
                        # 如果沒有棋子,則將當前位置組成一個元組，新增到列表
                        all_position.append((row + i, col))
                    elif self.map[row + i][col]:
                        # 如果當前位置有棋子，那麼就判斷是否能夠吃掉它
                        direction_down_chess_num += 1
                        if direction_down_chess_num == 2 and self.map[row + i][col].team != team:
                            all_position.append((row + i, col))
                            direction_down_chess_num = -1
        elif clicked_chess.name == "z":  # 卒
            if team == "r":  # 紅方
                if row - 1 >= 0:  # 只能向上移動
                    if not self.map[row - 1][col] or self.map[row - 1][col].team != team:
                        all_position.append((row - 1, col))
            else:  # 黑方
                if row + 1 <= 9:  # 只能向下移動
                    if not self.map[row + 1][col] or self.map[row + 1][col].team != team:
                        all_position.append((row + 1, col))
            # 左右判斷
            if (team == "r" and 0 <= row <= 4) or (team == "b" and 5 <= row <= 9):  # 左、右一步
                # 左
                if col - 1 >= 0 and (not self.map[row][col - 1] or self.map[row][col - 1].team != team):
                    all_position.append((row, col - 1))
                # 右
                if col + 1 <= 8 and (not self.map[row][col + 1] or self.map[row][col + 1].team != team):
                    all_position.append((row, col + 1))
        elif clicked_chess.name == "c":  # 車
            # 一行
            left_stop = False
            right_stop = False
            for i in range(1, 9):
                # 左邊位置沒有越界且沒有遇到任何一個棋子
                if not left_stop and col - i >= 0:
                    if not self.map[row][col - i]:
                        # 如果沒有棋子,則將當前位置組成一個元組，新增到列表
                        all_position.append((row, col - i))
                    else:
                        left_stop = True
                        if self.map[row][col - i].team != team:
                            # 如果當前位置有棋子，那麼就判斷是否能夠吃掉它
                            all_position.append((row, col - i))
                # 右邊位置沒有越界且沒有遇到任何一個棋子
                if not right_stop and col + i <= 8:
                    if not self.map[row][col + i]:
                        # 如果沒有棋子,則將當前位置組成一個元組，新增到列表
                        all_position.append((row, col + i))
                    else:
                        right_stop = True
                        if self.map[row][col + i].team != team:
                            # 如果當前位置有棋子，那麼就判斷是否能夠吃掉它
                            all_position.append((row, col + i))

            # 一列
            up_stop = False
            down_stoop = False
            for i in range(1, 10):
                # 上邊位置沒有越界且沒有遇到任何一個棋子
                if not up_stop and row - i >= 0:
                    if not self.map[row - i][col]:
                        # 如果沒有棋子,則將當前位置組成一個元組，新增到列表
                        all_position.append((row - i, col))
                    else:
                        up_stop = True
                        if self.map[row - i][col].team != team:
                            # 如果當前位置有棋子，那麼就判斷是否能夠吃掉它
                            all_position.append((row - i, col))
                # 下邊位置沒有越界且沒有遇到任何一個棋子
                if not down_stoop and row + i <= 9:
                    if not self.map[row + i][col]:
                        # 如果沒有棋子,則將當前位置組成一個元組，新增到列表
                        all_position.append((row + i, col))
                    else:
                        down_stoop = True
                        if self.map[row + i][col].team != team:
                            # 如果當前位置有棋子，那麼就判斷是否能夠吃掉它
                            all_position.append((row + i, col))
        elif clicked_chess.name == "m":  # 馬
            # 需要判斷的是4個方向，每個方向對應2個位置
            # 上方
            if row - 1 >= 0 and not self.map[row - 1][col]:  # 如果當前棋子沒有被蹩馬腿，那麼再對這個方向的2個位置進行判斷
                # 左上
                if row - 2 >= 0 and col - 1 >= 0 and (not self.map[row - 2][col - 1] or self.map[row - 2][col - 1].team != team):
                    all_position.append((row - 2, col - 1))
                # 右上
                if row - 2 >= 0 and col + 1 <= 8 and (not self.map[row - 2][col + 1] or self.map[row - 2][col + 1].team != team):
                    all_position.append((row - 2, col + 1))
            # 下方
            if row + 1 <= 9 and not self.map[row + 1][col]:  # 如果當前棋子沒有被蹩馬腿，那麼再對這個方向的2個位置進行判斷
                # 左下
                if row + 2 >= 0 and col - 1 >= 0 and (not self.map[row + 2][col - 1] or self.map[row + 2][col - 1].team != team):
                    all_position.append((row + 2, col - 1))
                # 右下
                if row + 2 >= 0 and col + 1 <= 8 and (not self.map[row + 2][col + 1] or self.map[row + 2][col + 1].team != team):
                    all_position.append((row + 2, col + 1))
            # 左方
            if col - 1 >= 0 and not self.map[row][col - 1]:  # 如果當前棋子沒有被蹩馬腿，那麼再對這個方向的2個位置進行判斷
                # 左上2（因為有左上了，暫且稱為左上2吧）
                if row - 1 >= 0 and col - 2 >= 0 and (not self.map[row - 1][col - 2] or self.map[row - 1][col - 2].team != team):
                    all_position.append((row - 1, col - 2))
                # 左下2
                if row + 1 <= 9 and col - 2 >= 0 and (not self.map[row + 1][col - 2] or self.map[row + 1][col - 2].team != team):
                    all_position.append((row + 1, col - 2))
            # 右方
            if col + 1 <= 8 and not self.map[row][col + 1]:  # 如果當前棋子沒有被蹩馬腿，那麼再對這個方向的2個位置進行判斷
                # 右上2（因為有右上了，暫且稱為右上2吧）
                if row - 1 >= 0 and col + 2 <= 8 and (not self.map[row - 1][col + 2] or self.map[row - 1][col + 2].team != team):
                    all_position.append((row - 1, col + 2))
                # 右下2
                if row + 1 <= 9 and col + 2 <= 8 and (not self.map[row + 1][col + 2] or self.map[row + 1][col + 2].team != team):
                    all_position.append((row + 1, col + 2))
        elif clicked_chess.name == "x":  # 象
            # 因為象是不能過河的，所以要計算出它們可以移動的行的範圍
            row_start, row_stop = (0, 4) if team == "b" else (5, 9)
            # 有4個方向的判斷(沒有越界，且沒有蹩象腿)
            if row - 2 >= row_start and col - 2 >= 0 and not self.map[row - 1][col - 1]:  # 左上
                if not self.map[row - 2][col - 2] or self.map[row - 2][col - 2].team != team:
                    all_position.append((row - 2, col - 2))
            if row - 2 >= row_start and col + 2 <= 8 and not self.map[row - 1][col + 1]:  # 右上
                if not self.map[row - 2][col + 2] or self.map[row - 2][col + 2].team != team:
                    all_position.append((row - 2, col + 2))
            if row + 2 <= row_stop and col - 2 >= 0 and not self.map[row + 1][col - 1]:  # 左下
                if not self.map[row + 2][col - 2] or self.map[row + 2][col - 2].team != team:
                    all_position.append((row + 2, col - 2))
            if row + 2 <= row_stop and col + 2 <= 8 and not self.map[row + 1][col + 1]:  # 右下
                if not self.map[row + 2][col + 2] or self.map[row + 2][col + 2].team != team:
                    all_position.append((row + 2, col + 2))
        elif clicked_chess.name == "s":  # 士
            # 因為士是不能過河的，所以要計算出它們可以移動的行的範圍
            row_start, row_stop = (0, 2) if team == "b" else (7, 9)
            if row - 1 >= row_start and col - 1 >= 3 and (not self.map[row - 1][col - 1] or self.map[row - 1][col - 1].team != team):
                all_position.append((row - 1, col - 1))
            if row - 1 >= row_start and col + 1 <= 5 and (not self.map[row - 1][col + 1] or self.map[row - 1][col + 1].team != team):
                all_position.append((row - 1, col + 1))
            if row + 1 <= row_stop and col - 1 >= 3 and (not self.map[row + 1][col - 1] or self.map[row + 1][col - 1].team != team):
                all_position.append((row + 1, col - 1))
            if row + 1 <= row_stop and col + 1 <= 5 and (not self.map[row + 1][col + 1] or self.map[row + 1][col + 1].team != team):
                all_position.append((row + 1, col + 1))
        elif clicked_chess.name == "j":  # 將
            # 因為"將"是不能過河的，所以要計算出它們可以移動的行的範圍
            row_start, row_stop = (0, 2) if team == "b" else (7, 9)
            # 有4個方向的判斷
            if row - 1 >= row_start and (not self.map[row - 1][col] or self.map[row - 1][col].team != team):
                all_position.append((row - 1, col))
            if row + 1 <= row_stop and (not self.map[row + 1][col] or self.map[row + 1][col].team != team):
                all_position.append((row + 1, col))
            if col - 1 >= 3 and (not self.map[row][col - 1] or self.map[row][col - 1].team != team):
                all_position.append((row, col - 1))
            if col + 1 <= 5 and (not self.map[row][col + 1] or self.map[row][col + 1].team != team):
                all_position.append((row, col + 1))

        all_position = self.judge_delete_position(all_position, clicked_chess)

        # 返回可以落子的所有位置
        return all_position

    def judge_delete_position(self, all_position, clicked_chess):
        """
        刪除被"將軍"的位置
        """
        # 定義要刪除的列表
        deleting_position = list()

        # 判斷這些位置，是否會導致被"將軍"，如果是則從列表中刪除這個位置
        for row, col in all_position:
            # 1. 備份
            # 備份當前棋子位置
            old_row, old_col = clicked_chess.row, clicked_chess.col
            # 備份要落子的位置的棋子(如果沒有，則為None)
            position_chess_backup = self.map[row][col]
            # 2. 挪動位置
            # 移動位置
            self.map[row][col] = self.map[old_row][old_col]
            # 修改棋子的屬性
            self.map[row][col].update_postion(row, col)
            # 清楚之前位置為None
            self.map[old_row][old_col] = None
            # 3. 判斷對方是否可以發起"將軍"
            if self.judge_attack_general("b" if clicked_chess.team == "r" else "r"):
                deleting_position.append((row, col))
            # 4. 恢復到之前位置
            self.map[old_row][old_col] = self.map[row][col]
            self.map[old_row][old_col].update_postion(old_row, old_col)
            self.map[row][col] = position_chess_backup

        # 5. 刪除不能落子的位置
        all_position = list(set(all_position) - set(deleting_position))

        return all_position

    def move_chess(self, new_row, new_col):
        """
        落子
        """
        # 得到要移動的棋子的位置
        old_row, old_col = ClickBox.singleton.row, ClickBox.singleton.col
        print("舊位置：", old_row, old_col, "新位置：", new_row, new_col)
        # 移動位置
        self.map[new_row][new_col] = self.map[old_row][old_col]
        # 修改棋子的屬性
        self.map[new_row][new_col].update_postion(new_row, new_col)
        # 清楚之前位置為None
        self.map[old_row][old_col] = None

    def judge_attack_general(self, attact_player):
        """
        判斷 attact_player方是否 將對方的軍
        """
        # 1. 找到對方"將"的位置
        general_player = "r" if attact_player == "b" else "b"
        general_position = self.get_general_position(general_player)

        # 2. 遍歷我方所有的棋子
        for row, line in enumerate(self.map):
            for col, chess in enumerate(line):
                if chess and chess.team == attact_player:
                    if chess.name == "z":  # 兵
                        # 傳遞5個引數（攻擊方的標識，攻擊方row，攻擊方col，對方將row，對方將col）
                        if self.judge_z_attack(chess.team, chess.row, chess.col, *general_position):
                            return True
                    elif chess.name == "p":  # 炮
                        if self.judge_c_and_p_attack(chess.name, chess.row, chess.col, *general_position):
                            return True
                    elif chess.name == "c":  # 車
                        if self.judge_c_and_p_attack(chess.name, chess.row, chess.col, *general_position):
                            return True
                    elif chess.name == "m":  # 馬
                        if self.judge_m_attack(chess.row, chess.col, *general_position):
                            return True
                    elif chess.name == "x":  # 象
                        pass
                    elif chess.name == "s":  # 士
                        pass
                    elif chess.name == "j":  # 將
                        if self.judge_j_attack(chess.row, chess.col, *general_position):
                            return True

    def judge_j_attack(self, attack_row, attack_col, general_row, general_col):
        """
        判斷 兩個將是否相對
        """
        if attack_col == general_col:
            # 在同一列
            min_row, max_row = (attack_row, general_row) if attack_row < general_row else (general_row, attack_row)

            chess_num = 0
            for i in range(min_row + 1, max_row):
                if self.map[i][general_col]:
                    chess_num += 1
            if chess_num == 0:
                return True

    def judge_m_attack(self, attack_row, attack_col, general_row, general_col):
        """
        判斷馬是否攻擊到"將"
        """
        if attack_row == general_row or attack_col == general_col:
            return False
        else:
            # "馬走日"，利用這個特點會得出，如果此馬能夠攻擊到"將"，那麼兩條邊的平方和一定是5
            col_length = (attack_col - general_col) ** 2
            row_length = (attack_row - general_row) ** 2
            if col_length + row_length == 5:
                # 判斷是否蹩馬腿
                if col_length == 1:
                    if general_row < attack_row and not self.map[attack_row - 1][attack_col]:
                        return True
                    elif general_row > attack_row and not self.map[attack_row + 1][attack_col]:
                        return True
                elif col_length == 4:
                    if general_col < attack_col and not self.map[attack_row][attack_col - 1]:
                        return True
                    elif general_col > attack_col and not self.map[attack_row][attack_col + 1]:
                        return True

    def judge_c_and_p_attack(self, attack_chess_name, attack_row, attack_col, general_row, general_col):
        """
        判斷"車"、"炮"能否攻擊到對方"將"
        """
        check_chess_num = 1 if attack_chess_name == "p" else 0
        chess_num = 0
        if attack_row == general_row:
            # 在同一行
            min_col, max_col = (attack_col, general_col) if attack_col < general_col else (general_col, attack_col)
            for i in range(min_col + 1, max_col):
                if self.map[attack_row][i]:
                    chess_num += 1
            if chess_num == check_chess_num:
                return True
        elif attack_col == general_col:
            # 在同一列
            min_row, max_row = (attack_row, general_row) if attack_row < general_row else (general_row, attack_row)
            for i in range(min_row + 1, max_row):
                if self.map[i][general_col]:
                    chess_num += 1
            if chess_num == check_chess_num:
                return True

    def judge_z_attack(self, attack_team, attack_row, attack_col, general_row, general_col):
        """
        判斷卒是否攻擊到"將"
        """
        if attack_team == "r" and attack_row < general_row:
            return False
        elif attack_team == "b" and attack_row > general_row:
            return False
        elif (attack_row - general_row) ** 2 + (attack_col - general_col) ** 2 == 1:
            return True

    def get_general_position(self, general_player):
        """
        找到general_player標記的一方的將的位置
        """
        for row, line in enumerate(self.map):
            for col, chess in enumerate(line):
                if chess and chess.team == general_player and chess.name == "j":
                    return chess.row, chess.col

    def judge_win(self, attack_player):
        """
        判斷是否獲勝
        """
        # 依次判斷是否被攻擊方的所有棋子，是否有阻擋攻擊的可能
        for line_chesses in self.map:
            for chess in line_chesses:
                if chess and chess.team != attack_player:
                    move_position_list = self.get_put_down_postion(chess)
                    if move_position_list:  # 只要找到一個可以移動的位置，就表示沒有失敗，還是有機會的
                        return False

        return True


class Game(object):
    """
    遊戲類
    """

    def __init__(self, screen):
        self.screen = screen
        self.player = "r"  # 預設走棋的為紅方r
        self.player_tips_r_image = pygame.image.load("images/red.png")
        self.player_tips_r_image_topleft = (550, 500)
        self.player_tips_b_image = pygame.image.load("images/black.png")
        self.player_tips_b_image_topleft = (550, 100)
        self.show_attack = False
        self.show_attack_count = 0
        self.show_attack_time = 100
        self.attack_img = pygame.image.load("images/pk.png")
        self.show_win = False
        self.win_img = pygame.image.load("images/win.png")
        self.win_player = None

    def get_player(self):
        """
        獲取當前走棋方
        """
        return self.player

    def exchange(self):
        """
        交換走棋方
        """
        self.player = "r" if self.player == "b" else "b"
        return self.get_player()

    def show(self):
        if self.show_win:
            if self.win_player == "b":
                self.screen.blit(self.win_img, (550, 100))
            else:
                self.screen.blit(self.win_img, (550, 450))
            return

        # 通過計時，實現顯示一會"將軍"之後，就消失
        if self.show_attack:
            self.show_attack_count += 1
            if self.show_attack_count == self.show_attack_time:
                self.show_attack_count = 0
                self.show_attack = False

        if self.player == "r":
            self.screen.blit(self.player_tips_r_image, self.player_tips_r_image_topleft)
            # 顯示"將軍"效果
            if self.show_attack:
                self.screen.blit(self.attack_img, (230, 400))
        else:
            self.screen.blit(self.player_tips_b_image, self.player_tips_b_image_topleft)
            # 顯示"將軍"效果
            if self.show_attack:
                self.screen.blit(self.attack_img, (230, 100))

    def set_attack(self):
        """
        標記"將軍"效果
        """
        self.show_attack = True

    def set_win(self, win_player):
        """
        設定獲勝方
        """
        self.show_win = True
        self.win_player = win_player


def main():
    # 初始化pygame
    pygame.init()
    # 建立用來顯示畫面的物件（理解為相框）
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    # 遊戲背景圖片
    background_img = pygame.image.load("images/bg.jpg")
    # 建立遊戲物件
    game = Game(screen)
    # 建立一個遊戲棋盤物件
    chess_board = ChessBoard(screen)
    # 建立計時器
    clock = pygame.time.Clock()

    # 主迴圈
    while True:
        # 事件檢測（例如點選了鍵盤、滑鼠等）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  # 退出程式

            # 如果遊戲沒有獲勝方，則遊戲繼續，否則一直顯示"獲勝"
            if not game.show_win:
                # 檢測是否點選了"可落子"物件
                clicked_dot = Dot.click()
                if clicked_dot:
                    chess_board.move_chess(clicked_dot.row, clicked_dot.col)
                    # 清理「點選物件」、「可落子位置物件」
                    Dot.clean_last_postion()
                    ClickBox.clean()
                    # 判斷此棋子走完之後，是否"將軍"
                    if chess_board.judge_attack_general(game.get_player()):
                        # 檢測對方是否可以挽救棋局，如果能挽救，就顯示"將軍"，否則顯示"勝利"
                        if chess_board.judge_win(game.get_player()):
                            game.set_win(game.get_player())
                        else:
                            # 如果攻擊到對方，則標記顯示"將軍"效果
                            game.set_attack()
                    # 落子之後，交換走棋方
                    game.exchange()
                # 檢查是否點選了棋子
                clicked_chess = Chess.click(game.get_player(), [chess for line in chess_board.map for chess in line if chess])
                if clicked_chess:
                    # 建立選中棋子物件
                    ClickBox(screen, clicked_chess.row, clicked_chess.col, clicked_chess.team)
                    # 清除之前的所有的可以落子物件
                    Dot.clean_last_postion()
                    # 真的點選了棋子，那麼計算當前被點選的棋子可以走的位置
                    all_position = chess_board.get_put_down_postion(clicked_chess)
                    if all_position:
                        # 清空上次可落子物件
                        Dot.clean_last_postion()
                        # 建立可落子物件
                        for position in all_position:
                            Dot(screen, position)

        # 顯示遊戲背景
        screen.blit(background_img, (0, 0))
        screen.blit(background_img, (0, 270))
        screen.blit(background_img, (0, 540))

        # 顯示棋盤以及棋盤上的棋子
        chess_board.show()

        # 顯示被點選的棋子
        ClickBox.show()

        # 顯示可落子物件
        Dot.show()

        # 顯示遊戲相關資訊
        game.show()

        # 顯示screen這個相框的內容（此時在這個相框中的內容像照片、文字等會顯示出來）
        pygame.display.update()

        # FPS（每秒鐘顯示畫面的次數）
        clock.tick(60)  # 通過一定的延時，實現1秒鐘能夠迴圈60次
