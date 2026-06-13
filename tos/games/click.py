# tos click — click targets before they disappear
import sys, os, random
os.environ["DISPLAY"] = os.environ.get("DISPLAY", ":99")
import pygame

RED=(0x8B,0,0); YEL=(0xFF,0xD7,0); YEL2=(0xCC,0xAC,0); BLK=(0,0,0)
W=480; H=400; FPS=60

def font(sz):
    return pygame.font.SysFont("More Perfect DOS VGA", sz, bold=True)

def scr():
    return pygame.display.set_mode((W, H))

def game(screen, clock):
    targets = []
    score = 0
    timer = 0
    lives = 3

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return None
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return score
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                hit = False
                for t in targets[:]:
                    tx, ty, ts, tt = t
                    if abs(mx-tx) < ts and abs(my-ty) < ts:
                        targets.remove(t)
                        score += 1
                        hit = True
                        break
                if not hit:
                    lives -= 1
                    if lives <= 0:
                        return score

        timer += 1
        if timer % 30 == 0 and len(targets) < 5:
            sz = random.randint(16, 32)
            targets.append([random.randint(sz, W-sz), random.randint(sz, H-sz), sz, 60])

        for t in targets[:]:
            t[3] -= 1
            if t[3] <= 0:
                targets.remove(t)
                lives -= 1
                if lives <= 0:
                    return score

        screen.fill(RED)
        for tx, ty, ts, tt in targets:
            fade = 60 - tt
            c = (200-fade*2, 180-fade, 0) if fade < 30 else YEL2
            pygame.draw.rect(screen, c, (tx-ts//2, ty-ts//2, ts, ts))
            pygame.draw.rect(screen, BLK, (tx-ts//2, ty-ts//2, ts, ts), 2)
        sc = font(14).render(f"score: {score}  lives: {lives}", True, YEL)
        screen.blit(sc, (8, 8))
        pygame.draw.rect(screen, YEL, (0,0,W,H), 2)
        pygame.display.flip()
        clock.tick(FPS)

def run():
    pygame.init()
    pygame.display.set_caption("tos click")
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
