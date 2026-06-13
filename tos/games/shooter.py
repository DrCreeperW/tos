# tos shooter — move and shoot enemies
import sys, os, random
os.environ["DISPLAY"] = os.environ.get("DISPLAY", ":99")
import pygame

RED=(0x8B,0,0); RED2=(0x5C,0,0); YEL=(0xFF,0xD7,0); YEL2=(0xCC,0xAC,0); BLK=(0,0,0)
W=480; H=400; FPS=60; PW=30; PH=20

def font(sz):
    return pygame.font.SysFont("More Perfect DOS VGA", sz, bold=True)

def scr():
    return pygame.display.set_mode((W, H))

def game(screen, clock):
    px, py = W//2, H-50
    bullets = []
    enemies = []
    score = 0
    timer = 0
    cooldown = 0

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return None
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return score

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: px -= 5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: px += 5
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            if cooldown <= 0:
                bullets.append([px+PW//2-2, py-10])
                cooldown = 12
        px = max(PW//2, min(W-PW//2, px))
        if cooldown > 0: cooldown -= 1

        for b in bullets[:]:
            b[1] -= 6
            if b[1] < 0: bullets.remove(b)

        timer += 1
        if timer % 25 == 0:
            ex = random.randint(20, W-20)
            enemies.append([ex, 0, 15, 15])

        for e2 in enemies[:]:
            e2[1] += 2
            if e2[1] > H: enemies.remove(e2)
            elif (abs(e2[0]-px) < e2[2]+PW//2 and abs(e2[1]-py) < e2[3]+PH//2):
                return score

        for b in bullets[:]:
            for e2 in enemies[:]:
                if abs(b[0]-e2[0]) < e2[2] and abs(b[1]-e2[1]) < e2[3]:
                    bullets.remove(b)
                    enemies.remove(e2)
                    score += 1
                    break

        screen.fill(RED)
        for ex, ey, ew, eh in enemies:
            pygame.draw.rect(screen, YEL2, (ex-ew//2, ey-eh//2, ew, eh))
            pygame.draw.rect(screen, BLK, (ex-ew//2, ey-eh//2, ew, eh), 1)
        for bx, by in bullets:
            pygame.draw.rect(screen, YEL, (bx, by, 4, 8))
        pygame.draw.rect(screen, YEL, (px-PW//2, py-PH//2, PW, PH))
        pygame.draw.rect(screen, BLK, (px-PW//2, py-PH//2, PW, PH), 1)
        sc = font(14).render(f"score: {score}", True, YEL)
        screen.blit(sc, (8, 8))
        pygame.draw.rect(screen, YEL, (0,0,W,H), 2)
        pygame.display.flip()
        clock.tick(FPS)

def run():
    pygame.init()
    pygame.display.set_caption("tos shooter")
    s, c = scr(), pygame.time.Clock()
    r = None
    while r is None:
        r = game(s, c)
        if r is not None:
            s.fill(RED)
            t1 = font(22).render("game over", True, YEL)
            t2 = font(36).render(str(r), True, YEL)
            t3 = font(14).render("space=again  esc=exit", True, YEL2)
            s.blit(t1, (W//2-t1.get_width()//2, 130))
            s.blit(t2, (W//2-t2.get_width()//2, 180))
            s.blit(t3, (W//2-t3.get_width()//2, 250))
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
