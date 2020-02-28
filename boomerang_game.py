
import pygame as pg
import os
import sys
import random
from math import sqrt


MAKESHOT = [0 for i in range(100)] + [1]
K = 3
lvl = 1
lose = 0
pg.init()
c0 = pg.Color('#000000')
c1 = pg.Color('#FFFFFF')

width, height = K * 300, K * 300
WIDTH, HEIGHT = width, height
screen = pg.display.set_mode((width, height))
screen.fill(c0)

enemies = pg.sprite.Group()
all_sprites = pg.sprite.Group()
boom_group = pg.sprite.Group()
bodies = pg.sprite.Group()


def terminate():
    pg.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pg.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Player(pg.sprite.Sprite):
    NV = 160  # normal v
    LEFT, RIGHT = True, False
    image = pg.transform.scale(load_image('Player-2.png', c0), (9*K, 9*K))
    death_anim = [pg.transform.scale(load_image(f'death-{i}.png', c0), (9*K, 9*K))
                  for i in range(1, 9)]

    def __init__(self, coords):
        super().__init__(all_sprites, bodies)
        self.image = Player.image
        self.run_anim = [pg.transform.scale(load_image(f'Player-{i}.png', c0), (9*K, 9*K))
                         for i in range(1, 5)]
        self.v = Player.NV
        self.health = 0
        self.having_b = True
        self.x, self.y = coords
        self.directions = set()
        self.watch = {'up'}
        self.run_time = 0
        self.run_i = 0
        self.d_time = 0
        self.d_i = 0
        self.lr = Player.RIGHT
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = coords
        self.mask = pg.mask.from_surface(self.image)
        self.kills = 0

    def update(self, ev):
        if ev.type == pg.KEYDOWN:
            if ev.key == pg.K_x and self.having_b:
                self.fire()
                self.having_b = False
            if ev.key == pg.K_UP:
                self.directions.add('up')
                if 'down' in self.watch:
                    self.watch.remove('down')
                self.watch.add('up')
            elif ev.key == pg.K_DOWN:
                self.directions.add('down')
                if 'up' in self.watch:
                    self.watch.remove('up')
                self.watch.add('down')
            elif ev.key == pg.K_LEFT:
                self.directions.add('left')
                if 'right' in self.watch:
                    self.watch.remove('right')
                self.watch.add('left')
            elif ev.key == pg.K_RIGHT:
                self.directions.add('right')
                if 'left' in self.watch:
                    self.watch.remove('left')
                self.watch.add('right')
        if ev.type == pg.KEYUP:
            if ev.key == pg.K_UP and 'up' in self.directions:
                self.directions.remove('up')
            elif ev.key == pg.K_DOWN and 'down' in self.directions:
                self.directions.remove('down')
            elif ev.key == pg.K_LEFT and 'left' in self.directions:
                self.directions.remove('left')
            elif ev.key == pg.K_RIGHT and 'right' in self.directions:
                self.directions.remove('right')

    def run(self):
        if self.directions:
            if 'up' in self.directions:
                if self.move_check(self.x, self.y - self.v / fps):
                    self.y -= self.v / fps
            if 'down' in self.directions:
                if self.move_check(self.x, self.y + self.v / fps):
                    self.y += self.v / fps
            if 'left' in self.directions:
                if self.move_check(self.x - self.v / fps, self.y):
                    self.x -= self.v / fps
                self.lr = Player.LEFT
            if 'right' in self.directions:
                if self.move_check(self.x + self.v / fps, self.y):
                    self.x += self.v / fps
                self.lr = Player.RIGHT

            self.run_time += 1
            if self.run_time == 7:
                self.run_time = 0
                self.run_i = (self.run_i + 1) % 4
            self.image = self.run_anim[self.run_i]
        else:
            self.run_time, self.run_i, self.image = 0, 0, Player.image
        self.image = pg.transform.flip(self.image, self.lr, False)
        self.rect.x, self.rect.y = round(self.x), round(self.y)

    def move_check(self, x, y):
        if 0 < x < width - 9 * K and 0 < y < height - 9 * K:
            return True
        return False

    def death(self):
        global enemies
        for sprite in enemies:
            if pg.sprite.collide_mask(self, sprite):
                return True

    def fire(self):
        Boomerang(self.watch)

    def set_watch(self):
        buf = self.watch.copy()
        self.watch = set()
        for d in self.directions:
            if d == 'up':
                self.watch.add('up')
            elif d == 'down':
                self.watch.add('down')
            elif d == 'left':
                self.watch.add('left')
            elif d == 'right':
                self.watch.add('right')
        if not self.watch:
            self.watch = buf.copy()

    def win(self):
        if plr.kills == 2 * lvl:
            return True
        return False

    def final(self):
        clock.tick(2)
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    terminate()
            screen.fill(c0)
            self.d_time += 1
            if self.d_time == 7:
                self.d_time = 0
                self.d_i = self.d_i + 1
            if self.d_i == len(Player.death_anim):
                return
            self.image = pg.transform.flip(Player.death_anim[self.d_i], plr.lr, False)
            all_sprites.draw(screen)
            pg.display.flip()
            clock.tick(fps)


