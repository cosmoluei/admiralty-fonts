"""
Aggregates all Milestone 3 glyph builders & OpenType features for Admiralty Sans Regular:
  - Uppercase A-Z, Lowercase a-z, Numerals (proportional, tabular, slashed zero)
  - Basic Latin & Typographic Punctuation, Currencies, Math, Superscripts/Fractions
  - Latin-1 Supplement & GF Latin Core Base Letters, Combining Marks, Chat UI Arrows
  - OpenType features: ccmp, locl, lnum, pnum, tnum, zero, case (+ ufo2ft kern, mark, mkmk)
"""

from __future__ import annotations
from typing import Callable, Dict, List, Tuple

from design_system import (
    ContourBuilder,
    DUPLEX_ADVANCE_WIDTHS,
    SANS_REGULAR,
    UNICODE_MAP,
    SansWeightParams,
)
from glyphs_sans_caps import CAP_GLYPH_BUILDERS
from glyphs_sans_figs_punct import FIG_PUNCT_GLYPH_BUILDERS
from glyphs_sans_latin_ext import EXT_CONTOUR_BUILDERS
from glyphs_sans_lc import LC_GLYPH_BUILDERS

CORE_BUILDERS: Dict[str, Callable[[SansWeightParams], List[ContourBuilder]]] = {
    **CAP_GLYPH_BUILDERS,
    **LC_GLYPH_BUILDERS,
    **FIG_PUNCT_GLYPH_BUILDERS,
}

OPEN_TYPE_FEATURES_FEA = """\
languagesystem DFLT dflt;
languagesystem latn dflt;
languagesystem latn TRK;
languagesystem latn AZE;
languagesystem latn CRT;
languagesystem latn ROM;
languagesystem latn MOL;

@figs_prop = [zero one two three four five six seven eight nine];
@figs_tnum = [zero.tnum one.tnum two.tnum three.tnum four.tnum five.tnum six.tnum seven.tnum eight.tnum nine.tnum];

@MarksTopLc  = [gravecomb acutecomb circumflexcomb tildecomb macroncomb brevecomb dotaccentcomb dieresiscomb ringabovecomb hungarumlautcomb caroncomb];
@MarksTopCap = [gravecomb.cap acutecomb.cap circumflexcomb.cap tildecomb.cap macroncomb.cap brevecomb.cap dotaccentcomb.cap dieresiscomb.cap ringabovecomb.cap hungarumlautcomb.cap caroncomb.cap];
@UpperBases  = [
    A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
    AE OE Oslash Eth Dcroat Thorn Germandbls Lslash Hbar Tbar Eng IJ Ldot
    Agrave Aacute Acircumflex Atilde Adieresis Aring Amacron Acaron Abreve Aogonek
    Ccedilla Cacute Ccircumflex Cdotaccent Ccaron
    Dcaron Egrave Eacute Ecircumflex Edieresis Emacron Ebreve Edotaccent Eogonek Ecaron
    Gcircumflex Gbreve Gdotaccent Gcommaaccent Hcircumflex
    Igrave Iacute Icircumflex Itilde Idieresis Imacron Icaron Ibreve Iogonek Idotaccent
    Jcircumflex Kcommaaccent Lacute Lcommaaccent Lcaron
    Ntilde Nacute Ncommaaccent Ncaron
    Ograve Oacute Ocircumflex Otilde Odieresis Omacron Ocaron Obreve Ohungarumlaut
    Racute Rcommaaccent Rcaron Sacute Scircumflex Scedilla Scaron Scommaaccent
    Tcedilla Tcaron Tcommaaccent
    Ugrave Uacute Ucircumflex Utilde Udieresis Ucaron Umacron Ubreve Uring Uhungarumlaut Uogonek
    Udieresismacron Udieresisacute Udieresiscaron Udieresisgrave
    Wcircumflex Wgrave Wacute Wdieresis Yacute Ycircumflex Ydieresis Ygrave
    Zacute Zdotaccent Zcaron
];

@punct_dflt = [hyphen hyphentwo nonbreakinghyphen endash emdash parenleft parenright bracketleft bracketright braceleft braceright colon periodcentered guilsinglleft guilsinglright guillemotleft guillemotright exclamdown questiondown];
@punct_case = [hyphen.case hyphentwo.case nonbreakinghyphen.case endash.case emdash.case parenleft.case parenright.case bracketleft.case bracketright.case braceleft.case braceright.case colon.case periodcentered.case guilsinglleft.case guilsinglright.case guillemotleft.case guillemotright.case exclamdown.case questiondown.case];

feature ccmp {
    lookup ccmp_soft_dotted {
        sub [i j iogonek]' @MarksTopLc by [dotlessi dotlessj iogonek.dotless];
    } ccmp_soft_dotted;

    lookup ccmp_cap_marks {
        sub @UpperBases @MarksTopLc' by @MarksTopCap;
        sub @MarksTopCap @MarksTopLc' by @MarksTopCap;
    } ccmp_cap_marks;
} ccmp;

feature locl {
    script latn;
    language TRK;
        sub i by i.loclTRK;
    language AZE;
        sub i by i.loclTRK;
    language CRT;
        sub i by i.loclTRK;
    language ROM;
        sub [Scedilla scedilla Tcedilla tcedilla] by [Scommaaccent scommaaccent Tcommaaccent tcommaaccent];
    language MOL;
        sub [Scedilla scedilla Tcedilla tcedilla] by [Scommaaccent scommaaccent Tcommaaccent tcommaaccent];
} locl;

feature lnum {
    sub @figs_tnum by @figs_prop;
} lnum;

feature pnum {
    sub @figs_tnum by @figs_prop;
} pnum;

feature tnum {
    sub @figs_prop by @figs_tnum;
} tnum;

feature zero {
    sub zero by zero.slash;
    sub zero.tnum by zero.tnum.slash;
} zero;

feature case {
    sub @punct_dflt by @punct_case;
} case;
"""


def build_all_sans_glyphs(
    params: SansWeightParams = SANS_REGULAR,
) -> Dict[str, Tuple[int, int | None, List[ContourBuilder]]]:
    """Return {gname: (width, unicode_or_None, contours)} for all contour-based glyphs."""
    result: Dict[str, Tuple[int, int | None, List[ContourBuilder]]] = {}

    for gname in DUPLEX_ADVANCE_WIDTHS:
        width = DUPLEX_ADVANCE_WIDTHS[gname]
        uni = UNICODE_MAP.get(gname)
        contours = CORE_BUILDERS[gname](params)
        result[gname] = (width, uni, contours)

    for gname, (width, uni, builder) in EXT_CONTOUR_BUILDERS.items():
        contours = builder(params)
        result[gname] = (width, uni, contours)

    return result
