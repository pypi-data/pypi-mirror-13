#!/usr/bin/env python3

import collections
import enum
import itertools
from typing import List, Mapping, Sequence

import colorama

_enum_value = itertools.count(1)


@enum.unique
class Symbol(enum.Enum):
    Blank = next(_enum_value)

    Triumph = next(_enum_value)
    Success = next(_enum_value)
    Advantage = next(_enum_value)

    Despair = next(_enum_value)
    Failure = next(_enum_value)
    Threat = next(_enum_value)


class Side:
    def __init__(self, symbols: Sequence[Symbol]):
        self.symbols = symbols

    def count_symbol(self, symbol: Symbol) -> int:
        n = 0
        for current_symbol in self.symbols:
            if current_symbol is symbol:
                n += 1
        return n


class Distribution:
    def __init__(self, distribution: Mapping[int, int]=None):
        if distribution is None:
            distribution = {0: 1}
        self._distribution = distribution

    def _total(self) -> int:
        return sum(self._distribution.values())

    def __index__(self, i: int) -> int:
        if i in self._distribution:
            return self._distribution[i]
        else:
            return 0

    def n_non_zeros(self) -> int:
        return len(self._distribution)

    def mean(self) -> float:
        return sum([value * frequency for (value, frequency) in
                    self._distribution.items()]) / self._total()

    def probability_above(self, cutoff: int=0) -> float:
        return sum([frequency for (value, frequency) in self._distribution.items() if
                    value > cutoff]) / self._total()

    def add(self, that: 'Distribution') -> 'Distribution':
        elements = collections.defaultdict(int)
        for (value_i, frequency_i) in self._distribution.items():
            for (value_j, frequency_j) in that._distribution.items():
                value = value_i + value_j
                frequency = frequency_i * frequency_j
                elements[value] += frequency

        return Distribution(elements)


class Rating:
    def __init__(self,
                 triumph: Distribution = Distribution(),
                 success: Distribution = Distribution(),
                 advantage: Distribution = Distribution(),
                 despair: Distribution = Distribution()):
        self.triumph = triumph
        self.success = success
        self.advantage = advantage
        self.despair = despair

    def add(self, that: 'Rating') -> 'Rating':
        new_triumph = self.triumph.add(that.triumph)
        new_success = self.success.add(that.success)
        new_advantage = self.advantage.add(that.advantage)
        new_despair = self.despair.add(that.despair)

        return Rating(new_triumph, new_success, new_advantage, new_despair)

    def __str__(self):
        if self.triumph.mean() > 0.0:
            triumph_color = colorama.Fore.GREEN
        else:
            triumph_color = colorama.Fore.RESET

        if self.success.mean() > 0.0:
            success_color = colorama.Fore.GREEN
        elif self.success.mean() < 0.0:
            success_color = colorama.Fore.RED
        else:
            success_color = colorama.Fore.RESET

        if self.advantage.mean() > 0.0:
            advantage_color = colorama.Fore.GREEN
        elif self.advantage.mean() < 0.0:
            advantage_color = colorama.Fore.RED
        else:
            advantage_color = colorama.Fore.RESET

        if self.despair.mean() > 0.0:
            despair_color = colorama.Fore.RED
        else:
            despair_color = colorama.Fore.RESET

        return ('{9}Rating:\n'
                '\tTriumph: {5}{0}{4} ({5}{10}%{4} for at least 1)\n'
                '\tSuccess: {6}{1}{4} ({6}{11}%{4} for at least 1)\n'
                '\tAdvantage: {7}{2}{4} ({7}{12}%{4} for at least 1)\n'
                '\tDespair: {8}{3}{4} ({8}{13}%{4} for at least 1)'.format(
                    round(self.triumph.mean(), 2),
                    round(self.success.mean(), 2),
                    round(self.advantage.mean(), 2),
                    round(self.despair.mean(), 2),
                    colorama.Fore.RESET,
                    triumph_color,
                    success_color,
                    advantage_color,
                    despair_color,
                    colorama.Style.BRIGHT,
                    round(100 * self.triumph.probability_above(cutoff=0), 0),
                    round(100 * self.success.probability_above(cutoff=0), 0),
                    round(100 * self.advantage.probability_above(cutoff=0), 0),
                    round(100 * self.despair.probability_above(cutoff=0), 0)))


