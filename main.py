from typing import List, Tuple
import pygame as pg
import json

import funcs
import colors as col


class App:
    singleton = None

    def __init__(self, size: Tuple[int, int]):
        App.singleton = self

        self.size = self.width, self.height = size

        pg.init()

        self.sc = pg.display.set_mode(size)
        self.clock = pg.time.Clock()

        self.drawer = Drawer()
        self.drawer.m_coords = MainCoords((self.width / 2, self.height / 2))

        self.im = InputManager()

    def update(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                exit(0)

            for ttu in Thing.get(update=True):
                ttu.update(event)

        pg.display.set_caption(str(self.drawer.m_coords.zoom) + ' ' + str(self.im.m.pos))

    def draw(self):
        self.sc.fill(col.background)
        self.drawer.draw_all(self.sc)

        pg.display.flip()

    def tick(self):
        Refractor.del_all_not_real_shit()
        self.update()
        Refractor.refract_all()
        self.draw()

        self.clock.tick(60)


class Thing:
    things = set()

    def __init__(self, draw=False, update=False, refract=False):
        self.need_to_draw = draw
        self.need_to_update = update
        self.need_to_refract = refract

        Thing.things.add(self)

    def die(self):
        if self in Thing.things:
            Thing.things.remove(self)

    @staticmethod
    def get(draw=None, update=None, refract=None):
        return list(filter(lambda x: (draw is None or x.need_to_draw == draw) and
                                     (update is None or x.need_to_update == update) and
                                     (refract is None or x.need_to_refract == refract), Thing.things))


class InputManager(Thing):
    def __init__(self):
        Thing.__init__(self, update=True)

        self.m = MouseDot((10, 10), '')

        self.moa = MainOpticAxis()

    def update(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_m:
                self.m.need_to_draw *= -1
                self.m.need_to_refract *= -1
            elif event.key == pg.K_SPACE:
                try:
                    self.input()
                except:
                    print('ошибка')

    @staticmethod
    def save(name: str):
        ts = []
        for i in sorted(filter(lambda x: x.__class__ in (Dot, Line) and x.real, Thing.get(draw=True, refract=True)),
                        key=lambda x: (Dot, Line).index(x.__class__)):
            if i.__class__ == Dot:
                ts += [[i.name, list(i.pos)]]
            else:
                ts += [[list(i.dots[0].pos), list(i.dots[1].pos)]]

        open(f'saves/{name}.json', 'w', encoding='UTF-8').write(json.dumps(ts))

    @staticmethod
    def load(name: str):
        ts = json.load(open(f'saves/{name}.json', encoding="UTF-8"))
        dots = dict()
        for i in ts:
            if i[0].__class__ == str:
                dots[tuple(i[1])] = Dot(tuple(i[1]), i[0])
            else:
                Line((dots[tuple(i[0])], dots[tuple(i[1])]))

    def input(self):
        print('\n\nВыбор действия')
        print('0 - переместить фокус')
        print('1 - добавить точку')
        print('2 - переместить точку')
        print('3 - удалить точку')
        print('4 - соединить точки')
        print('5 - разединить точки')
        print('6 - добавить промежуточные точки')
        print('7 - сохранить')
        print('8 - загрузить')
        n = input().strip()

        if n == '0':
            print('введите новое значение F')

            self.moa.update_f(float(input().strip()))
        elif n == '1':
            print('введите координаты новой точки через пробел')
            pos = tuple(float(i) for i in input().strip().split())
            pos = pos[0], pos[1]
            print('введите имя точки')
            name = input().strip()

            if not name:
                raise NameError()

            Dot(pos, name)
        elif n == '2':
            print('введите имя точки')
            name = input().strip()
            print('введите новые координаты точки через пробел')
            pos = tuple(float(i) for i in input().strip().split())

            tuple(filter(lambda x: isinstance(x, Dot) and x.name == name,
                         Thing.get(draw=True, refract=True)))[0].pos = pos
        elif n == '3':
            print('введите имя точки')
            name = input().strip()

            for i in filter(lambda x: isinstance(x, Dot) and x.name == name,
                            Thing.get(draw=True, refract=True)):
                i.die()
        elif n == '4':
            print('введите имена точек')
            names = input().strip().split()

            ShapeGenerator.make_polygon(sorted(
                filter(lambda x: x.__class__ == Dot and x.name in names,
                       Thing.get(draw=True, refract=True)), key=lambda x: names.index(x.name)))

        elif n == '5':
            print('введите имена 2 точек')
            names = input().strip().split()[:2]

            for i in filter(lambda x: isinstance(x, Line) and
                            x.dots[0].name in names and
                            x.dots[1].name in names,
                            Thing.get(draw=True, refract=True)):
                i.die()
        elif n == '6':
            print('введите имена 2 точек')
            names = input().strip().split()[:2]
            print('на сколько частей разделить отрезок?')
            n = int(input().strip())

            line = tuple(filter(lambda x: isinstance(x, Line) and
                                x.dots[0].name in names and
                                x.dots[1].name in names,
                                Thing.get(draw=True, refract=True)))[0]
            ShapeGenerator.line_divider(line, n)
        elif n == '7':
            print('введите название файла')

            InputManager.save(input().strip())
        elif n == '8':
            print('введите название файла')

            InputManager.load(input().strip())
        else:
            raise Exception()

        print('успех')


class Coords:
    def __init__(self, pos: Tuple[float, float]):
        self.pos = pos


class MainCoords(Coords, Thing):
    keys_to_vectrors = {
        pg.K_UP: (0, 1),
        pg.K_DOWN: (0, -1),
        pg.K_RIGHT: (-1, 0),
        pg.K_LEFT: (1, 0)
    }

    def __init__(self, pos: Tuple[float, float]):
        Coords.__init__(self, pos)
        Thing.__init__(self, update=True)

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
                delta = funcs.mult_tuple_num(MainCoords.keys_to_vectrors[event.key], 150 / self.zoom)
                self.pos = funcs.sum_tuple(self.pos, delta)

            elif event.key in {pg.K_PAGEDOWN, pg.K_PAGEUP}:
                self.zoom *= (2 if event.key == pg.K_PAGEUP else 1 / 2)

            elif event.key == pg.K_HOME:
                self.pos = self.start_pos
                self.zoom = 1


class Drawer:
    singleton = None

    def __init__(self):
        self.m_coords: (MainCoords, None) = None

    def draw_all(self, sc: pg.Surface):
        for i in sorted(Thing.get(draw=True), key=lambda x: 0 if x.__class__ == Line else 1):
            i.draw(self.m_coords, sc)


class VirtualDot(Coords, Thing):
    def __init__(self, pos: Tuple[float, float], name: str, color: Tuple[int, int, int] = col.dot, real: bool = True):
        Coords.__init__(self, pos)
        Thing.__init__(self, draw=True)
        self.name = name
        self.color = color
        self.real = real

    def draw(self, mc: MainCoords, sc: pg.Surface):
        pos = mc.get_one(self)

        pg.draw.circle(sc, self.color, pos, 5)
        sc.blit(pg.font.Font(None, 24).render(self.name, False, self.color), (pos[0], pos[1] + 10))

    def __repr__(self):
        return f'Dot({self.name}:{self.pos}:real={self.real})'


class Dot(VirtualDot):
    def __init__(self, pos: Tuple[float, float], name: str = '', color: Tuple[int, int, int] = col.dot,
                 real: bool = True):
        VirtualDot.__init__(self, pos, name, color, real)
        self.need_to_refract = True

    def die(self):
        Thing.die(self)

        for i in filter(lambda x: isinstance(x, Line) and
                        self in x.dots,
                        Thing.get(draw=True, refract=True)):
            i.die()


class MouseDot(Dot):
    def __init__(self, pos: Tuple[float, float], name: str, color: Tuple[int, int, int] = col.dot, real: bool = True):
        Dot.__init__(self, pos, name, color, real)
        self.need_to_update = True

    def update(self, event: pg.event.Event):
        if event.type == pg.MOUSEMOTION:
            p = App.singleton.drawer.m_coords
            self.pos = funcs.sum_tuple(pg.mouse.get_pos(), funcs.mult_tuple_num(p.pos, -1))


class MainOpticAxis(Coords, Thing):
    singleton = None

    def __init__(self):
        Coords.__init__(self, (0, 0))
        Thing.__init__(self, draw=True)

        self.focus = VirtualDot((100, 0), 'F', col.milk)
        self.focus2 = VirtualDot((-self.focus.pos[0], 0), 'F \'', col.milk)

        MainOpticAxis.singleton = self

    def draw(self, mc: MainCoords, sc: pg.Surface):
        pos = mc.get_one(self)

        pg.draw.line(sc, col.milk, (0, pos[1]), (sc.get_width(), pos[1]))
        pg.draw.line(sc, col.milk, (pos[0], pos[1] + 200), (pos[0], pos[1] - 200), 5)

        if self.focus.pos[0] < self.pos[0]:
            pg.draw.line(sc, col.milk, (pos[0] - 20, pos[1] + 200), (pos[0] + 20, pos[1] + 200), 5)
            pg.draw.line(sc, col.milk, (pos[0] - 20, pos[1] - 200), (pos[0] + 20, pos[1] - 200), 5)

    def update_f(self, x: float):
        self.focus.pos = x, 0
        self.focus2.pos = -x, 0


class Line(Thing):
    def __init__(self, dots: Tuple[Dot, Dot], real: bool = True):
        Thing.__init__(self, draw=True, refract=True)

        self.dots = dots
        self.real = real

    def draw(self, mc: MainCoords, sc: pg.Surface):
        pos1 = mc.get_one(self.dots[0])
        pos2 = mc.get_one(self.dots[1])

        pg.draw.line(sc, col.line, pos1, pos2, 2)

    def __repr__(self):
        return f'Line({self.dots[0].__repr__()}, {self.dots[1].__repr__()})'


class ShapeGenerator:
    @staticmethod
    def make_polygon(dots: List[Dot]) -> None:
        if len(dots) < 2:
            return

        f = dots[0]
        for d in dots[1:]:
            Line((f, d))
            f = d

        Line((dots[0], dots[-1]))

    @staticmethod
    def line_divider(line: Line, n: int):
        d1, d2 = line.dots

        line.die()
        del line

        delta = funcs.mult_tuple_num(funcs.sum_tuple(d2.pos, funcs.mult_tuple_num(d1.pos, -1)), 1 / n)

        f = d1
        for i in range(n - 1):
            d = Dot(funcs.sum_tuple(f.pos, delta))
            Line((f, d))
            f = d

        Line((f, d2))


class Refractor:
    @staticmethod
    def refract_all():
        dots = dict().copy()

        shit = Thing.get(refract=True).copy()
        shit.sort(key=lambda x: 0 if isinstance(x, Line) else 1)

        while shit:
            s = shit[0]
            if isinstance(s, Line):
                d1, d2 = s.dots

                if d1 in shit:
                    p = d1.pos
                    shit.remove(d1)
                    d1 = Refractor.refract_dot(d1)
                    dots[p] = d1
                else:
                    d1 = dots[d1.pos]

                if d2 in shit:
                    p = d2.pos
                    shit.remove(d2)
                    d2 = Refractor.refract_dot(d2)
                    dots[p] = d2
                else:
                    d2 = dots[d2.pos]

                Line((d1, d2), real=False)
            else:
                Refractor.refract_dot(s)

            shit = shit[1:]

    @staticmethod
    def refract_dot(one: Dot) -> (Dot, None):
        p = one.pos
        if one.pos[1] == MainOpticAxis.singleton.pos[1]:
            p = (one.pos[0], one.pos[1] + 10 ** -3)

        fpos = MainOpticAxis.singleton.focus.pos if p[0] < MainOpticAxis.singleton.pos[0] else \
            MainOpticAxis.singleton.focus2.pos

        line1 = (p, MainOpticAxis.singleton.pos)
        line2 = ((MainOpticAxis.singleton.pos[0], p[1]), fpos)

        rdot = funcs.line_intersection(line1, line2)

        return Dot(rdot[0], one.name + ('\'' if one.name else ''), col.dot2, real=False)

    @staticmethod
    def del_all_not_real_shit():
        for i in Thing.get(refract=True):
            if not i.real:
                i.die()


try:
    app = App((1600, 1000))

    ShapeGenerator.make_polygon([Dot((-200, 100), '1'), Dot((-350, 100), '2'), Dot((-200, -100), '3')])

    while True:
        app.tick()
except:
    while True:
        input('ПРОИЗОШЛА НЕИЗВЕСТНАЯ ОШИБКА')
