# tos jumper — 2d platformer, flat retro
import sys, os, random
os.environ["DISPLAY"] = os.environ.get("DISPLAY", ":99")
import pygame

RED=(0x8B,0,0); RED2=(0x5C,0,0); YEL=(0xFF,0xD7,0); YEL2=(0xCC,0xAC,0); BLK=(0,0,0)
W=480; H=480; FPS=60; PW=18; PH=18; GRAV=0.5; JUMP=-10; SPD=5
PW2=18; PH2=18

def font(sz):
    return pygame.font.SysFont("More Perfect DOS VGA", sz, bold=True)

def scr():
    return pygame.display.set_mode((W, H))

class Player:
    def __init__(self, x, y):
        self.r = pygame.Rect(x, y, PW, PH)
        self.vx = 0; self.vy = 0; self.on = False; self.score = 0

    def update(self, plats):
        self.vy += GRAV
        if self.vy > 12: self.vy = 12
        self.r.x += self.vx
        for p in plats:
            if self.r.colliderect(p.r):
                if self.vx > 0: self.r.right = p.r.left
                elif self.vx < 0: self.r.left = p.r.right
        self.r.y += self.vy
        self.on = False
        for p in plats:
            if self.r.colliderect(p.r):
                if self.vy > 0:
                    self.r.bottom = p.r.top; self.vy = 0; self.on = True
                elif self.vy < 0:
                    self.r.top = p.r.bottom; self.vy = 0
        if self.r.y < 0:
            self.score += abs(self.r.y)//20
            self.r.y = 0

    def jump(self):
        if self.on: self.vy = JUMP

    def draw(self, s):
        s2 = self.r.copy(); s2.x += 2; s2.y += 2
        pygame.draw.rect(s, RED2, s2)
        pygame.draw.rect(s, YEL, self.r)
        pygame.draw.rect(s, BLK, self.r, 2)

    def dead(self):
        return self.r.y > H + 50


def make_plats():
    plats = [pygame.Rect(0, H-20, W, 14)]
    y = H - 60
    for _ in range(15):
        y -= random.randint(50, 90)
        if y < 20: break
        x = random.randint(20, W-80)
        plats.append(pygame.Rect(x, y, random.choice([60,80,100]), 12))
    return plats


def game(s, c):
    plats = make_plats()
    p = Player(100, H-80)
    scr2 = 0

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return None
        keys = pygame.key.get_pressed()
        p.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: p.vx = -SPD
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: p.vx = SPD
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]: p.jump()
        if keys[pygame.K_ESCAPE]: return p.score

        p.update(plats)
        if p.dead(): return p.score

        # scroll
        if p.r.y < H//3 and p.vy < 0:
            scroll = -p.vy
            p.r.y += scroll
            for pl in plats: pl.y += scroll
            plats = [pl for pl in plats if pl.y < H+20]
            while True:
                top = min(pl.y for pl in plats) if plats else H
                if top > 20:
                    ny = top - random.randint(50, 90)
                    nx = random.randint(20, W-80)
                    plats.append(pygame.Rect(nx, ny, random.choice([60,80,100]), 12))
                else:
                    break

        s.fill(RED)
        for gx in range(0, W, 40):
            pygame.draw.line(s, RED2, (gx,0), (gx,H), 1)
        for gy in range(0, H, 40):
            pygame.draw.line(s, RED2, (0,gy), (W,gy), 1)
        for pl in plats:
            r = pygame.Rect(pl.x, pl.y, pl.width, pl.height)
            pygame.draw.rect(s, RED2, r)
            pygame.draw.line(s, YEL2, (pl.x, pl.y), (pl.x+pl.width-1, pl.y), 2)
            pygame.draw.line(s, BLK, (pl.x, pl.y+pl.height-1), (pl.x+pl.width-1, pl.y+pl.height-1), 2)
            pygame.draw.line(s, YEL2, (pl.x, pl.y), (pl.x, pl.y+pl.height-1), 2)
            pygame.draw.line(s, BLK, (pl.x+pl.width-1, pl.y), (pl.x+pl.width-1, pl.y+pl.height-1), 2)
        p.draw(s)
        sc = font(14).render(f"score: {p.score}", True, YEL)
        s.blit(sc, (8, 8))
        pygame.draw.rect(s, YEL, (0,0,W,H), 2)
        pygame.display.flip()
        c.tick(FPS)


def run():
    pygame.init()
    pygame.display.set_caption("tos jumper")
    s, c = scr(), pygame.time.Clock()
    r = None
    while r is None:
        r = game(s, c)
        if r is not None:
            s.fill(RED)
            t1 = font(22).render("game over", True, YEL)
            t2 = font(36).render(str(r), True, YEL)
            t3 = font(14).render("space=again  esc=exit", True, YEL2)
            s.blit(t1, (W//2-t1.get_width()//2, 160))
            s.blit(t2, (W//2-t2.get_width()//2, 210))
            s.blit(t3, (W//2-t3.get_width()//2, 280))
            pygame.draw.rect(s, YEL, (0,0,W,H), 2)
            pygame.display.flip()
            wait = True
            while wait:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: r=None; wait=False
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_SPACE: r=None; wait=False
                        if e.key == pygame.K_ESCAPE: wait=False
                c.tick(10)
            if r is None: break
    pygame.quit()

if __name__ == "__main__": run()