class Enemy(pg.sprite.Sprite):
    image = pg.transform.scale(load_image('minion-1.png', c0), (9*K, 9*K))
    run_anim = [pg.transform.scale(load_image(f'minion-{i}.png', c0), (9*K, 9*K))
                for i in range(1, 3)]
    emerging_anim = [pg.transform.scale(load_image(f'emerging-{i}.png', c0), (9*K, 9*K))
                     for i in range(1, 6)]
    death_anim = [pg.transform.scale(load_image(f'enemy_death_anim-{i}.png.png', c0), (9 * K, 9 * K))
                  for i in range(2, 7)]
    tremble_anim = [pg.transform.scale(load_image(f'minion-{i}.png', c0), (9 * K, 9 * K))
                    for i in range(1, 3)]

    def __init__(self):
        super().__init__(all_sprites, enemies, bodies)
        self.image = Enemy.image
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, width - 9*K)
        self.rect.y = random.randrange(0, height - 9*K)

        self.health = 18
        self.d_time = 0
        self.d_i = 0
        self.t_time = 0
        self.t_i = 0
        self.em_time = 0
        self.em_i = 0
        self.turn = 0
        self.turnT = 100
        self.frozen = True
        self.mask = pg.mask.from_surface(self.image)

    def emerging(self):
        self.em_time += 1
        if self.em_time == 7:
            self.em_time = 0
            self.em_i = self.em_i + 1
        self.image = Enemy.emerging_anim[self.em_i]
        if self.em_i == len(Enemy.emerging_anim) - 1:
            self.image = Enemy.image
            self.frozen = False

    def update(self):
        if self.health <= 0:
            self.fire()
            self.fire()
            self.fire()
            self.fire()
            self.fire()
            self.fire()
            self.fire()
            self.fire()
            self.d_time += 1
            if self.d_time == 7:
                self.d_time = 0
                self.d_i = self.d_i + 1
            self.image = Enemy.death_anim[self.d_i]
            if self.d_i == len(Enemy.death_anim) - 1:
                plr.kills += 1
                self.kill()
        if not self.frozen:
            self.turn += 1
            # if self.turn == self.turnT:
            #     self.turn = 0
            #     self.fire()
            self.fire()
        else:
            self.emerging()

    def fire(self):
        if random.choice(MAKESHOT) == 1:
            Bullet(plr, self.rect.x, self.rect.y)

    def tremble(self):
        self.t_time += 1
        if self.t_time == 2:
            self.t_time = 0
            self.t_i = (self.t_i + 1) % 2
        self.image = Enemy.tremble_anim[self.t_i]


class Bullet(pg.sprite.Sprite):
    image = pg.transform.scale(load_image('bullet.png', c0), (9*K, 9*K))
    v = 180

    def __init__(self, target, x, y):
        super().__init__(all_sprites, enemies)
        self.image = Bullet.image
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.x, self.y = x, y
        self.rect.x, self.rect.y = x, y
        tx, ty = target.x + random.randrange(-100, 100), target.y + random.randrange(-100, 100)
        self.vy = abs(Bullet.v / sqrt(1 + ((tx - x) / (ty - y))**2))
        self.vx = abs(((tx - x) / (ty - y)) * self.vy)
        if tx < x:
            self.vx *= -1
        if ty < y:
            self.vy *= -1

    def update(self):
        self.x += self.vx / fps
        self.y += self.vy / fps
        self.rect.x, self.rect.y = round(self.x), round(self.y)


