import pygame

# 初始化
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((400, 300))

# 加载音频
pygame.mixer.music.load("vedio/im_dead.wav")
# jump_sound = pygame.mixer.Sound("vedio/im_dead.wav")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # 按 P 播放/暂停
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
            elif event.key == pygame.K_j:  # 按 J 播放音效
                pygame.mixer.music.play()

    pygame.display.flip()

pygame.quit()