# tos dodge — avoid falling blocks
import sys, os, random
os.environ["DISPLAY"] = os.environ.get("DISPLAY", ":99")
import pygame

RED=(0x8B,0,0); YEL=(0xFF,0xD7,0); YEL2=(0xCC,0xAC,0); BLK=(0,0,0)
W=400; H=500; FPS=60; PW=30

def font(sz):
    return pygame.font.SysFont("More Perfect DOS VGA", sz, bold=True)

def scr():
    return pygame.display.set_mode((W, H))

def game(screen, clock):
    px = W//2-PW//2
    py = H-50
    speed = 5
    blocks = []
    score = 0
    timer = 0

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return None
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return score

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: px -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: px += speed
        px = max(0, min(W-PW, px))

        timer += 1
        if timer % 20 == 0:
            bw = random.randint(15, 40)
            bx = random.randint(0, W-bw)
            blocks.append([bx, 0, bw, 15])

        for b in blocks[:]:
            b[1] += 3 + score//10
            if b[1] > H:
                blocks.remove(b)
                score += 1
            elif (px < b[0]+b[2] and px+PW > b[0] and
                  py < b[1]+b[3] and py+20 > b[1]):
                return score

        screen.fill(RED)
        for b in blocks:
            r = pygame.Rect(b[0], b[1], b[2], b[3])
            pygame.draw.rect(screen, YEL2, r)
            pygame.draw.rect(screen, BLK, r, 1)
        pygame.draw.rect(screen, YEL, (px, py, PW, 20))
        pygame.draw.rect(screen, BLK, (px, py, PW, 20), 1)
        sc = font(14).render(f"score: {score}", True, YEL)
        screen.blit(sc, (8, 8))
        pygame.draw.rect(screen, YEL, (0,0,W,H), 2)
        pygame.display.flip()
        clock.tick(FPS)

def run():
    pygame.init()
    pygame.display.set_caption("tos dodge")
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
