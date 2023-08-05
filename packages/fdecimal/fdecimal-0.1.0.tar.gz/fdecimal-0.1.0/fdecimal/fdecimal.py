# -*- coding: utf-8 -*-

from decimal import Decimal


class FDecimal(Decimal):
    """
    Replacement for Decimal that allows for arithmetic with float values
    """
    def __add__(self, other, context=None):
        if isinstance(other, float):
            other = Decimal(other)
        return super(FDecimal, self).__add__(other, context)
    __radd__ = __add__

    def __sub__(self, other, context=None):
        if isinstance(other, float):
            other = Decimal(other)
        return super(FDecimal, self).__sub__(other, context)
    __rsub__ = __sub__

    def __mul__(self, other, context=None):
        if isinstance(other, float):
            other = Decimal(other)
        return super(FDecimal, self).__mul__(other, context)
    __rmul__ = __mul__

    def __truediv__(self, other, context=None):
        if isinstance(other, float):
            other = Decimal(other)
        return super(FDecimal, self).__truediv__(other, context)
    __rtruediv__ = __truediv__
    __div__ = __truediv__
    __rdiv__ = __rtruediv__
