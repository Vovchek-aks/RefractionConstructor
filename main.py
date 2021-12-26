from typing import List, Tuple
import pygame as pg
import colors as col


class App:
    def __init__(self, size: Tuple[int, int], name: str = 'App'):
        self.size = self.width, self.height = size

        pg.init()

        self.sc = pg.display.set_mode(size)
        self.clock = pg.time.Clock()

        self.drawer = Drawer()

    def update(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                exit(0)

        pg.display.set_caption(str(self.clock.get_fps()))

    def draw(self):
        self.sc.fill(col.background)
        self.drawer.draw_all(self.sc)

        pg.display.flip()

    def tick(self):
        self.update()
        self.draw()

        self.clock.tick(60)


class Coords:
    def __init__(self, pos: Tuple[int, int]):
        self.pos = pos


class MainCoords(Coords):
    def __init__(self, pos: Tuple[int, int]):
        super().__init__(pos)
        self.coords: List[Coords] = []

    def get_one(self, coords: Coords):
        return coords.pos[0] + self.pos[0], \
               coords.pos[1] + self.pos[1]

    def get_all(self):
        return (self.get_one(c) for c in self.coords)


class ThingToDraw(Coords):
    def draw(self, pos: Tuple[int, int], sc: pg.Surface):
        pass


class Drawer:
    def __init__(self):
        self.things: List[ThingToDraw] = []
        self.m_coords = MainCoords((0, 0))

    def draw_all(self, sc: pg.Surface):
        for i in self.things:
            i.draw(self.m_coords.get_one(i), sc)

    def add(self, ttd: ThingToDraw):
        self.things += [ttd]


class Dot(ThingToDraw):
    def __init__(self, pos: Tuple[int, int], name: str):
        super().__init__(pos)
        self.name = name

    def draw(self, pos: Tuple[int, int], sc: pg.Surface):
        pg.draw.circle(sc, col.dot, pos, 5)
        sc.blit(pg.font.Font(None, 24).render(self.name, False, col.dot), (pos[0], pos[1] + 10))


app = App((1600, 1000))

app.drawer.add(Dot((10, 10), '1'))

while True:
    app.tick()




