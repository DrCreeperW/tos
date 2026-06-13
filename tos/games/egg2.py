# egg2: fake loading
import sys, os, random
os.environ["DISPLAY"] = os.environ.get("DISPLAY", ":99")
import pygame as pg
pg.init()
s = pg.display.set_mode((400, 200))
pg.display.set_caption("")
f = pg.font.SysFont("More Perfect DOS VGA", 14)
c = pg.time.Clock()
r = True
for i in range(101):
    for e in pg.event.get():
        if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
            r = False
    if not r: break
    s.fill((0x5C,0,0))
    t = f.render(f"loading... {i}%", True, (0xFF,0xD7,0))
    s.blit(t, (200-t.get_width()//2, 80))
    pg.draw.rect(s, (0xFF,0xD7,0), (100, 110, i*2, 10))
    pg.draw.rect(s, (0,0,0), (100, 110, 200, 10), 1)
    pg.display.flip()
    c.tick(random.randint(5,30))
pg.time.wait(2000)
pg.quit()
