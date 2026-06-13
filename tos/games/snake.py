# tos snake — classic snake game, flat retro
import sys, os, random
os.environ["DISPLAY"] = os.environ.get("DISPLAY", ":99")
import pygame

RED=(0x8B,0,0); RED2=(0x5C,0,0); YEL=(0xFF,0xD7,0); YEL2=(0xCC,0xAC,0)
BLK=(0,0,0); W=480; H=480; CELL=16; COLS=W//CELL; ROWS=H//CELL; FPS=8

def font(sz=16):
    return pygame.font.SysFont("More Perfect DOS VGA", sz, bold=True)

def scr():
    return pygame.display.set_mode((W, H))

def game(screen, clock):
    snake = [(COLS//2, ROWS//2)]
    dx, dy = 1, 0
    food = (random.randrange(COLS), random.randrange(ROWS))
    score = 0

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return score
                if e.key in (pygame.K_LEFT,pygame.K_a) and dx!=1: dx,dy=-1,0
                if e.key in (pygame.K_RIGHT,pygame.K_d) and dx!=-1: dx,dy=1,0
                if e.key in (pygame.K_UP,pygame.K_w) and dy!=1: dx,dy=0,-1
                if e.key in (pygame.K_DOWN,pygame.K_s) and dy!=-1: dx,dy=0,1

        hx, hy = snake[0]
        nx, ny = hx+dx, hy+dy
        if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS:
            return score
        if (nx, ny) in snake:
            return score

        snake.insert(0, (nx, ny))
        if (nx, ny) == food:
            score += 1
            food = (random.randrange(COLS), random.randrange(ROWS))
        else:
            snake.pop()

        screen.fill(RED)
        for gx in range(0, W, CELL):
            pygame.draw.line(screen, RED2, (gx,0), (gx,H), 1)
        for gy in range(0, H, CELL):
            pygame.draw.line(screen, RED2, (0,gy), (W,gy), 1)
        for x, y in snake:
            r = pygame.Rect(x*CELL+1, y*CELL+1, CELL-2, CELL-2)
            pygame.draw.rect(screen, YEL, r)
            pygame.draw.rect(screen, BLK, r, 1)
        fx, fy = food
        pygame.draw.rect(screen, YEL2, (fx*CELL+2, fy*CELL+2, CELL-4, CELL-4))
        sc = font(14).render(f"score: {score}", True, YEL)
        screen.blit(sc, (8, 8))
        pygame.draw.rect(screen, YEL, (0,0,W,H), 2)
        pygame.display.flip()
        clock.tick(FPS)

def run():
    pygame.init()
    pygame.display.set_caption("tos snake")
    s, c = scr(), pygame.time.Clock()
    r = None
    while r is None:
        r = game(s, c)
        if r is not None:
            s.fill(RED)
            t1 = font(22).render("game over", True, YEL)
            t2 = font(36).render(str(r), True, YEL)
            t3 = font(14).render("space=again  esc=exit", True, YEL2)
            s.blit(t1, (W//2-t1.get_width()//2, 150))
            s.blit(t2, (W//2-t2.get_width()//2, 200))
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
