"""Choose construction references for every text glyph in the magnified proof."""

import unicodedata

from thin_figures import DIGITS, FIGURES, FRACTIONS

GROUPS = [
    "A V W M N X Y K",
    "C G O Q D",
    "B P R D",
    "E F H I L T",
    "J U",
    "S Z",
    "a e s c o",
    "b d p q o",
    "m n h r u",
    "f t l i j",
    "g y j",
    "k x v w z",
    "AE A E OE O",
    "ae a e oe o",
    "Eth Dcroat D",
    "eth dcroat d",
    "Thorn P B",
    "thorn b p",
    "IJ I J",
    "ij i j",
    "Ldot Lslash L",
    "ldot lslash l",
    "Hbar H Tbar",
    "hbar h tbar",
    "Eng N J",
    "eng n j",
    "Germandbls B S",
    "germandbls f s",
    "longs f t",
    "zero six eight nine",
    "two three five eight",
    "one four seven",
    "period periodcentered bullet colon ellipsis",
    "comma semicolon quotesinglbase quotedblbase",
    "exclam exclamdown question questiondown",
    "quotesingle quotedbl minute second",
    "quoteleft quoteright quotedblleft quotedblright",
    "space nbspace thinspace narrownbspace",
    "hyphen nonbreakinghyphen softhyphen endash emdash underscore minus",
    "parenleft parenright braceleft braceright",
    "bracketleft bracketright",
    "uni27E8 uni27E9 less greater",
    "slash backslash fraction bar brokenbar uni2016",
    "less greater guilsinglleft guilsinglright",
    "guillemotleft guillemotright guilsinglleft guilsinglright",
    "dagger daggerdbl plus",
    "asciicircum asciitilde circumflex tilde",
    "hyphentwo equal approxequal",
    "plus minus plusminus divide equal",
    "lessequal greaterequal notequal equal",
    "multiply asterisk ballotx",
    "checkmark radical",
    "percent perthousand degree",
    "at copyright registered trademark uni24B9",
    "uni20BE uni20BC uni20AA H",
    "uni20B4 S dollar",
    "uni20BF uni0E3F B",
    "uni20B2 G uni20B5 C",
    "uni20B5 uni20A1 C",
    "uni20A6 N H",
    "uni20AD K",
    "uni20AE uni20B8 T",
    "uni20BA L",
    "uni20AB dcroat",
    "uni20A8 R s",
    "uni20B1 ruble P",
    "sterling euro cent C",
    "yen Y won W",
    "rupee R",
    "currency circle",
    "section paragraph S",
    "numbersign H equal",
    "pi n m",
    "Delta increment A",
    "Omega ohm O",
    "partialdiff d",
    "emptyset Oslash O",
    "product H",
    "summation Z",
    "integral uni2113 f",
    "infinity eight",
    "micro u",
    "ordfeminine a",
    "ordmasculine o",
    "uni212E e",
    "Oslash O Q",
    "oslash o",
    "kgreenlandic k x",
    "dotlessi i",
    "dotlessj j",
    "napostrophe n",
    "ampersand eight S",
    "filledbox whitesquare uni25AA uni25AB",
    "triagup uni25B3 triagdn uni25BD",
    "uni25B4 uni25B5 uni25BE uni25BF",
    "uni25B6 uni25B7 uni25C0 uni25C1",
    "uni25B8 uni25B9 uni25C2 uni25C3",
    "uni25C6 uni25C7 lozenge",
    "circle uni25CF openbullet degree",
]
GROUPS = [g.split() for g in GROUPS]


def reference_names(font):
    order = font.getGlyphOrder()
    available = set(order)
    cp = {n: c for c, n in font.getBestCmap().items()}
    result = {}
    for n in order:
        glyph = font["glyf"][n]
        candidates = list(
            {
                "won": ("W", "numbersign"),
                "X": ("x", "multiply"),
                "x": ("X", "multiply"),
                "multiply": ("X", "x"),
                "a": ("ae", "aacute"),
                "ae": ("a", "oe"),
                "oe": ("o", "ae"),
                "less.lig_le": ("lessequal", "greater.lig_ge"),
                "equal.lig_le": ("lessequal", "equal.lig_ge"),
                "greater.lig_ge": ("greaterequal", "less.lig_le"),
                "equal.lig_ge": ("greaterequal", "equal.lig_le"),
                "germandbls": ("Germandbls", "s"),
                "Germandbls": ("germandbls", "S"),
                "Oslash": ("O", "oslash"),
                "oslash": ("o", "Oslash"),
                "uni20BE": ("uni20BC", "C"),
                "six.tnum": ("six", "nine.tnum"),
                "numbersign": ("H", "equal"),
            }.get(n, ())
        )
        base = n.split(".")[0]
        if glyph.isComposite():
            candidates.extend(c.glyphName for c in glyph.components)
        if n != base:
            candidates.append(base)
        if n in FIGURES or base in DIGITS:
            digit = FIGURES[n] if n in FIGURES else DIGITS.index(base)
            number = DIGITS[digit]
            candidates.append(number)
            if n == number or ".tnum" in n:
                candidates.append(number + ".tnum")
            else:
                candidates.extend(
                    k
                    for k, v in FIGURES.items()
                    if v == digit
                    and k != n
                    and k.startswith("uni208") != n.startswith("uni208")
                    and (k.startswith("uni20") or k.endswith("superior"))
                )
        if n in FRACTIONS:
            a, b = FRACTIONS[n]
            candidates += [DIGITS[a], DIGITS[b], "fraction"]
        if "comb" in n:
            candidates.extend(
                (base.removesuffix("comb"), base + ".cap", base.replace("dotaccent", "dieresis"))
            )
        if base + "comb" in available:
            candidates.append(base + "comb")
        code = cp.get(n, 0)
        if 0x2500 <= code <= 0x257F:
            candidates += [f"uni{0x2500 + ((code - 0x2500) ^ 1):04X}", "uni2500", "uni2502"]
        elif 0x2580 <= code <= 0x259F:
            candidates += [f"uni{0x2580 + ((code - 0x2580) ^ 1):04X}", "uni2588", "uni2580"]
        elif ".lig_" in n:
            candidates += [x for x in order if ".lig_" in x and x.split(".lig_")[1] == n.split(".lig_")[1]]
        elif code and ("ARROW" in unicodedata.name(chr(code), "") or n.startswith("arrow")):
            candidates += ["arrowright", "arrowleft", "arrowup"]
        for group in GROUPS:
            if n in group or base in group:
                candidates.extend(group)
                break
        # Prefer a sibling with the same base over an unrelated fallback.
        if len(set(candidates) - {n, ""}) < 2:
            candidates.extend(x for x in order if x != n and x.split(".")[0] == base)
        if code and len(set(candidates) - {n, ""}) < 2:
            category = unicodedata.category(chr(code))
            candidates.extend(
                sorted(
                    (x for x, c in cp.items() if unicodedata.category(chr(c)) == category),
                    key=lambda x: abs(cp[x] - code),
                )
            )
        candidates += ["H", "O", "period"]
        result[n] = list(dict.fromkeys(x for x in candidates if x in available and x != n))[:2]
    return result
