import os
import sys
import time
import pygame

# constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WALL_COLOR = (228, 192, 83)
GLOW_DARK = (5, 255, 157)

wn_w = 1100
wn_h = 700

timer = 0


class Game:
    def __init__(self, caption, screen_w, screen_h):
        self.caption = pygame.display.set_caption(str(caption))
        self.screen = pygame.display.set_mode((screen_w, screen_h), pygame.SRCALPHA)
        self.clock = pygame.time.Clock()
        self.intro = self.sim = self.play = self.outro = True
        self.opening = True
        self.instructions = False
        self.room_front = True
        self.room_right = self.room_back = self.room_left = False

        # text
        self.title = Text(125, "Escape the Room", "fonts/Quantum.otf", WHITE, 550, 133)
        self.start = Text(45, "start", "fonts/Quantum.otf", WHITE, 550, 270)
        self.quit = Text(50, "quit", "fonts/Quantum.otf", WHITE, 874, 270)
        self.help = Text(50, "help", "fonts/Quantum.otf", WHITE, 226, 270)

        self.instructions_title = Text(100, "Instructions", "fonts/Quantum.otf", WHITE, 550, 100)
        self.instructions_back = Text(45, "back", "fonts/Quantum.otf", WHITE, 60, 25)
        self.instructions_text1 = Text(50, "click arrows to move", "fonts/Quantum.otf", WHITE, 550, 200)
        self.instructions_text2 = Text(50, "click items to obtain them", "fonts/Quantum.otf", WHITE, 550, 250)
        self.instructions_text3 = Text(50, "click and hold to drag", "fonts/Quantum.otf", WHITE, 550, 300)
        self.instructions_text4 = Text(50, "use any hints you find", "fonts/Quantum.otf", WHITE, 550, 350)
        self.instructions_text5 = Text(50, "solve the puzzles", "fonts/Quantum.otf", WHITE, 550, 400)
        self.instructions_text6 = Text(50, "use your head", "fonts/Quantum.otf", WHITE, 550, 450)
        self.instructions_text7 = Text(50, "escape the room", "fonts/Quantum.otf", WHITE, 550, 500)
        self.instructions_text1.rect.left = self.instructions_text2.rect.left = self.instructions_text3.rect.left = \
            self.instructions_text4.rect.left = self.instructions_text5.rect.left = \
            self.instructions_text6.rect.left = self.instructions_text7.rect.left = 250

        self.click = Text(75, "click to start simulation", "fonts/Quantum.otf", WHITE, 550, 350)

        self.congrats = Text(100, "CONGRATS!", "fonts/Quantum.otf", WHITE, 550, 182)
        self.win = Text(75, "You escaped the room!", "fonts/Quantum.otf", WHITE, 550, 315)
        self.again = Text(50, "play again", "fonts/Quantum.otf", WHITE, 550, 445)

        # sounds
        self.intro_music = pygame.mixer.Sound("sounds/ElectronicaSci-Fi.ogg")
        self.intro_music.set_volume(0.75)
        self.play_music = pygame.mixer.Sound("sounds/JazzCity.ogg")
        self.play_music.set_volume(0.75)
        self.jumpscare = pygame.mixer.Sound("sounds/SuspenseStrike.ogg")

        # images
        self.op_bg = pygame.image.load("images/bg/op_bg.png").convert()
        self.op_bg = pygame.transform.scale(self.op_bg, (wn_w, wn_h))
        self.op_bg_rect = self.op_bg.get_rect()

        self.sim_room = pygame.image.load("images/bg/sim_room.png").convert()
        self.sim_room = pygame.transform.scale(self.sim_room, (wn_w, wn_h))
        self.sim_room_rect = self.sim_room.get_rect()

        self.fade_in = pygame.image.load("images/bg/fade_in.png").convert()
        self.fade_in = pygame.transform.scale(self.fade_in, (wn_w, wn_h))
        self.fade_in_rect = self.fade_in.get_rect()

        self.room_bg = pygame.image.load("images/bg/room.png").convert()
        self.room_bg = pygame.transform.scale(self.room_bg, (wn_w, wn_h))
        self.room_bg_rect = self.room_bg.get_rect()

        self.dark = pygame.image.load("images/bg/dark.png").convert_alpha()
        self.dark = pygame.transform.scale(self.dark, (wn_w, wn_h))
        self.dark_rect = self.dark.get_rect()

        self.zoom_in = pygame.image.load("images/bg/zoom_in.png").convert()
        self.zoom_in = pygame.transform.scale(self.zoom_in, (wn_w, wn_h))
        self.zoom_in_rect = self.zoom_in.get_rect()

        self.white = pygame.image.load("images/bg/white.png").convert()
        self.white = pygame.transform.scale(self.white, (wn_w, wn_h))
        self.white_rect = self.white.get_rect()

        self.black = pygame.image.load("images/bg/black.png").convert()
        self.black = pygame.transform.scale(self.black, (wn_w, wn_h))
        self.black_rect = self.black.get_rect()

    def blink(self, image, rect):
        # blinking text
        if (pygame.time.get_ticks() % 1500) < 500:
            self.screen.blit(image, rect)


