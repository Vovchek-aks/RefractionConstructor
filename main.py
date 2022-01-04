from typing import List, Tuple
import pygame as pg
import colors as col

import funcs


class App:
    singleton = None

    def __init__(self, size: Tuple[int, int], name: str = 'App'):
        App.singleton = self

        self.size = self.width, self.height = size

        pg.init()

        self.sc = pg.display.set_mode(size)
        self.clock = pg.time.Clock()

        self.drawer = Drawer()
        self.drawer.m_coords = MainCoords((self.width / 2, self.height / 2))

        self.things_to_update: List[ThingToUpdate] = []

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
    def __init__(self):
        App.singleton.things_to_update += [self]

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
    def draw(self, mc: MainCoords, sc: pg.Surface):
        pass


class ThingToRefract(ThingToDraw):
    all_things = []

    def __init__(self, pos: Tuple[float, float]):
        super().__init__(pos)
        ThingToRefract.all_things += [self]


class Drawer:
    singleton = None

    def __init__(self):
        self.things: List[ThingToDraw] = []
        self.m_coords = MainCoords((0, 0))

        Drawer.singleton = self

    def draw_all(self, sc: pg.Surface):
        for i in self.things:
            i.draw(self.m_coords, sc)

    def add(self, ttd: ThingToDraw):
        self.things += [ttd]


class VirtualDot(ThingToDraw):
    def __init__(self, pos: Tuple[float, float], name: str, color: Tuple[int, int, int] = col.dot, real: bool = True):
        super().__init__(pos)
        self.name = name
        self.color = color
        self.real = real

        Drawer.singleton.add(self)

    def draw(self, mc: MainCoords, sc: pg.Surface):
        pos = mc.get_one(self)

        pg.draw.circle(sc, self.color, pos, 5)
        sc.blit(pg.font.Font(None, 24).render(self.name, False, self.color), (pos[0], pos[1] + 10))


class Dot(VirtualDot, ThingToRefract):
    def __init__(self, pos: Tuple[float, float], name: str, color: Tuple[int, int, int] = col.dot, real: bool = True):
        VirtualDot.__init__(self, pos, name, color, real)
        ThingToRefract.__init__(self, pos)


class MouseDot(Dot, ThingToUpdate):
    def __init__(self, pos: Tuple[float, float], name: str, color: Tuple[int, int, int] = col.dot, real: bool = True):
        super().__init__(pos, name)
        VirtualDot.__init__(self, pos, name, color, real)
        ThingToUpdate.__init__(self)

    def update(self, event: pg.event.Event):
        if event.type == pg.MOUSEMOTION:
            p = Drawer.singleton.m_coords.pos
            self.pos = funcs.sum_tuple(pg.mouse.get_pos(), funcs.mult_tuple_num(p, -1))


class MainOpticAxis(ThingToDraw):
    singleton = None

    def __init__(self):
        super().__init__((0, 0))

        dr = Drawer.singleton

        self.focus = VirtualDot((100, 0), 'F', col.milk)
        self.focus2 = VirtualDot((-100, 0), 'F \'', col.milk)
        dr.add(self.focus)
        dr.add(self)

        MainOpticAxis.singleton = self

    def draw(self, mc: MainCoords, sc: pg.Surface):
        pos = mc.get_one(self)

        pg.draw.line(sc, col.milk, (0, pos[1]), (sc.get_width(), pos[1]))
        pg.draw.line(sc, col.milk, (pos[0], pos[1] + 200), (pos[0], pos[1] - 200), 5)

        if self.focus.pos[0] < self.pos[0]:
            pg.draw.line(sc, col.milk, (pos[0] - 20, pos[1] + 200), (pos[0] + 20, pos[1] + 200), 5)


class Line(ThingToRefract):
    def __init__(self, dots: Tuple[Dot, Dot], real: bool = True):
        super().__init__(dots[0].pos)

        Drawer.singleton.add(self)

        self.dots = dots
        self.real = real

    def draw(self, mc: MainCoords, sc: pg.Surface):
        pos1 = mc.get_one(self.dots[0])
        pos2 = mc.get_one(self.dots[1])

        pg.draw.line(sc, col.line, pos1, pos2, 2)


class Refractor:
    @staticmethod
    def refract_all():
        ThingToRefract.all_things = list(filter(lambda x: x.real, ThingToRefract.all_things))

        lines: List[Line] = []
        ndots: List[Dot] = []
        for i in ThingToRefract.all_things.copy():
            if isinstance(i, Line):
                lines += [i]
                continue

            d = Refractor.refract_dot(i)
            if d is not None:
                ndots += [d]

        for line in lines:
            d1 = list(filter(lambda x: x.name == line.dots[0].name + '\'', ndots))[0]
            d2 = list(filter(lambda x: x.name == line.dots[1].name + '\'', ndots))[0]

            Line((d1, d2), False)

    @staticmethod
    def refract_dot(one: Dot) -> (Dot, None):
        # if one.pos[1] == MainOpticAxis.singleton.pos[1]:
        #     raise NotImplementedError('Dot.y = MOA.y')

        fpos = MainOpticAxis.singleton.focus.pos if one.pos[0] < MainOpticAxis.singleton.pos[0] else \
            MainOpticAxis.singleton.focus2.pos

        line1 = (one.pos, MainOpticAxis.singleton.pos)
        line2 = ((MainOpticAxis.singleton.pos[0], one.pos[1]), fpos)

        rdot = funcs.line_intersection(line1, line2)

        # if not rdot[1]:
        #     print(f'dot "{one.name}":{one.pos} have strange refraction {rdot[0]}')

        return Dot(rdot[0], one.name + '\'', col.dot2, False)


app = App((1600, 1000))

MainOpticAxis()

Line((Dot((-150, 100), '1'), Dot((-100, 150), '2')))

MouseDot((-10, 10), '')

while True:
    app.tick()
    Refractor.refract_all()