class Dice:
    def __init__(self, sides: Sequence[Side]):
        self._sides = sides

        triumph_mapping = collections.defaultdict(int)
        success_mapping = collections.defaultdict(int)
        advantage_mapping = collections.defaultdict(int)
        despair_mapping = collections.defaultdict(int)
        for side in sides:
            triumph_mapping[side.count_symbol(Symbol.Triumph)] += 1

            success_mapping[(side.count_symbol(Symbol.Success) +
                             side.count_symbol(Symbol.Triumph) +
                             (-1 * side.count_symbol(Symbol.Failure)) +
                             (-1 * side.count_symbol(Symbol.Despair)))] += 1

            advantage_mapping[(side.count_symbol(Symbol.Advantage) +
                               (-1 * side.count_symbol(Symbol.Threat)))] += 1

            despair_mapping[side.count_symbol(Symbol.Despair)] += 1

        self._rating = Rating(
                triumph=Distribution(triumph_mapping),
                success=Distribution(success_mapping),
                advantage=Distribution(advantage_mapping),
                despair=Distribution(despair_mapping))

    def num_sides(self) -> int:
        return len(self._sides)

    @property
    def rating(self) -> Rating:
        return self._rating


class BoostDice(Dice):
    def __init__(self):
        super().__init__(sides=[
            Side(symbols=[Symbol.Blank]),
            Side(symbols=[Symbol.Blank]),
            Side(symbols=[Symbol.Advantage, Symbol.Advantage]),
            Side(symbols=[Symbol.Advantage]),
            Side(symbols=[Symbol.Success, Symbol.Advantage]),
            Side(symbols=[Symbol.Success])
        ])


class AbilityDice(Dice):
    def __init__(self):
        super().__init__(sides=[
            Side(symbols=[Symbol.Blank]),
            Side(symbols=[Symbol.Success]),
            Side(symbols=[Symbol.Success]),
            Side(symbols=[Symbol.Success, Symbol.Success]),
            Side(symbols=[Symbol.Advantage]),
            Side(symbols=[Symbol.Advantage]),
            Side(symbols=[Symbol.Success, Symbol.Advantage]),
            Side(symbols=[Symbol.Advantage, Symbol.Advantage]),
        ])


class ProficiencyDice(Dice):
    def __init__(self):
        super().__init__(sides=[
            Side(symbols=[Symbol.Blank]),
            Side(symbols=[Symbol.Success]),
            Side(symbols=[Symbol.Success]),
            Side(symbols=[Symbol.Success, Symbol.Success]),
            Side(symbols=[Symbol.Success, Symbol.Success]),
            Side(symbols=[Symbol.Advantage]),
            Side(symbols=[Symbol.Success, Symbol.Advantage]),
            Side(symbols=[Symbol.Success, Symbol.Advantage]),
            Side(symbols=[Symbol.Success, Symbol.Advantage]),
            Side(symbols=[Symbol.Advantage, Symbol.Advantage]),
            Side(symbols=[Symbol.Advantage, Symbol.Advantage]),
            Side(symbols=[Symbol.Triumph]),
        ])


class SetbackDice(Dice):
    def __init__(self):
        super().__init__(sides=[
            Side(symbols=[Symbol.Blank]),
            Side(symbols=[Symbol.Blank]),
            Side(symbols=[Symbol.Failure]),
            Side(symbols=[Symbol.Failure]),
            Side(symbols=[Symbol.Threat]),
            Side(symbols=[Symbol.Threat])
        ])


