from typing import List, Tuple
import pygame as pg
import colors as col

import funcs


class App:
    def __init__(self, size: Tuple[int, int], name: str = 'App'):
        self.size = self.width, self.height = size

        pg.init()

        self.sc = pg.display.set_mode(size)
        self.clock = pg.time.Clock()

        self.drawer = Drawer()
        self.drawer.m_coords.pos = (self.width / 2, self.height / 2)

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
    def __init__(self, pos: Tuple[float, float]):
        self.pos = pos


class MainCoords(Coords):
    def __init__(self, pos: Tuple[float, float]):
        super().__init__(pos)
        self.coords: List[Coords] = []
        self.zoom: float = 1

    def get_one(self, coords: Coords):
        return funcs.mult_tuple_num(funcs.sum_tuple(coords.pos, self.pos), self.zoom)

    def get_all(self):
        return (self.get_one(c) for c in self.coords)


class ThingToDraw(Coords):
    def draw(self, pos: Tuple[float, float], sc: pg.Surface):
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
    def __init__(self, pos: Tuple[float, float], name: str, color: Tuple[int, int, int] = col.dot):
        super().__init__(pos)
        self.name = name
        self.color = color

    def draw(self, pos: Tuple[float, float], sc: pg.Surface):
        pg.draw.circle(sc, self.color, pos, 5)
        sc.blit(pg.font.Font(None, 24).render(self.name, False, self.color), (pos[0], pos[1] + 10))


class MainOpticAxis(ThingToDraw):
    def __init__(self, dr: Drawer):
        super().__init__((0, 0))

        self.focus = Dot((100, 0), 'F', col.milk)
        dr.add(self.focus)
        dr.add(self)

    def draw(self, pos: Tuple[float, float], sc: pg.Surface):
        pg.draw.line(sc, col.milk, (0, pos[1]), (sc.get_width(), pos[1]))


app = App((1600, 1000))

MainOpticAxis(app.drawer)

app.drawer.add(Dot((100, 100), '1'))

app.drawer.m_coords.zoom = 1

while True:
    app.tick()