class Text:
    def __init__(self, size, text, font, color, x, y):
        self.font = pygame.font.Font(font, int(size))
        self.image = self.font.render(str(text), 1, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Item(pygame.sprite.Sprite):
    def __init__(self, item, link, width, height, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item = item
        self.w = width
        self.h = height
        self.x = x
        self.y = y
        self.image = pygame.image.load(link).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.w, self.h))
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.click = False

        # special cases
        if self.item == 'drawer':
            self.lock = True
        if self.item == 'safe':
            self.lock = True
        if self.item == 'safe_button':
            self.lock = True
            self.switch = False

        if self.item == 'light_switch':
            self.switch = False

        if self.item == 'bookshelf':
            self.moved = 0

        if self.item == 'drawer_key':
            self.lock = True
            self.keep = False
        if self.item == 'door_key':
            self.lock = True
            self.keep = False

        if self.item == 'vent':
            self.lock = True
        if self.item == 'screwdriver':
            self.keep = False



    def update(self):
        # boundaries
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > wn_w - self.rect.width:
            self.rect.x = wn_w - self.rect.width

        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y > wn_h - self.rect.height:
            self.rect.y = wn_h - self.rect.height

        # sliding
        if self.item == 'bookshelf':
            if self.rect.y < self.rect.bottom:
                self.rect.y = self.rect.bottom
            if self.rect.y > 595 - self.rect.height:
                self.rect.y = 595 - self.rect.height
            if self.rect.x > 937 - self.rect.width:
                self.rect.x = 937 - self.rect.width
            if self.rect.x < 389 + 389/4:
                self.rect.x = 389 + 389/4
        if self.item == 'plant':
            if self.rect.y < self.rect.bottom:
                self.rect.y = self.rect.bottom
            if self.rect.y > 618 - self.rect.height:
                self.rect.y = 618 - self.rect.height
            if self.rect.x > 100 + self.rect.width / 4:
                self.rect.x = 100 + self.rect.width / 4
            if self.rect.x < 75:
                self.rect.x = 75

        # light switch
        if self.item == 'light_switch':
            if self.click:
                self.image = pygame.image.load("images/room_F/switch_off.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (29, 45))
            if not self.click:
                self.image = pygame.image.load("images/room_F/switch_on.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (29, 45))
        if self.item == 'light':
            if self.click:
                self.image = pygame.image.load("images/light_off.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (37, 60))
            if not self.click:
                self.image = pygame.image.load("images/light_on.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (37, 60))

        # safe
        if self.item == 'safe':
            # zoom in
            if self.lock:
                if not self.click:
                    self.image = pygame.image.load("images/lock_safe/lock_safe.png").convert_alpha()
                    self.image = pygame.transform.scale(self.image, (self.w, self.h))
                    self.rect = self.image.get_rect()
                    self.rect.center = (250, 375)
                elif self.click:
                    self.image = pygame.image.load("images/lock_safe/lock_safe_clear.png").convert_alpha()
                    self.image = pygame.transform.scale(self.image, (522, 650))
                    self.rect = self.image.get_rect()
                    self.rect.center = (wn_w/2, wn_h/2)
            # safe answer
            if not self.lock:
                if self.click:
                    self.image = pygame.image.load("images/lock_safe/open_safe.png").convert_alpha()
                    self.image = pygame.transform.scale(self.image, (836, 650))
                    self.rect = self.image.get_rect()
                    self.rect.center = (393, wn_h/2)
                if not self.click:
                    self.image = pygame.image.load("images/lock_safe/open_safe.png").convert_alpha()
                    self.image = pygame.transform.scale(self.image, (152, self.h))
                    self.rect = self.image.get_rect()
                    self.rect.center = (221, 375)
        if self.item == 'safe_button':
            if self.click:
                self.image = pygame.image.load("images/lock_safe/on_button.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (60, 60))
            if not self.click:
                self.image = pygame.image.load("images/lock_safe/off_button.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (60, 60))

        if self.item == 'drawer':
            self.image = pygame.image.load("images/drawer/drawer.png").convert_alpha()
            if not self.click:
                self.image = pygame.transform.scale(self.image, (self.w, self.h))
                self.rect = self.image.get_rect()
                self.rect.center = (900, 550)
            elif self.click:
                self.image = pygame.transform.scale(self.image, (650, 650))
                self.rect = self.image.get_rect()
                self.rect.center = (wn_w/2, wn_h/2)

        if self.item == 'plaque':
            # zoom in
            self.image = pygame.image.load("images/room_R/tesla_plaque.png").convert_alpha()
            if not self.click:
                self.image = pygame.transform.scale(self.image, (self.w, self.h))
                self.rect = self.image.get_rect()
                self.rect.center = (250, 450)
            if self.click:
                self.image = pygame.transform.scale(self.image, (1000, 322))
                self.rect = self.image.get_rect()
                self.rect.center = (wn_w/2, wn_h/2)

        if self.item == 'mousehole':
            self.image = pygame.image.load("images/room_L/mousehole.png").convert_alpha()
            if not self.click:
                self.image = pygame.transform.scale(self.image, (self.w, self.h))
                self.rect = self.image.get_rect()
                self.rect.center = (450, 567)
            elif self.click:
                self.image = pygame.transform.scale(self.image, (620, 457))
                self.rect = self.image.get_rect()
                self.rect.center = (wn_w/2, 315)

        if self.item == 'vent':
            if self.lock:
                self.image = pygame.image.load("images/room_B/vent.png").convert_alpha()
                if not self.click:
                    self.image = pygame.transform.scale(self.image, (self.w, self.h))
                    self.rect = self.image.get_rect()
                    self.rect.center = (225, 150)
                elif self.click:
                    self.image = pygame.transform.scale(self.image, (658, 525))
                    self.rect = self.image.get_rect()
                    self.rect.center = (wn_w/2, wn_h/2)
            if not self.lock:
                self.image = pygame.image.load("images/room_B/open_vent.png").convert_alpha()
                if not self.click:
                    self.image = pygame.transform.scale(self.image, (153, 128))
                    self.rect = self.image.get_rect()
                    self.rect.center = (190, 172)
                elif self.click:
                    self.image = pygame.transform.scale(self.image, (997, 834))
                    self.rect = self.image.get_rect()
                    self.rect.center = (329, 493)

        if self.item == 'short_cabinet':
            self.image = pygame.image.load("images/room_B/short_cabinet.png").convert_alpha()
            if not self.click:
                self.image = pygame.transform.scale(self.image, (self.w, self.h))
                self.rect = self.image.get_rect()
                self.rect.center = (275, 550)
            elif self.click:
                self.image = pygame.transform.scale(self.image, (1000, 364))
                self.rect = self.image.get_rect()
                self.rect.center = (wn_w/2, 450)

        if self.item == 'note':
            self.image = pygame.image.load("images/room_B/note.png").convert_alpha()
            if not self.click:
                self.image = pygame.transform.scale(self.image, (self.w, self.h))
                self.rect = self.image.get_rect()
                self.rect.center = (675, 500)
            if self.click:
                self.image = pygame.transform.scale(self.image, (619, 600))
                self.rect = self.image.get_rect()
                self.rect.center = (wn_w/2, wn_h/2)


class Inventory(pygame.sprite.Sprite):
    def __init__(self, num, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.num = num
        self.w = self.h = 90
        self.x = x
        self.y = y
        self.image = pygame.image.load("images/bg/transparent.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.w, self.h))
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.click = False
        self.taken = False

    def update(self):
        # zoom
        if self.click:
            self.rect.centery = 53
        if not self.click:
            self.rect.centery = 647

        # visibility
        if not self.taken:
            self.image = pygame.image.load("images/bg/transparent.png").convert_alpha()
        if self.taken:
            self.image = pygame.image.load("images/inventory_slot.png").convert_alpha()


def main():
    global wn_w, wn_h, timer, WHITE, BLACK

    while True:
        # variables
        fps = 72

        # objects
        game = Game('Escape the Room', wn_w, wn_h)

        # --INTRO
        start_door = Item('start_door', "images/bg/transparent.png", 144, 288, 550, 432)
        quit_door = Item('quit_door', "images/bg/transparent.png", 144, 288, 874, 432)
        help_door = Item('start_door', "images/bg/transparent.png", 144, 288, 226, 432)

        # --PLAY
        arrow_l = Item('arrow_l', "images/arrows/arrow_left.png", 40, 73, 25, 350)
        arrow_r = Item('arrow_r', "images/arrows/arrow_right.png", 40, 73, 1075, 350)
        arrow_d = Item('arrow_d', "images/arrows/arrow_down.png", 73, 40, 550, 675)

        inventory_slot1 = Inventory('1', 50, 647)
        inventory_slot2 = Inventory('2', 150, 647)
        inventory_slot3 = Inventory('3', 250, 647)

        light = Item('light', "images/light_on.png", 37, 60, 550, 0)

        # *room_F
        door = Item('door', "images/room_F/door.png", 210, 364, 550, 400)
        light_switch = Item('light_switch', "images/room_F/switch_on.png", 29, 45, 410, 375)
        door_key = Item('door_key', "images/room_F/door_key.png", 57, 65, wn_w/2, 540)

        safe = Item('safe', "images/lock_safe/lock_safe.png", 95, 118, 250, 375)
        #   1st row
        safe_button1 = Item('safe_button', "images/lock_safe/off_button.png", 60, 60, 435, 227)
        safe_button2 = Item('safe_button', "images/lock_safe/off_button.png", 60, 60, 550, 227)
        safe_button3 = Item('safe_button', "images/lock_safe/off_button.png", 60, 60, 665, 227)
        #   2nd row
        safe_button4 = Item('safe_button', "images/lock_safe/off_button.png", 60, 60, 435, 342)
        safe_button5 = Item('safe_button', "images/lock_safe/off_button.png", 60, 60, 550, 342)
        safe_button6 = Item('safe_button', "images/lock_safe/off_button.png", 60, 60, 665, 342)
        #   3rd row
        safe_button7 = Item('safe_button', "images/lock_safe/off_button.png", 60, 60, 435, 457)
        safe_button8 = Item('safe_button', "images/lock_safe/off_button.png", 60, 60, 550, 457)
        safe_button9 = Item('safe_button', "images/lock_safe/off_button.png", 60, 60, 665, 457)

        # *room_R
        table = Item('table', "images/room_R/table.png", 400, 117, 250, 570)
        portrait = Item('portrait', "images/room_R/tesla_portrait.png", 225, 266, 250, 300)
        plaque = Item('plaque', "images/room_R/tesla_plaque.png", 62, 20, 250, 450)
        bookshelf = Item('bookshelf', "images/room_R/bookshelf.png", 274, 350, 800, 420)
        safe_answer = Item('safe_answer', "images/lock_safe/lock_safe_answer.png", 150, 187, 830, 410)

        # *room_B
        vent = Item('vent', "images/room_B/vent.png", 100, 80, 225, 150)
        short_cabinet = Item('short_cabinet', "images/room_B/short_cabinet.png", 350, 127, 275, 550)
        cabinet_l = Item('cabinet_l', "images/bg/transparent.png", 342, 149, 304, 474)
        cabinet_r = Item('cabinet_r', "images/bg/transparent.png", 342, 149, 781, 474)
        sofa = Item('sofa', "images/room_B/sofa.png", 450, 187, 750, 535)
        drawer_key = Item('drawer_key', "images/drawer/drawer_key.png", 65, 65, wn_w / 2, wn_h/2)
        note = Item('note', "images/room_B/note.png", 100, 97, 675, 500)

        # *room_L
        mousehole = Item('mousehole', "images/room_L/mousehole.png", 50, 37, 450, 567)
        inv_hole = Item('invisible_hole', "images/bg/transparent.png", 620, 457, wn_w/2, 315)
        rat = Item('rat', "images/room_L/rat.png", 535, 350, 550, 450)
        plant = Item('plant', "images/room_L/house_plant.png", 250, 386, 200, 425)
        drawer = Item('drawer', "images/drawer/drawer.png", 150, 150, 900, 550)
        drawer_t = Item('drawer_top', "images/bg/transparent.png", 477, 238, 546, 239)
        drawer_b = Item('drawer_bottom', "images/bg/transparent.png", 477, 238, 546, 491)
        screwdriver = Item('screwdriver', "images/room_L/screwdriver.png", 59, 85, wn_w / 2, wn_h / 2)

        # groups
        intro_doors = pygame.sprite.Group()
        intro_doors.add(start_door, quit_door, help_door)

        not_move_group1 = pygame.sprite.Group()
        not_move_group1.add(door, light, light_switch)
        lock_group1 = pygame.sprite.Group()
        lock_group1.add(safe)
        safe_button_group = pygame.sprite.Group()
        safe_button_group.add(safe_button1, safe_button2, safe_button3, safe_button4, safe_button5, safe_button6,
                              safe_button7, safe_button8, safe_button9)
        inventory_item_group1 = pygame.sprite.Group()
        inventory_item_group1.add(door_key)

        not_move_group2 = pygame.sprite.Group()
        not_move_group2.add(light, table, portrait, plaque)
        move_group2 = pygame.sprite.Group()
        move_group2.add(bookshelf)
        lock_group2 = pygame.sprite.Group()
        lock_group2.add(safe_answer)

        not_move_group3 = pygame.sprite.Group()
        not_move_group3.add(light, vent, short_cabinet, sofa)
        cabinet_group = pygame.sprite.Group()
        cabinet_group.add(cabinet_l, cabinet_r)

        not_move_group4 = pygame.sprite.Group()
        not_move_group4.add(light, mousehole)
        move_group4 = pygame.sprite.Group()
        move_group4.add(plant)
        lock_group4 = pygame.sprite.Group()
        lock_group4.add(drawer)
        drawer_group = pygame.sprite.Group()
        drawer_group.add(drawer_t, drawer_b)

        arrow_group = pygame.sprite.Group()
        arrow_group.add(arrow_l, arrow_r)
        arrow_d_group = pygame.sprite.Group()
        arrow_d_group.add(arrow_d)

        inventory_group = pygame.sprite.Group()
        inventory_group.add(inventory_slot1, inventory_slot2, inventory_slot3)
        inv_item_group = pygame.sprite.Group()

        # INTRO MUSIC
        game.intro_music.play(-1, 0, 2500)

        # intro
        while game.intro:
            while game.opening:
                # checks if window exit button is pressed or if screen is clicked
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # start
                        if start_door.rect.collidepoint(event.pos):
                            game.intro = game.opening = False
                            game.intro_music.fadeout(1500)
                            time.sleep(1.5)
                        # quit
                        if quit_door.rect.collidepoint(event.pos):
                            time.sleep(0.25)
                            sys.exit()
                        # help
                        if help_door.rect.collidepoint(event.pos):
                            time.sleep(0.25)
                            game.opening = False
                            game.instructions = True

                intro_doors.update()

                # blit images
                game.screen.blit(game.op_bg, game.op_bg_rect)
                game.screen.blit(game.title.image, game.title.rect)

                for x in intro_doors:
                    game.screen.blit(x.image, x.rect)

                game.screen.blit(game.start.image, game.start.rect)
                game.screen.blit(game.quit.image, game.quit.rect)
                game.screen.blit(game.help.image, game.help.rect)

                # limits frames per iteration of while loop
                game.clock.tick(fps)
                # writes to main surface
                pygame.display.flip()

            while game.instructions:
                # checks if window exit button is pressed or if screen is clicked
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # back to game.opening
                        if game.instructions_back.rect.collidepoint(event.pos):
                            time.sleep(0.25)
                            game.instructions = False
                            game.opening = True

                game.screen.fill(BLACK)

                # blit images
                game.screen.blit(game.instructions_title.image, game.instructions_title.rect)
                game.screen.blit(game.instructions_back.image, game.instructions_back.rect)
                game.screen.blit(game.instructions_text1.image, game.instructions_text1.rect)
                game.screen.blit(game.instructions_text2.image, game.instructions_text2.rect)
                game.screen.blit(game.instructions_text3.image, game.instructions_text3.rect)
                game.screen.blit(game.instructions_text4.image, game.instructions_text4.rect)
                game.screen.blit(game.instructions_text5.image, game.instructions_text5.rect)
                game.screen.blit(game.instructions_text6.image, game.instructions_text6.rect)
                game.screen.blit(game.instructions_text7.image, game.instructions_text7.rect)

                # limits frames per iteration of while loop
                game.clock.tick(fps)
                # writes to main surface
                pygame.display.flip()

        # fade in sim room
        for x in range(25):
            pygame.time.delay(50)
            game.sim_room.set_alpha(x)
            game.screen.blit(game.sim_room, game.sim_room_rect)
            pygame.display.update()

        # simulation room
        while game.sim:
            # checks if window exit button is pressed or if screen is clicked
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if game.click.rect.collidepoint(event.pos):
                        game.screen.blit(game.click.image, game.click.rect)
                        pygame.display.flip()
                        time.sleep(1)
                        game.sim = False

            game.screen.blit(game.sim_room, game.sim_room_rect)

            # blinking text
            game.blink(game.click.image, game.click.rect)

            # limits frames per iteration of while loop
            game.clock.tick(fps)
            # writes to main surface
            pygame.display.flip()

        # fade in game room
        for x in range(50):
            pygame.time.delay(50)
            game.fade_in.set_alpha(x)
            game.screen.blit(game.fade_in, game.fade_in_rect)
            pygame.display.update()

        # PLAY MUSIC
        game.play_music.play(-1, 0, 2500)

        # gameplay
        while game.play:
            while game.room_front:
                for event in pygame.event.get():
                    # exit screen
                    if event.type == pygame.QUIT:
                        sys.exit()
                    # drag
                    for g in inv_item_group:
                        if g.keep:
                            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                if g.rect.collidepoint(event.pos):
                                    g.click = True
                                    mx, my = event.pos
                                    offset_x = g.rect.x - mx
                                    offset_y = g.rect.y - my
                            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                                g.click = False
                            elif event.type == pygame.MOUSEMOTION and g.click:
                                mx, my = event.pos
                                g.rect.x = mx + offset_x
                                g.rect.y = my + offset_y
                    # click
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # light switch
                        if light_switch.rect.collidepoint(event.pos):
                            if not light_switch.switch:
                                light_switch.click = True
                                light.click = True
                                light_switch.switch = True
                            elif light_switch.switch:
                                light_switch.click = False
                                light.click = False
                                light_switch.switch = False
                        # switch rooms
                        if arrow_l.rect.collidepoint(event.pos):
                            time.sleep(0.25)
                            game.room_front = False
                            game.room_left = True
                        elif arrow_r.rect.collidepoint(event.pos):
                            time.sleep(0.25)
                            game.room_front = False
                            game.room_right = True
                        # safe
                        if safe.rect.collidepoint(event.pos):
                            safe.click = True
                            for i in inventory_group:
                                i.click = True
                        # down arrow
                        if arrow_d.rect.collidepoint(event.pos):
                            safe.click = False
                            for i in inventory_group:
                                i.click = False
                            # returns buttons back to normal when leaving
                            for l in safe_button_group:
                                l.click = False
                                l.switch = False
                        # safe button
                        for l in safe_button_group:
                            if l.rect.collidepoint(event.pos):
                                if not l.switch:
                                    l.click = True
                                    l.switch = True
                                elif l.switch:
                                    l.click = False
                                    l.switch = False
                        # safe answer
                        if safe_button1.click and safe_button5.click and safe_button7.click and safe_button8.click and \
                                safe_button9.click:
                            # open safe
                            safe.lock = False
                            # remove buttons
                            for l in safe_button_group:
                                l.kill()
                        # put door_key in inventory
                        if door_key.rect.collidepoint(event.pos):
                            inventory_item_group1.remove(door_key)
                            inv_item_group.add(door_key)
                            door_key.keep = True
                            inventory_slot3.taken = True

                # update
                lock_group1.update()
                safe_button_group.update()
                not_move_group1.update()
                inventory_group.update()
                inventory_item_group1.update()
                inv_item_group.update()

                # inventory
                if screwdriver.keep and not screwdriver.click:
                    screwdriver.rect.center = inventory_slot1.rect.center
                if drawer_key.keep and not drawer_key.click:
                    drawer_key.rect.center = inventory_slot2.rect.center

                # blit
                game.screen.blit(game.room_bg, game.room_bg_rect)

                for n in not_move_group1:
                    game.screen.blit(n.image, n.rect)
                for l in lock_group1:
                    game.screen.blit(l.image, l.rect)

                # darkens screen if lights are off
                if light_switch.click and light.click:
                    game.screen.blit(game.dark, game.dark_rect)

                for a in arrow_group:
                    game.screen.blit(a.image, a.rect)

                for i in inventory_group:
                    game.screen.blit(i.image, i.rect)
                for x in inv_item_group:
                    game.screen.blit(x.image, x.rect)

                # zoom in safe
                if safe.click:
                    game.screen.fill(WALL_COLOR)
                    for l in lock_group1:
                        game.screen.blit(l.image, l.rect)
                    for b in safe_button_group:
                        game.screen.blit(b.image, b.rect)
                    # darkens screen if lights are off
                    if light_switch.click and light.click:
                        game.screen.blit(game.dark, game.dark_rect)
                    for d in arrow_d_group:
                        game.screen.blit(d.image, d.rect)
                    for i in inventory_group:
                        game.screen.blit(i.image, i.rect)
                    for x in inv_item_group:
                        game.screen.blit(x.image, x.rect)
                    # open safe
                    if not safe.lock:
                        for d in inventory_item_group1:
                            game.screen.blit(d.image, d.rect)

                # door + key = win
                if not door_key.click and door_key.keep:
                    if pygame.sprite.collide_rect(door_key, door) and not safe.click:
                        door_key.keep = False
                        inventory_slot3.taken = False
                        door_key.kill()
                        game.play_music.fadeout(1500)
                        time.sleep(1.5)
                        game.play = game.room_front = False
                        # game.ending.play(-1, 0, 2500)
                    elif door_key.keep:
                        door_key.rect.center = inventory_slot3.rect.center

                # limits frames per iteration of while loop
                game.clock.tick(fps)
                # writes to main surface
                pygame.display.flip()

            while game.room_right:
                for event in pygame.event.get():
                    # exit screen
                    if event.type == pygame.QUIT:
                        sys.exit()
                    # drag
                    for m in move_group2:
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if m.rect.collidepoint(event.pos):
                                m.click = True
                                mx, my = event.pos
                                offset_x = m.rect.x - mx
                                offset_y = m.rect.y - my
                        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                            m.click = False
                        elif event.type == pygame.MOUSEMOTION and m.click:
                            mx, my = event.pos
                            m.rect.x = mx + offset_x
                            m.rect.y = my + offset_y
                    for g in inv_item_group:
                        if g.keep:
                            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                if g.rect.collidepoint(event.pos):
                                    g.click = True
                                    mx, my = event.pos
                                    offset_x = g.rect.x - mx
                                    offset_y = g.rect.y - my
                            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                                g.click = False
                            elif event.type == pygame.MOUSEMOTION and g.click:
                                mx, my = event.pos
                                g.rect.x = mx + offset_x
                                g.rect.y = my + offset_y
                    # click
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # switch rooms
                        if arrow_l.rect.collidepoint(event.pos):
                            time.sleep(0.25)
                            game.room_right = False
                            game.room_front = True
                        elif arrow_r.rect.collidepoint(event.pos):
                            time.sleep(0.25)
                            game.room_right = False
                            game.room_back = True
                        # plaque
                        if plaque.rect.collidepoint(event.pos):
                            plaque.click = True
                            for i in inventory_group:
                                i.click = True
                        # down arrow
                        if arrow_d.rect.collidepoint(event.pos):
                            plaque.click = False
                            for i in inventory_group:
                                i.click = False

                # update
                not_move_group2.update()
                move_group2.update()
                inventory_group.update()
                inv_item_group.update()

                # inventory
                if screwdriver.keep and not screwdriver.click:
                    screwdriver.rect.center = inventory_slot1.rect.center
                if drawer_key.keep and not drawer_key.click:
                    drawer_key.rect.center = inventory_slot2.rect.center
                if door_key.keep and not door_key.click:
                    door_key.rect.center = inventory_slot3.rect.center

                # blit
                game.screen.blit(game.room_bg, game.room_bg_rect)

                # glow in the dark
                if light_switch.click and light.click:
                    for s in lock_group2:
                        game.screen.blit(s.image, s.rect)

                for n in not_move_group2:
                    game.screen.blit(n.image, n.rect)
                for m in move_group2:
                    game.screen.blit(m.image, m.rect)

                # darkens screen if lights are off
                if light_switch.click and light.click:
                    game.screen.blit(game.dark, game.dark_rect)

                for a in arrow_group:
                    game.screen.blit(a.image, a.rect)

                for i in inventory_group:
                    game.screen.blit(i.image, i.rect)
                for x in inv_item_group:
                    game.screen.blit(x.image, x.rect)

                # zoom in plaque
                if plaque.click:
                    game.screen.fill(WALL_COLOR)
                    game.screen.blit(plaque.image, plaque.rect)
                    # darkens screen if lights are off
                    if light_switch.click and light.click:
                        game.screen.blit(game.dark, game.dark_rect)
                    for d in arrow_d_group:
                        game.screen.blit(d.image, d.rect)
                    for i in inventory_group:
                        game.screen.blit(i.image, i.rect)
                    for x in inv_item_group:
                        game.screen.blit(x.image, x.rect)

                # limits frames per iteration of while loop
                game.clock.tick(fps)
                # writes to main surface
                pygame.display.flip()

            while game.room_back:
                for event in pygame.event.get():
                    # exit screen
                    if event.type == pygame.QUIT:
                        sys.exit()
                    # drag
                    for g in inv_item_group:
                        if g.keep:
                            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                if g.rect.collidepoint(event.pos):
                                    g.click = True
                                    mx, my = event.pos
                                    offset_x = g.rect.x - mx
                                    offset_y = g.rect.y - my
                            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                                g.click = False
                            elif event.type == pygame.MOUSEMOTION and g.click:
                                mx, my = event.pos
                                g.rect.x = mx + offset_x
                                g.rect.y = my + offset_y
                    # click
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # switch rooms
                        if arrow_l.rect.collidepoint(event.pos):
                            time.sleep(0.25)
                            game.room_back = False
                            game.room_right = True
                        elif arrow_r.rect.collidepoint(event.pos):
                            time.sleep(0.25)
                            game.room_back = False
                            game.room_left = True
                        # vent
                        if vent.rect.collidepoint(event.pos):
                            vent.click = True
                            for i in inventory_group:
                                i.click = True
                        # note
                        if not vent.lock and note.rect.collidepoint(event.pos):
                            note.click = True
                        # cabinet
                        if short_cabinet.rect.collidepoint(event.pos):
                            short_cabinet.click = True
                            for i in inventory_group:
                                i.click = True
                        if short_cabinet.click:
                            # cabinet_l -- get item
                            if cabinet_l.rect.collidepoint(event.pos):
                                cabinet_l.kill()
                            # cabinet_r -- get item
                            if cabinet_r.rect.collidepoint(event.pos) and not drawer.click:
                                cabinet_r.kill()
                                drawer_key.keep = inventory_slot2.taken = True
                                inv_item_group.add(drawer_key)
                        # down arrow
                        if arrow_d.rect.collidepoint(event.pos):
                            if not note.click:
                                vent.click = short_cabinet.click = False
                                for i in inventory_group:
                                    i.click = False
                            if vent.click and not vent.lock:
                                note.click = False

                # update
                not_move_group3.update()
                inventory_group.update()
                inv_item_group.update()
                cabinet_group.update()
                note.update()

                # inventory
                if screwdriver.keep and not screwdriver.click and not vent.click:
                    screwdriver.rect.center = inventory_slot1.rect.center
                if drawer_key.keep and not drawer_key.click:
                    drawer_key.rect.center = inventory_slot2.rect.center
                if door_key.keep and not door_key.click:
                    door_key.rect.center = inventory_slot3.rect.center

                # blit
                game.screen.blit(game.room_bg, game.room_bg_rect)

                for n in not_move_group3:
                    game.screen.blit(n.image, n.rect)

                # darkens screen if lights are off
                if light_switch.click and light.click:
                    game.screen.blit(game.dark, game.dark_rect)

                for a in arrow_group:
                    game.screen.blit(a.image, a.rect)

                for i in inventory_group:
                    game.screen.blit(i.image, i.rect)
                for x in inv_item_group:
                    game.screen.blit(x.image, x.rect)

                # zoom in vent
                if vent.click:
                    game.screen.fill(WALL_COLOR)
                    game.screen.blit(vent.image, vent.rect)
                    # zoom in note
                    if not vent.lock:
                        game.screen.blit(note.image, note.rect)
                    # darkens screen if lights are off
                    if light_switch.click and light.click:
                        game.screen.blit(game.dark, game.dark_rect)
                    for a in arrow_d_group:
                        game.screen.blit(a.image, a.rect)
                    for i in inventory_group:
                        game.screen.blit(i.image, i.rect)
                    for x in inv_item_group:
                        game.screen.blit(x.image, x.rect)
                    # screwdriver + vent = open
                    if not screwdriver.click and screwdriver.keep:
                        if pygame.sprite.collide_rect(screwdriver, vent):
                            screwdriver.keep = inventory_slot1.taken = vent.lock = False
                            screwdriver.kill()
                        elif screwdriver.keep:
                            screwdriver.rect.center = inventory_slot1.rect.center

                # zoom in cabinet
                if short_cabinet.click:
                    game.screen.blit(game.zoom_in, game.zoom_in_rect)
                    game.screen.blit(short_cabinet.image, short_cabinet.rect)
                    for c in cabinet_group:
                        game.screen.blit(c.image, c.rect)
                    # darkens screen if lights are off
                    if light_switch.click and light.click:
                        game.screen.blit(game.dark, game.dark_rect)
                    for a in arrow_d_group:
                        game.screen.blit(a.image, a.rect)
                    for i in inventory_group:
                        game.screen.blit(i.image, i.rect)
                    for x in inv_item_group:
                        game.screen.blit(x.image, x.rect)

                # limits frames per iteration of while loop
                game.clock.tick(fps)
                # writes to main surface
                pygame.display.flip()

            while game.room_left:
                for event in pygame.event.get():
                    # exit screen
                    if event.type == pygame.QUIT:
                        sys.exit()
                    # drag
                    for m in move_group4:
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if m.rect.collidepoint(event.pos):
                                m.click = True
                                mx, my = event.pos
                                offset_x = m.rect.x - mx
                                offset_y = m.rect.y - my
                        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                            m.click = False
                        elif event.type == pygame.MOUSEMOTION and m.click:
                            mx, my = event.pos
                            m.rect.x = mx + offset_x
                            m.rect.y = my + offset_y
                    for g in inv_item_group:
                        if g.keep:
                            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                if g.rect.collidepoint(event.pos):
                                    g.click = True
                                    mx, my = event.pos
                                    offset_x = g.rect.x - mx
                                    offset_y = g.rect.y - my
                            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                                g.click = False
                            elif event.type == pygame.MOUSEMOTION and g.click:
                                mx, my = event.pos
                                g.rect.x = mx + offset_x
                                g.rect.y = my + offset_y
                    # click
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # switch rooms
                        if arrow_l.rect.collidepoint(event.pos):
                            time.sleep(0.25)
                            game.room_left = False
                            game.room_back = True
                        elif arrow_r.rect.collidepoint(event.pos):
                            time.sleep(0.25)
                            game.room_left = False
                            game.room_front = True
                        # drawer
                        if drawer.rect.collidepoint(event.pos):
                            drawer.click = True
                            for i in inventory_group:
                                i.click = True
                        # mousehole
                        if mousehole.rect.collidepoint(event.pos):
                            mousehole.click = True
                            for i in inventory_group:
                                i.click = True
                            # rat appears -- muahahaha
                            if inv_hole.rect.collidepoint(event.pos):
                                game.jumpscare.play(0)
                                rat.click = True
                        # down arrow
                        if arrow_d.rect.collidepoint(event.pos):
                            drawer.click = mousehole.click = rat.click = False
                            for i in inventory_group:
                                i.click = False

                # update
                not_move_group4.update()
                move_group4.update()
                lock_group4.update()
                inventory_group.update()
                drawer_group.update()
                inv_item_group.update()

                # inventory
                if screwdriver.keep and not screwdriver.click:
                    screwdriver.rect.center = inventory_slot1.rect.center
                if drawer_key.keep and not drawer_key.click and not drawer.click:
                    drawer_key.rect.center = inventory_slot2.rect.center
                if door_key.keep and not door_key.click:
                    door_key.rect.center = inventory_slot3.rect.center

                # blit
                game.screen.blit(game.room_bg, game.room_bg_rect)

                for n in not_move_group4:
                    game.screen.blit(n.image, n.rect)
                for l in lock_group4:
                    game.screen.blit(l.image, l.rect)
                for m in move_group4:
                    game.screen.blit(m.image, m.rect)

                # darkens screen if lights are off
                if light_switch.click and light.click:
                    game.screen.blit(game.dark, game.dark_rect)

                for a in arrow_group:
                    game.screen.blit(a.image, a.rect)

                for i in inventory_group:
                    game.screen.blit(i.image, i.rect)
                for x in inv_item_group:
                    game.screen.blit(x.image, x.rect)

                # zoom in drawer
                if drawer.click:
                    game.screen.blit(game.zoom_in, game.zoom_in_rect)
                    for l in lock_group4:
                        game.screen.blit(l.image, l.rect)
                    for d in drawer_group:
                        game.screen.blit(d.image, d.rect)
                    # darkens screen if lights are off
                    if light_switch.click and light.click:
                        game.screen.blit(game.dark, game.dark_rect)
                    for a in arrow_d_group:
                        game.screen.blit(a.image, a.rect)
                    for i in inventory_group:
                        game.screen.blit(i.image, i.rect)
                    for x in inv_item_group:
                        game.screen.blit(x.image, x.rect)
                    # drawer_key + drawer_t = open
                    if not drawer_key.click and drawer_key.keep:
                        if pygame.sprite.collide_rect(drawer_key, drawer_t):
                            drawer_key.keep = inventory_slot2.taken = False
                            drawer_key.kill()
                            drawer_t.kill()
                            screwdriver.keep = inventory_slot1.taken = True
                            inv_item_group.add(screwdriver)
                        elif drawer_key.keep:
                            drawer_key.rect.center = inventory_slot2.rect.center

                # zoom in mousehole
                if mousehole.click:
                    game.screen.blit(game.zoom_in, game.zoom_in_rect)
                    game.screen.blit(mousehole.image, mousehole.rect)
                    game.screen.blit(inv_hole.image, inv_hole.rect)
                    # jumpscare ;)
                    if rat.click:
                        game.screen.blit(rat.image, rat.rect)
                    # darkens screen if lights are off
                    if light_switch.click and light.click:
                        game.screen.blit(game.dark, game.dark_rect)
                    for a in arrow_d_group:
                        game.screen.blit(a.image, a.rect)
                    for i in inventory_group:
                        game.screen.blit(i.image, i.rect)
                    for x in inv_item_group:
                        game.screen.blit(x.image, x.rect)

                # limits frames per iteration of while loop
                game.clock.tick(fps)
                # writes to main surface
                pygame.display.flip()

        # fade to white
        for x in range(50):
            pygame.time.delay(50)
            game.white.set_alpha(x)
            game.screen.blit(game.white, game.white_rect)
            pygame.display.update()

        # outro
        while game.outro:
            # checks if window exit button is pressed or if screen is clicked
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if game.again.rect.collidepoint(event.pos):
                        game.screen.blit(game.again.image, game.again.rect)
                        pygame.display.flip()
                        time.sleep(1.5)
                        game.outro = False

            game.screen.blit(game.sim_room, game.sim_room_rect)
            game.screen.blit(game.congrats.image, game.congrats.rect)
            game.screen.blit(game.win.image, game.win.rect)

            game.blink(game.again.image, game.again.rect)

            # limits frames per iteration of while loop
            game.clock.tick(fps)
            # writes to main surface
            pygame.display.flip()

        # fade to black
        for x in range(40):
            pygame.time.delay(50)
            game.black.set_alpha(x)
            game.screen.blit(game.black, game.black_rect)
            pygame.display.update()


if __name__ == "__main__":
    # force static position of screen
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    # runs imported module
    pygame.init()

    # to get rid of sound lag
    pygame.mixer.pre_init(44100, -16, 2, 2048)

    main()
