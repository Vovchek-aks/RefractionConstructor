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
        self.drawer.m_coords = MainCoords((self.width / 2, self.height / 2))

        self.things_to_update: List[ThingToUpdate] = [self.drawer.m_coords]

    def update(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                exit(0)

            for ttu in self.things_to_update:
                ttu.update(event)

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


class ThingToUpdate:
    def update(self, event: pg.event.Event):
        pass


class MainCoords(Coords, ThingToUpdate):
    keys_to_vectrors = {
        pg.K_UP: (0, 1),
        pg.K_DOWN: (0, -1),
        pg.K_RIGHT: (-1, 0),
        pg.K_LEFT: (1, 0)
    }

    def __init__(self, pos: Tuple[float, float]):
        super().__init__(pos)
        self.coords: List[Coords] = []
        self.zoom: float = 1

        self.start_pos = pos

    def get_one(self, coords: Coords):
        return funcs.mult_tuple_num(funcs.sum_tuple(coords.pos, self.pos), self.zoom)

    def get_all(self):
        return (self.get_one(c) for c in self.coords)

    def update(self, event: pg.event.Event):
        if event.type == pg.KEYDOWN:
            if event.key in MainCoords.keys_to_vectrors:
                delta = funcs.mult_tuple_num(MainCoords.keys_to_vectrors[event.key], 50 / self.zoom)
                self.pos = funcs.sum_tuple(self.pos, delta)

            elif event.key in {pg.K_PAGEDOWN, pg.K_PAGEUP}:
                self.zoom += .3 * (1 if event.key == pg.K_PAGEUP else -1)

            elif event.key == pg.K_HOME:
                self.pos = self.start_pos
                self.zoom = 1


class ThingToDraw(Coords):
    def draw(self, pos: Tuple[float, float], sc: pg.Surface):
        pass


class Drawer:
    singleton = None

    def __init__(self):
        self.things: List[ThingToDraw] = []
        self.m_coords = MainCoords((0, 0))

        Drawer.singleton = self

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

        Drawer.singleton.add(self)

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
        pg.draw.line(sc, col.milk, (pos[0], pos[1] + 200), (pos[0], pos[1] - 200), 5)

        if self.focus.pos[0] < self.pos[0]:
            pg.draw.line(sc, col.milk, (pos[0] - 20, pos[1] + 200), (pos[0] + 20, pos[1] + 200), 5)


app = App((1600, 1000))

MainOpticAxis(app.drawer)

Dot((100, 100), '1')

while True:
    app.tick()




