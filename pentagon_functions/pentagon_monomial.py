import functools
import operator
import re

from collections import defaultdict
from multiset import FrozenMultiset


class PentagonMonomial(FrozenMultiset):

    def __init__(self, pentagons_and_powers={}):
        if isinstance(pentagons_and_powers, (dict, tuple, FrozenMultiset, PentagonMonomial)):
            super(PentagonMonomial, self).__init__(pentagons_and_powers)
        elif isinstance(pentagons_and_powers, str):
            super(PentagonMonomial, self).__init__(self.__rstr__(pentagons_and_powers))
        elif isinstance(pentagons_and_powers, bytes):
            super(PentagonMonomial, self).__init__(self.__rstr__(pentagons_and_powers.decode("utf-8").replace("\n", "")))
        else:
            print("entry:", repr(pentagons_and_powers))
            print("type:", type(pentagons_and_powers))
            raise NotImplementedError

    @staticmethod
    def __rstr__(monomial):
        if monomial == '' or monomial == '1':
            return dict()
        monomial = monomial.replace("/sqrtG3[1]", "*one_over_sqrtG3[1]").replace("/sqrtG3[2]", "*one_over_sqrtG3[2]")
        monomial = monomial.replace("/sqrtG3[3]", "*one_over_sqrtG3[3]").replace("(", "").replace(")", "")
        factors = monomial.split('*')
        factor_groups = defaultdict(list)
        for factor in factors:
            if '^' in factor:
                function, power = factor.split('^')
                power = int(power)
            else:
                function = factor
                power = 1
            factor_groups[function].append(power)
        powers = [(function, sum(powers)) for function, powers in factor_groups.items()]
        return dict(powers)

    def __repr__(self):
        return super(PentagonMonomial, self).__repr__()

    def __str__(self):
        if self == FrozenMultiset():
            return '1'
        return "*".join([f"{key}^{val}" if val != 1 else f"{key}" for key, val in self.items()])

    @property
    def weight(self):
        return sum([int(re.findall(r"\[(\d+)", key)[0]) * val if re.findall(r"\[(\d+)", key) != [] else 0
                    for key, val in self.items()])

    def subs(self, pentagons_dict):
        return functools.reduce(operator.mul, [pentagons_dict[key] ** val for key, val in self.items()], 1)

    # Ordering

    @functools.cached_property
    def canonical_ordering(self):
        """Orders monomials by the following criterea"""
        if self.weight == 0:
            return (0, )
        criterea = (
            # by weight
            (self.weight, ) + tuple([
                # lexicographically on the pentagon function name, e.g. F's before im's before re's
                (key.split("[")[0], ) +
                # by indices of the pentagon functions, e.g. F[1,1] before F[1,2] before F[1,10]
                # and with small powers first
                tuple(map(int, re.findall(r"(\d+)", key))) + (-val, ) for key, val in self.items()])
        )
        return criterea

    def __lt__(self, other):
        return (self.canonical_ordering < other.canonical_ordering)

    def __le__(self, other):
        return (self.canonical_ordering <= other.canonical_ordering)

    def __gt__(self, other):
        return (self.canonical_ordering > other.canonical_ordering)

    def __ge__(self, other):
        return (self.canonical_ordering >= other.canonical_ordering)
