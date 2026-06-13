# egg1: why are you here
import sys, os
os.environ["DISPLAY"] = os.environ.get("DISPLAY", ":99")
import pygame as pg
pg.init()
s = pg.display.set_mode((400, 300))
pg.display.set_caption("")
f = pg.font.SysFont("More Perfect DOS VGA", 14)
c = pg.time.Clock()
r = True
n = 0
while r and n < 200:
    for e in pg.event.get():
        if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
            r = False
    s.fill((0x5C,0,0))
    t = f.render("why are you here?", True, (0xFF,0xD7,0))
    s.blit(t, (200-t.get_width()//2, 140))
    pg.display.flip()
    c.tick(10)
    n += 1
pg.quit()
