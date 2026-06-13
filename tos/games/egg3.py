# egg3: beep machine
import sys, os
os.environ["DISPLAY"] = os.environ.get("DISPLAY", ":99")
import pygame as pg
pg.init()
s = pg.display.set_mode((400, 200))
pg.display.set_caption("")
f = pg.font.SysFont("More Perfect DOS VGA", 14)
c = pg.time.Clock()
r = True
notes = ["beep","boop","bip","bop","baap"]
i = 0
while r and i < 50:
    for e in pg.event.get():
        if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
            r = False
    s.fill((0x5C,0,0))
    t = f.render(notes[i % len(notes)], True, (0xFF,0xD7,0))
    s.blit(t, (200-t.get_width()//2, 90))
    pg.display.flip()
    c.tick(4)
    i += 1
pg.quit()