class DifficultyDice(Dice):
    def __init__(self):
        super().__init__(sides=[
            Side(symbols=[Symbol.Blank]),
            Side(symbols=[Symbol.Failure]),
            Side(symbols=[Symbol.Failure, Symbol.Failure]),
            Side(symbols=[Symbol.Threat]),
            Side(symbols=[Symbol.Threat]),
            Side(symbols=[Symbol.Threat]),
            Side(symbols=[Symbol.Threat, Symbol.Threat]),
            Side(symbols=[Symbol.Failure, Symbol.Threat])
        ])


class ChallengeDice(Dice):
    def __init__(self):
        super().__init__(sides=[
            Side(symbols=[Symbol.Blank]),
            Side(symbols=[Symbol.Failure]),
            Side(symbols=[Symbol.Failure]),
            Side(symbols=[Symbol.Failure, Symbol.Failure]),
            Side(symbols=[Symbol.Failure, Symbol.Failure]),
            Side(symbols=[Symbol.Threat]),
            Side(symbols=[Symbol.Threat]),
            Side(symbols=[Symbol.Failure, Symbol.Threat]),
            Side(symbols=[Symbol.Failure, Symbol.Threat]),
            Side(symbols=[Symbol.Threat, Symbol.Threat]),
            Side(symbols=[Symbol.Threat, Symbol.Threat]),
            Side(symbols=[Symbol.Despair])
        ])


@enum.unique
class DiceColor(enum.Enum):
    b = BoostDice
    g = AbilityDice
    y = ProficiencyDice
    k = SetbackDice
    p = DifficultyDice
    r = ChallengeDice

    @classmethod
    def names(cls) -> List[str]:
        names = []
        for dice_color in cls:
            names.append(dice_color.name)
        return names


def dice_from_color_char(color_char: str) -> Dice:
    try:
        dice_color = DiceColor[color_char]
    except KeyError:
        raise ValueError('Invalid dice color: {}.  Possible choices are: {}'.format(
                color_char,
                DiceColor.names()))
    return dice_color.value()


dice_color_to_ansi = {
    DiceColor.b: colorama.Fore.CYAN,
    DiceColor.g: colorama.Fore.GREEN,
    DiceColor.y: colorama.Fore.YELLOW,
    DiceColor.k: colorama.Fore.BLACK + colorama.Back.WHITE,
    DiceColor.p: colorama.Fore.MAGENTA,
    DiceColor.r: colorama.Fore.RED
}


class DicePool:
    def __init__(self, pool: Sequence[Dice]):
        self._pool = pool

    def rating(self) -> Rating:
        rating = Rating()

        for dice in self._pool:
            rating = rating.add(dice.rating)

        return rating

    def __str__(self):
        s = ''
        for dice in self._pool:
            dice_color = DiceColor(type(dice))
            color_code = dice_color_to_ansi[dice_color]

            # Do not turn on bright style for black die as it makes it harder to read.
            brightness_code = colorama.Style.BRIGHT
            if dice_color is DiceColor.k:
                brightness_code = ''
            s += ('{}{}{}{}'.format(brightness_code, color_code, dice_color.name,
                                    colorama.Style.RESET_ALL))
        return s

    @staticmethod
    def _sort_dice_by_power(dice_char: str) -> int:
        try:
            dice_color = DiceColor[dice_char]
            if dice_color is DiceColor.y:
                return 1
            elif dice_color is DiceColor.g:
                return 2
            elif dice_color is DiceColor.b:
                return 3
            elif dice_color is DiceColor.r:
                return 4
            elif dice_color is DiceColor.p:
                return 5
            elif dice_color is DiceColor.k:
                return 6
        except KeyError:
            raise ValueError('Invalid dice character given: {}'.format(dice_char))

    @classmethod
    def from_string(cls, pool_string: str) -> 'DiceColor':
        dice_chars = []
        for char in pool_string:
            dice_chars.append(char)

        dice_chars.sort(key=cls._sort_dice_by_power)
        pool = []
        for dice_char in dice_chars:
            pool.append(dice_from_color_char(dice_char))

        return cls(pool)
