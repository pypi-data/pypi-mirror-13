#!/usr/bin/env python
# encoding: utf8

# Copyright (C) 2015 by Roy Levien.
# This file is part of crypto-enigma, an Enigma Machine simulator.
# released under the BSD-3 License (see LICENSE.txt).

"""
This is a supporting module that implements the simple substitution cypher employed by the Enigma machine to
encode messages. It will not generally be used directly.
"""

from __future__ import (absolute_import, print_function, division, unicode_literals)

from .utils import *


# A note on the use of string indexing to implement encryption:
# Improvements from implementing mappings as lists of numbers rather than strings are negligible and not worth the
# loss of clarity and correspondence to the underlying math.


# TBD - Fix encapsulation here; sould not be used by other modules (e.g., reversed encoding should start with mapping) <<<
def num_A0(c):
    return ord(c) - ord('A')


def chr_A0(n):
    return chr(n + ord('A'))


class Mapping(unicode):
    """A substitution cypher mapping.

    The Enigma machine, and the components from which it is constructed, use **mappings** to perform a
    `simple substitution encoding`_. Mappings describe

    * the cryptographic effects of each component's fixed `~.components.Component.wiring`;
    * the encoding they perform individually in a machine based on their rotational `~EnigmaConfig.positions` and
      the direction in which a signal passes through them (see `~.components.Component.mapping`); and,
    * the progressive (`~EnigmaConfig.stage_mapping_list`) and overall (`~EnigmaConfig.enigma_mapping_list`
      and `~EnigmaConfig.enigma_mapping`) encoding performed by the machine as a whole.

    """

    def __init__(self, str):
        """Mappings are  expressed as a string of letters indicating the mapped-to letter
        for the letter at that position in the alphabet — i.e., as a permutation of the alphabet.
        For example, the mapping **EKMFLGDQVZNTOWYHXUSPAIBRCJ** encodes
        **A** to **E**, **B** to **K**, **C** to **M**, ..., **Y** to **C**, and **Z** to **J**:

        >>> mpg = Mapping(u'EKMFLGDQVZNTOWYHXUSPAIBRCJ')
        >>> mpg.encode_string(u'ABCYZJ')
        u'EKMCJZ'
        >>> mpg.encode_string(u'ABCDEFGHIJKLMNOPQRSTUVWXYZ') == mpg
        True

        Note that there is no way to directly create `Mapping` for use by an `EnigmaMachine` or `Component`.
        The closest one can get is to configure a plugboard with `component`:

        >>> component(u'AE.BK.CM.FD').wiring # doctest: +ELLIPSIS
        u'EKMF...'

        """
        super(Mapping, self).__init__()
        self._len = len(self)

    # standard simple-substitution cypher encoding
    def encode_char(self, ch):
        """Encode a single character using the mapping.

        Args:
            ch (char):  A character to encode using the `Mapping`.

        Returns:
            chr: The character, replaced with the corresponding characters in the `Mapping`.

        Example:
            In the context of this package, this is most useful in low level analysis of the encoding process:

            >>> wng = component(u'AE.BK.CM.FD').wiring
            >>> wng.encode_char(u'A')
            u'E'
            >>> wng.encode_char(u'K')
            u'B'
            >>> wng.encode_char(u'Q')
            u'Q'

            For example, it can be used to confirm that only letters connected in a plugboard are unaltered
            by the encoding it performs:

            >>> pbd = component(u'AE.BK.CM.FD')
            >>> all(pbd.wiring.encode_char(c) == c for c in filter(lambda c: c not in pbd.name,  u'ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
            True
            >>> all(pbd.wiring.encode_char(c) != c for c in filter(lambda c: c in pbd.name,  u'ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
            True

        """
        if 0 <= num_A0(ch) < self._len:
            return self[num_A0(ch)]
        else:
            return ' '

    def encode_string(self, string):
        """Encode a string using the mapping.

        Args:
            string (str):  A string to encode using the `Mapping`.

        Returns:
            str: A string consisting of each of the characters replaced with the corresponding
                character in the `Mapping`.

        Examples:
            This just the collected results of applying `encode_char` to each letter of the string:

            >>> component(u'AE.BK.CM.FD').wiring.encode_string(u'ABKCFEKMD')
            u'EKBMDABCF'
            >>> ''.join(component(u'AE.BK.CM.FD').wiring.encode_char(c) for c in u'ABKCFEKMD')
            u'EKBMDABCF'

            Note that, critically, the mapping used by an Enigma machine *changes before each character is encoded*
            so that:

             .. testsetup::

                cfg = EnigmaConfig.config_enigma(u"B-I-II-III", u"ABC", u"XO.YM.QL", u"01.02.03")
                str=u'ABKCJFIRUFDLSLKFDHLSJHFLSDJFHLJSDHFLSJDFHSLDJFHSLDFJHSFEKMD'

            >>> cfg.enigma_mapping().encode_string(str) != cfg.enigma_encoding(str)
            True

        """
        return ''.join([self.encode_char(ch) for ch in string])