import json

import pygame
import requests
from pygame.locals import *

from configs import *


class LoginSystem:
    def __init__(self, screen):
        self.view_password = False
        self.screen = screen
        self.width, self.height = screen.get_size()  # 540 640
        self.state = LOGIN_STATE

        # 字体设置
        self.title_font = pygame.font.SysFont(None, 48)
        self.input_font = pygame.font.SysFont(None, 25)
        self.button_font = pygame.font.SysFont(None, 20)
        self.error_msg_font = pygame.font.SysFont(None, 20)

        self.login_surface = pygame.Surface((230, 300), pygame.SRCALPHA)
        self.login_rect = self.login_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        # 输入框位置
        self.input_boxes = {
            'username': pygame.Rect(self.login_rect.x + 10, self.login_rect.y + 100, 200, 30),
            'password': pygame.Rect(self.login_rect.x + 10, self.login_rect.y + 140, 200, 30),
        }
        self.active_input = 'username'
        self.input_text = {'username': '', 'password': ''}

        # 按钮位置
        self.login_btn = pygame.Rect(self.login_rect.x + 10, self.height // 2 + 80, 80, 20)
        self.register_btn = pygame.Rect(self.login_rect.x + 130, self.height // 2 + 80, 80, 20)
        self.back_btn = pygame.Rect(self.login_rect.x + 10, self.height // 2 + 80, 80, 20)
        self.view_btn = pygame.Rect(self.login_rect.h + 40, self.login_rect.y + 146, 20, 20)
        # self.back_btn = pygame.Rect(20, 20, 80, 40)

        # 错误信息
        self.passwd_error_msg = ''
        self.error_msg = ''
        self.headers = {'Content-Type': 'application/json'}

    def handle_event(self, event):
        """处理事件"""
        if event.type == MOUSEBUTTONDOWN:
            print(self.view_btn.collidepoint(event.pos))
            if self.view_btn.collidepoint(event.pos):
                self.view_password = not self.view_password

            # 检查输入框点击
            for name, box in self.input_boxes.items():
                if box.collidepoint(event.pos):
                    self.active_input = name
                    return

            # 检查按钮点击
            if self.state == LOGIN_STATE:
                if self.login_btn.collidepoint(event.pos):
                    if not self.passwd_error_msg:
                        self.login()
                elif self.register_btn.collidepoint(event.pos):
                    self.input_text = {'username': '', 'password': ''}
                    self.state = REGISTER_STATE
            elif self.state == REGISTER_STATE:
                if self.register_btn.collidepoint(event.pos):
                    if not self.passwd_error_msg:
                        self.register()
                elif self.back_btn.collidepoint(event.pos):
                    self.error_msg = ""
                    self.input_text = {'username': '', 'password': ''}
                    self.state = LOGIN_STATE

        elif event.type == KEYDOWN:
            if self.active_input:
                if event.key == K_RETURN:
                    if self.state == LOGIN_STATE:
                        self.login()
                    elif self.state == REGISTER_STATE:
                        self.register()
                elif event.key == K_BACKSPACE:
                    self.input_text[self.active_input] = self.input_text[self.active_input][:-1]
                else:
                    self.input_text[self.active_input] += event.unicode
                    if self.active_input == 'password':
                        if len(self.input_text[self.active_input]) > MAXIMUM_PASSWD_LEN:
                            self.passwd_error_msg = f'maximum password length is {MAXIMUM_PASSWD_LEN}'
                            self.input_text[self.active_input] = self.input_text[self.active_input][:-1]
                        elif 0 < len(self.input_text[self.active_input]) < MINIMUM_PASSWD_LEN:
                            self.passwd_error_msg = f'minimum password length is {MINIMUM_PASSWD_LEN}'
                        else:
                            self.passwd_error_msg = ''

    def login(self):
        """处理登录逻辑"""
        username = self.input_text["username"]
        password = self.input_text["password"]

        if not username or not password:
            self.error_msg = "username and password cannot be empty"
            return

        payload = json.dumps({"username": username, "password": password})
        response = requests.request("POST", LOGIN_URL, headers=self.headers, data=payload)

        data = response.json()
        print(data)
        if data['code'] == 200:
            access = data['access']
            refresh = data['refresh']
            user_id = data['user_id']
            username = data['username']
            self.state = GAME_STATE
            self.error_msg = ""
            self.headers.update({'Authorization': f'Bearer {access}'})
        else:
            self.error_msg = 'error username or password'

    def register(self):
        """处理注册逻辑"""
        username = self.input_text["username"]
        password = self.input_text["password"]

        if not username or not password:
            self.error_msg = "username and password cannot be empty"
            return

        payload = json.dumps({"username": username, "password": password})
        try:
            response = requests.request("POST", REGISTER_URL, headers=self.headers, data=payload)
            data = response.json()

            if data['code'] == 200:
                self.error_msg = "success!"
                self.state = LOGIN_STATE
            else:
                errors = data['errors']

                error_msg = []
                if isinstance(errors, dict):
                    error_msg.extend(errors.values())
                self.error_msg = str(data['errors'])
        except Exception as e:
            self.error_msg = 'Bad Request, please check you internet connection'

    def draw(self):
        """绘制登录/注册界面"""
        # 绘制背景
        # self.screen.fill((30, 30, 50))  DIALOG_BG_COLOR
        pygame.draw.rect(self.login_surface, (210, 180, 140, 255), self.login_surface.get_rect())  # 180 是透明度值
        # pygame.draw.rect(self.login_surface, (190,190,190, 255), self.login_surface.get_rect())  # 180 是透明度值
        pygame.draw.rect(self.login_surface, (0, 0, 0, 255), self.login_surface.get_rect(), 2)  # 黑色边框

        self.screen.blit(self.login_surface, self.login_rect.topleft)

        # 绘制标题
        if self.state == LOGIN_STATE:
            title = self.title_font.render("login", True, (0, 0, 0))
        else:
            title = self.title_font.render("register", True, (0, 0, 0))
        self.screen.blit(title, (
            (self.login_rect.x * 2 + self.login_rect.w) // 2 - title.get_width() // 2, self.login_rect.y + 40))

        # 绘制输入框
        for name, box in self.input_boxes.items():
            color = (85, 102, 0) if self.active_input == name else (200, 200, 200)
            pygame.draw.rect(self.screen, color, box, 2, border_radius=5)

            # 显示文本（密码显示*）
            display_text = self.input_text[name]
            if name == "password":
                display_text = "*" * len(display_text)

            if self.view_password:
                display_text = self.input_text[name]

            if not display_text and self.active_input != name:
                placeholder = "username" if name == "username" else "password"
                text_surf = self.input_font.render(placeholder, True, (150, 150, 150))
            else:
                text_surf = self.input_font.render(display_text, True, (255, 255, 255))

            self.screen.blit(text_surf, (box.x + 5, box.y + 6))

        pygame.draw.rect(self.screen, (0, 100, 200), self.register_btn, border_radius=8)
        register_text = self.button_font.render("register", True, (255, 255, 255))
        self.screen.blit(register_text, (self.register_btn.centerx - register_text.get_width() // 2,
                                         self.register_btn.centery - register_text.get_height() // 2))

        pygame.draw.rect(self.screen, 'gray', self.view_btn, border_radius=5)
        view_text = self.button_font.render("view", True, (255, 255, 255))
        self.screen.blit(view_text, (self.view_btn.centerx - view_text.get_width() // 2,
                                     self.view_btn.centery - view_text.get_height() // 2))

        # 绘制按钮
        if self.state == LOGIN_STATE:
            pygame.draw.rect(self.screen, (0, 150, 0), self.login_btn, border_radius=8)
            login_text = self.button_font.render("login", True, (255, 255, 255))
            self.screen.blit(login_text, (self.login_btn.centerx - login_text.get_width() // 2,
                                          self.login_btn.centery - login_text.get_height() // 2))
        else:
            pygame.draw.rect(self.screen, (0, 150, 0), self.back_btn, border_radius=8)
            back_text = self.button_font.render("return", True, (255, 255, 255))
            self.screen.blit(back_text, (self.back_btn.centerx - back_text.get_width() // 2,
                                         self.back_btn.centery - back_text.get_height() // 2))

        # 显示错误信息
        if self.error_msg:
            error_text = self.error_msg_font.render(self.error_msg, True, (255, 50, 50))
            self.screen.blit(error_text, (self.login_rect.x + 10, self.login_rect.y + 175, 200, 30))

        if self.passwd_error_msg:
            error_text = self.error_msg_font.render(self.passwd_error_msg, True, (255, 50, 50))
            self.screen.blit(error_text, (self.login_rect.x + 10, self.login_rect.y + 175, 200, 30))
