# egg ya — cryptic "y & a" message
import sys, os, random, math
os.environ["DISPLAY"] = os.environ.get("DISPLAY", ":99")
import pygame as pg

pg.init()
s = pg.display.set_mode((400, 300))
pg.display.set_caption("")
f = pg.font.SysFont("More Perfect DOS VGA", 48, bold=True)
f2 = pg.font.SysFont("More Perfect DOS VGA", 14)
c = pg.time.Clock()
r = True
t = 0
while r and t < 300:
    for e in pg.event.get():
        if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
            r = False
        if e.type == pg.QUIT:
            r = False
    s.fill((0x5C, 0, 0))
    # flicker text
    if t % 15 < 12:
        txt = f.render("y & a", True, (0xFF, 0xD7, 0))
        s.blit(txt, (200 - txt.get_width()//2, 120 - txt.get_height()//2))
    # random dots
    for _ in range(20):
        dx = random.randint(0, 400)
        dy = random.randint(0, 300)
        s.set_at((dx, dy), (0xFF, 0xD7, 0) if random.random() > 0.5 else (0xCC, 0xAC, 0))
    hint = f2.render("press esc to exit", True, (0xCC, 0xAC, 0))
    s.blit(hint, (200 - hint.get_width()//2, 230))
    pg.display.flip()
    c.tick(10)
    t += 1
pg.quit()
