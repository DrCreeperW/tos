# tos pong — 1 player vs wall, flat retro
import sys, os
os.environ["DISPLAY"] = os.environ.get("DISPLAY", ":99")
import pygame

RED=(0x8B,0,0); RED2=(0x5C,0,0); YEL=(0xFF,0xD7,0); YEL2=(0xCC,0xAC,0)
BLK=(0,0,0); W=480; H=360; FPS=60

PAD_W=8; PAD_H=50; BALL_S=8

def font(sz):
    return pygame.font.SysFont("More Perfect DOS VGA", sz, bold=True)

def scr():
    return pygame.display.set_mode((W, H))

def game(screen, clock):
    px, py = 20, H//2-PAD_H//2
    bx, by = W//2, H//2
    bdx, bdy = 4, 3
    score = 0

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return None
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return score
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]: py -= 5
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: py += 5
        py = max(0, min(H-PAD_H, py))

        bx += bdx; by += bdy
        if by <= 0 or by >= H-BALL_S: bdy = -bdy
        if bx <= 0: return score
        if bx >= W: bdx = -bdx; score += 1

        # paddle collision
        if (bx <= px + PAD_W and by + BALL_S > py and by < py + PAD_H):
            bdx = -bdx
            bx = px + PAD_W

        screen.fill(RED)
        for y in range(0, H, 20):
            pygame.draw.rect(screen, RED2, (W//2-1, y, 2, 10))
        pygame.draw.rect(screen, YEL, (px, py, PAD_W, PAD_H))
        pygame.draw.rect(screen, BLK, (px, py, PAD_W, PAD_H), 1)
        pygame.draw.rect(screen, YEL, (bx, by, BALL_S, BALL_S))
        pygame.draw.rect(screen, BLK, (bx, by, BALL_S, BALL_S), 1)
        sc = font(14).render(f"score: {score}", True, YEL)
        screen.blit(sc, (W//2-40, 10))
        pygame.draw.rect(screen, YEL, (0,0,W,H), 2)
        pygame.display.flip()
        clock.tick(FPS)

def run():
    pygame.init()
    pygame.display.set_caption("tos pong")
    s, c = scr(), pygame.time.Clock()
    r = None
    while r is None:
        r = game(s, c)
        if r is not None:
            s.fill(RED)
            t1 = font(22).render("game over", True, YEL)
            t2 = font(36).render(str(r), True, YEL)
            t3 = font(14).render("space=again  esc=exit", True, YEL2)
            s.blit(t1, (W//2-t1.get_width()//2, 100))
            s.blit(t2, (W//2-t2.get_width()//2, 150))
            s.blit(t3, (W//2-t3.get_width()//2, 220))
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