class Boomerang(pg.sprite.Sprite):
    anim = [pg.transform.scale(load_image(f'boomerang-{i}.png', c0), (9*K, 9*K))
            for i in range(1, 4)]
    v = 150
    v0 = 150

    def __init__(self, dirs):
        super().__init__(all_sprites, boom_group)
        self.image = Boomerang.anim[0]
        self.rect = self.image.get_rect()
        self.x = plr.x
        self.y = plr.y
        self.rect.x = plr.rect.x
        self.rect.y = plr.rect.y
        self.b_time = 0
        self.b_i = 0
        self.shot = 0
        self.vx = 0
        self.vy = 0
        self.dirs = dirs
        self.v1 = Boomerang.v0 + self.v
        self.v2 = 0

    def update(self):
        for sprite in bodies:
            if pg.sprite.collide_mask(self, sprite):
                sprite.health -= 1
                if sprite.health > 0:
                    sprite.tremble()

        self.b_time += 1
        if self.b_time == 7:
            self.b_time = 0
            self.b_i = (self.b_i + 1) % 3
        self.image = Boomerang.anim[self.b_i]
        if self.v1 <= 0:
            self.v2 += 2
            if self.y == plr.y:
                self.vy = abs(self.v2 / sqrt(1 + (plr.x - self.x) ** 2))
                self.vx = abs((plr.x - self.x) * self.vy)
            else:
                self.vy = abs(self.v2 / sqrt(1 + ((plr.x - self.x) / (plr.y - self.y)) ** 2))
                self.vx = abs(((plr.x - self.x) / (plr.y - self.y)) * self.vy)
            if plr.x < self.x:
                self.vx *= -1
            if plr.y < self.y:
                self.vy *= -1

            self.x += self.vx / fps
            self.y += self.vy / fps
            self.rect.x, self.rect.y = round(self.x), round(self.y)

            if pg.sprite.collide_mask(self, plr):
                plr.having_b = True
                self.kill()
        else:
            # self.shot += 1
            self.v1 -= 4
            if len(self.dirs) == 2:
                k_b = 1 / sqrt(2)
            else:
                k_b = 1
            for d in self.dirs:
                if d == 'up':
                    self.y -= k_b * self.v1 / fps
                elif d == 'right':
                    self.x += k_b * self.v1 / fps
                elif d == 'left':
                    self.x -= k_b * self.v1 / fps
                elif d == 'down':
                    self.y += k_b * self.v1 / fps
            self.rect.x, self.rect.y = round(self.x), round(self.y)


def intro(n):
    if lose == 1:
        intro_text = ["YOU DIED", "",
                      f"level {n}", "", "",
                      "Press x"]
    elif lose == 2:
        intro_text = ["YOU WIN!", "",
                      f"level {n}", "", "",
                      "Press x"]
    else:
        intro_text = ["BOOMERANG GAME", "",
                      f"level {n}", "", "",
                      "Press x"]

    fon = pg.transform.scale(load_image('intro.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pg.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, c1)
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            elif event.type == pg.KEYDOWN and event.key == pg.K_x:
                return  # начинаем игру
        pg.display.flip()
        clock.tick(fps)


def level():
    global lvl
    global lose
    global plr
    intro(lvl)

    for _ in range(2 * lvl):
        x = Enemy()
        for sprite in bodies:
            while pg.sprite.collide_mask(x, sprite):
                x.kill()
                x = Enemy()
    # Enemy()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            plr.update(event)

        plr.set_watch()
        screen.fill(c0)
        plr.run()
        if plr.death():
            lose = 1
            plr.final()
            clock.tick(0.5)
            all_sprites.empty()
            enemies.empty()
            boom_group.empty()
            bodies.empty()
            plr = Player((WIDTH // 2, HEIGHT // 2))
            return
        if plr.win():
            lvl += 1
            lose = 2
            clock.tick(0.5)
            all_sprites.empty()
            enemies.empty()
            bodies.empty()
            boom_group.empty()
            plr = Player((WIDTH // 2, HEIGHT // 2))
            return
        # enemies.update()
        enemies.update()
        enemies.draw(screen)
        screen.blit(plr.image, (round(plr.x), round(plr.y)))
        boom_group.draw(screen)
        boom_group.update()

        clock.tick(fps)
        pg.display.flip()


if __name__ == '__main__':
    plr = Player((WIDTH // 2, HEIGHT // 2))
    fps = 60
    clock = pg.time.Clock()
    lvl = 1
    while True:
        level()
