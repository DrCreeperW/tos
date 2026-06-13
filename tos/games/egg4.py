# egg4: nope
import sys, os
os.environ["DISPLAY"] = os.environ.get("DISPLAY", ":99")
import pygame as pg
pg.init()
s = pg.display.set_mode((400, 200))
pg.display.set_caption("nope")
f = pg.font.SysFont("More Perfect DOS VGA", 48, bold=True)
f2 = pg.font.SysFont("More Perfect DOS VGA", 14)
c = pg.time.Clock()
r = True
frames = 0
while r and frames < 120:
    for e in pg.event.get():
        if e.type == pg.KEYDOWN and (e.key == pg.K_SPACE or e.key == pg.K_ESCAPE):
            r = False
    s.fill((0x8B,0,0))
    t = f.render("nope", True, (0xFF,0xD7,0))
    s.blit(t, (200-t.get_width()//2, 70))
    t2 = f2.render("press space to escape", True, (0xCC,0xAC,0))
    s.blit(t2, (200-t2.get_width()//2, 150))
    pg.display.flip()
    c.tick(60)
    frames += 1
pg.quit()
