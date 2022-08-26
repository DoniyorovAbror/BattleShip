from random import randint


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f'{self.x}, {self.y}'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class GameException(Exception):
    pass


class OutBoardFireException(GameException):
    def __str__(self):
        return f'координаты не верны для выстрела'


class BoardUsedException(GameException):
    def __str__(self):
        return f'в эту точку уже стреляли '


class OutOfAreaException(GameException):
    pass


class Ship:

    def __init__(self, ship_coords, ship_length, orient):
        self.ship_coords = ship_coords
        self.ship_length = ship_length
        self.orient = orient
        self.health = ship_length

    @property
    def _ship_dots(self):
        self.ship_array = []

        for i in range(self.ship_length):
            _x = self.ship_coords.x
            _y = self.ship_coords.y

            if self.orient:
                _x += i
            else:
                _y += i

            self.ship_array.append(Dot(_x, _y))

        return self.ship_array

    def fired(self, fire):
        return fire in self._ship_dots


class BattleArea:

    def __init__(self, hidden=False):
        self.busy = []
        self.ship_coords = []
        self.size = 6
        self.hidden = hidden
        self.cnt = 0

        self.r = []
        self.r = [['~'] * 6 for i in range(self.size)]

    def add_ships(self, _ships):

        for i in _ships._ship_dots:
            if not (0 <= i.x < 6 > i.y >= 0) or i in self.busy:
                raise OutOfAreaException()
        for i in _ships._ship_dots:
            self.r[i.x][i.y] = '■'
            self.busy.append(i)

        self.ship_coords.append(_ships)
        self.zone_around_ship(_ships)

    def __str__(self):
        lines = f'  1 2 3 4 5 6'
        for i, j in enumerate(self.r):
            lines += f'\n{i + 1} ' + ' '.join(j)
        if self.hidden:
            lines = lines.replace('■', '~')
        return lines

    def clear(self):
        self.busy = []

    def out(self, dots):
        return not (0 <= dots.x < 6 > dots.y >= 0)

    def shot(self, dots):
        if self.out(dots):
            raise OutBoardFireException()

        if dots in self.busy:
            raise BoardUsedException()

        self.busy.append(dots)

        for ship in self.ship_coords:
            if dots in ship._ship_dots:
                ship.health -= 1
                self.r[dots.x][dots.y] = "X"
                if ship.health == 0:
                    self.cnt += 1
                    self.zone_around_ship(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("попали, но не уничтожили")
                    return True

        self.r[dots.x][dots.y] = "."
        print("Мимо!")
        return False

    def zone_around_ship(self, array, verb=False):
        around = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 0), (0, 1),
                  (1, -1), (1, 0), (1, 1)]
        for i in array._ship_dots:
            for i_x, i_y in around:
                current = Dot(i.x + i_x, i.y + i_y)
                if (0 <= current.x < 6 > current.y >= 0) and current not in self.busy:
                    if verb:
                        self.r[current.x][current.y] = '.'
                    self.busy.append(current)


class Turn:
    def __init__(self, board, enem):
        self.b = board
        self.e = enem

    def ask(self):  # Обязательно создать в экземпляре класса этот метод
        raise NotImplementedError()

    def turn(self):
        while True:
            try:
                target = self.ask()
                repeat = self.e.shot(target)
                return repeat
            except GameException as e:
                print(e)


class USER(Turn):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите x y координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите число! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class CPU(Turn):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class Game:
    def __init__(self):
        player = self.try_make_board()
        comp = self.try_make_board()
        comp.hidden = True
        self.cpu = CPU(comp, player)
        self.user = USER(player, comp)

    def try_make_board(self):
        board = None
        while board is None:
            board = self.random_ships()
        return board

    def random_ships(self):
        battle_area = BattleArea()
        count_ships = [3, 2, 2, 1, 1, 1, 1]
        retry = 1
        for ship in count_ships:
            while True:
                retry += 1
                if retry > 2000:
                    return None
                _orient = randint(0, 1)
                _ship = Dot(randint(0, 6), randint(0, 6))
                ship_length = ship
                x_y = Ship(_ship, ship_length, _orient)
                try:
                    battle_area.add_ships(x_y)
                    break
                except OutOfAreaException:
                    pass
        battle_area.clear()
        return battle_area

    def greet(self):
        print('-' * 20)
        print('  Игра Морской Бой')
        print('-' * 20)
        print('   нужно вводить\n   координаты X Y')
        print('   x - Строка')
        print('   Y - Столбец')

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Карта пользователя:")
            print(self.user.b)
            print("-" * 20)
            print("Карта компьютера:")
            print(self.cpu.b)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.user.turn()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.cpu.turn()
            if repeat:
                num -= 1

            if self.cpu.b.cnt == 7:
                print("-" * 20)
                print(self.cpu.b)
                print("Пользователь выиграл!")
                break

            if self.user.b.cnt == 7:
                print("-" * 20)
                print(self.user.b)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


b = Game()
b.start()
