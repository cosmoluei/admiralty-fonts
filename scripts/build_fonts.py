"""
Builds UFO v3 source, DesignSpace v5 file, UFO anchors & composite European glyphs,
class-based kerning, OpenType features (ccmp, locl, lnum, pnum, tnum, zero, case,
kern, mark, mkmk), and compiled OTF / TTF / WOFF2 binaries for Admiralty Sans.
"""

from __future__ import annotations
from pathlib import Path
import shutil
import sys

from fontTools.designspaceLib import AxisDescriptor, DesignSpaceDocument, InstanceDescriptor, SourceDescriptor
from fontTools.misc.bezierTools import calcCubicBounds
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import ttProgram
import pathops
import ufo2ft
import ufoLib2

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from design_system import METRICS, SANS_REGULAR, TABULAR_FIG_WIDTH, clean_contour_nicks
from glyphs_bold import (
    apply_bold_class_kerning,
    attach_bold_anchors_and_composites,
    build_all_mono_bold_glyphs,
    build_all_sans_bold_glyphs,
    build_all_serif_bold_glyphs,
)
from glyphs_italic import (
    CARET_SLOPE_RUN,
    ITALIC_ANGLE,
    apply_italic_class_kerning,
    attach_italic_anchors_and_composites,
    build_all_mono_italic_glyphs,
    build_all_sans_italic_glyphs,
    build_all_serif_italic_glyphs,
)
from glyphs_medium import (
    apply_medium_class_kerning,
    attach_medium_anchors_and_composites,
    build_all_mono_medium_glyphs,
    build_all_sans_medium_glyphs,
    build_all_serif_medium_glyphs,
)
from glyphs_box import build_box_glyphs
from glyphs_latin_plus import build_latin_plus
from glyphs_vietnamese import add_vietnamese
from glyphs_mono import (
    MONO_FEATURES_FEA,
    MONO_REGULAR,
    MONO_WIDTH,
    attach_mono_anchors_and_composites,
    build_all_mono_glyphs,
)
from glyphs_sans import OPEN_TYPE_FEATURES_FEA, build_all_sans_glyphs
from glyphs_serif_figs_ext import SERIF_REGULAR, build_all_serif_glyphs
from spacing_kerning import apply_class_kerning, attach_ufo_anchors_and_composites
import uharfbuzz as hb

VERSION_MINOR = 500
VERSION_STR = "0.500"


def autohint_otf(otf_path) -> bool:
    """Review 3: add PostScript stem hints to an OTF with AFDKO's otfautohint, when it is
    installed (pip install afdko). Without it the OTF is left unhinted, as before."""
    import shutil
    import subprocess
    exe = shutil.which("otfautohint")
    if exe is None:
        return False
    res = subprocess.run([exe, str(otf_path)], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"    otfautohint failed for {otf_path.name}: {res.stderr.strip()[:200]}")
        return False
    return True


def autohint_ttf(ttf_path) -> bool:
    """Release prep: TrueType hints from ttfautohint (pip install ttfautohint-py), for clearer
    small text on Windows. Static text fonts only; the variable fonts and Symbols stay unhinted
    with the non-hinting gasp/prep tables. Without ttfautohint the TTF is left as it is."""
    try:
        import ttfautohint
    except ImportError:
        return False
    # hinted fonts must not use scaled or flipped components (Font Bakery
    # transformed_components): draw those glyphs as plain outlines first
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    f = TTFont(str(ttf_path))
    glyf, gs = f["glyf"], f.getGlyphSet()
    changed = 0
    for name in f.getGlyphOrder():
        g = glyf[name]
        if not g.isComposite():
            continue
        if all(not hasattr(c, "transform") for c in g.components):
            continue
        rec = DecomposingRecordingPen(gs)
        gs[name].draw(rec)
        pen = TTGlyphPen(None)
        rec.replay(pen)
        glyf[name] = pen.glyph()
        changed += 1
    if changed:
        f.save(str(ttf_path))
    tmp = ttf_path.with_suffix(".hinted.ttf")
    try:
        ttfautohint.ttfautohint(in_file=str(ttf_path), out_file=str(tmp), hint_composites=True,
                                no_info=True, windows_compatibility=True)
    except Exception as exc:  # keep the unhinted font rather than fail the build
        print(f"    ttfautohint failed for {ttf_path.name}: {exc}")
        return False
    tmp.replace(ttf_path)
    f = TTFont(str(ttf_path))
    f["head"].flags |= 1 << 3          # integer ppem, required for hinted fonts
    f.save(str(ttf_path))
    return True


def populate_ufo_metadata(
    ufo: ufoLib2.Font,
    family_name: str,
    style_name: str,
    is_monospace: bool = False,
    weight_class: int = 400,
    is_italic: bool = False,
) -> None:
    ps_family = family_name.replace(" ", "")
    ps_style = style_name.replace(" ", "")
    info = ufo.info

    info.familyName = family_name
    info.styleName = style_name
    if weight_class == 500:
        info.styleMapFamilyName = f"{family_name} Medium"
        info.styleMapStyleName = "italic" if is_italic else "regular"
        info.openTypeNamePreferredFamilyName = family_name
        info.openTypeNamePreferredSubfamilyName = style_name
    else:
        info.styleMapFamilyName = family_name
        info.styleMapStyleName = style_name.lower()
    info.postscriptFontName = f"{ps_family}-{ps_style}"
    info.openTypeNameUniqueID = f"{VERSION_STR};LYT;{ps_family}-{ps_style}"

    info.versionMajor = 0
    info.versionMinor = VERSION_MINOR
    info.openTypeNameVersion = f"Version {VERSION_STR}"

    info.copyright = (
        "Copyright 2026 The Admiralty Project Authors "
        "(https://github.com/cosmoluei/admiralty-fonts)"
    )
    info.openTypeNameDesigner = "Lei Yutian"
    info.openTypeNameManufacturer = "Lei Yutian"
    info.openTypeOS2VendorID = "LYT "
    info.openTypeNameDescription = (
        f"{family_name} is a calm humanist typeface designed to pair seamlessly "
        "without text reflow alongside its companion families in a Personal Agent app. "
        "Latin only."
    )
    info.openTypeNameLicense = (
        "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
        "This license is available with a FAQ at: https://openfontlicense.org"
    )
    info.openTypeNameLicenseURL = "https://openfontlicense.org"

    info.unitsPerEm = METRICS.upm
    info.xHeight = METRICS.x_height
    info.capHeight = METRICS.cap_height
    info.ascender = METRICS.ascender
    info.descender = METRICS.descender

    info.openTypeOS2WeightClass = weight_class
    info.openTypeOS2WidthClass = 5
    info.openTypeOS2Type = []
    info.openTypeOS2TypoAscender = METRICS.typo_ascender
    info.openTypeOS2TypoDescender = METRICS.typo_descender
    info.openTypeOS2TypoLineGap = METRICS.typo_line_gap
    info.openTypeOS2WinAscent = METRICS.win_ascent
    info.openTypeOS2WinDescent = METRICS.win_descent
    info.openTypeOS2Selection = [7]  # USE_TYPO_METRICS

    info.openTypeHheaAscender = METRICS.hhea_ascender
    info.openTypeHheaDescender = METRICS.hhea_descender
    info.openTypeHheaLineGap = METRICS.hhea_line_gap

    info.postscriptUnderlinePosition = -100
    info.postscriptUnderlineThickness = 50
    if is_italic:
        info.italicAngle = ITALIC_ANGLE
        info.openTypeHheaCaretSlopeRise = 1000
        info.openTypeHheaCaretSlopeRun = CARET_SLOPE_RUN
    else:
        info.italicAngle = 0

    # PostScript CFF Private Dict hinting zones & dominant stem snaps (Fix #4)
    info.postscriptBlueValues = [-12, 0, 520, 530, 700, 712, 740, 754]
    info.postscriptOtherBlues = [-226, -220]
    info.postscriptBlueScale = 0.039625
    info.postscriptBlueShift = 7
    info.postscriptBlueFuzz = 0

    is_bold = weight_class >= 700
    is_med = weight_class == 500
    panose_w = 8 if is_bold else (6 if is_med else 5)
    if is_monospace:
        info.postscriptIsFixedPitch = True
        info.openTypeOS2Panose = [2, 11, panose_w, 9, 2, 2, 3, 2, 2, 7]  # bProportion=9 (Monospaced)
        info.postscriptStemSnapH = [92, 96] if is_bold else ([80, 84] if is_med else [72, 74])
        info.postscriptStemSnapV = [114, 116] if is_bold else ([96, 100] if is_med else [84, 86])
    elif "Serif" in family_name:
        info.openTypeOS2Panose = [2, 2, panose_w, 3, 5, 2, 3, 2, 2, 4]  # Serif Book/Med/Bold Text
        info.postscriptStemSnapH = [58, 62] if is_bold else ([48, 52] if is_med else [48, 50])
        info.postscriptStemSnapV = [144, 154] if is_bold else ([112, 122] if is_med else [92, 102])
    else:
        info.openTypeOS2Panose = [2, 11, panose_w, 3, 2, 2, 3, 2, 2, 4]  # Sans Book/Med/Bold Text
        info.postscriptStemSnapH = [116, 120] if is_bold else ([86, 90] if is_med else [74, 78])
        info.postscriptStemSnapV = [136, 140] if is_bold else ([104, 110] if is_med else [86, 88])


def apply_ttf_nonhinting_tables(ttf_font: TTFont) -> None:
    """Insert Google-Fonts standard non-hinting gasp + prep tables into compiled TTF."""
    gasp = newTable("gasp")
    gasp.gaspRange = {0xFFFF: 0x000F}
    ttf_font["gasp"] = gasp

    prep = newTable("prep")
    prog = ttProgram.Program()
    prog.fromAssembly(["PUSHW[]", "511", "SCANCTRL[]", "PUSHB[]", "4", "SCANTYPE[]"])
    prep.program = prog
    ttf_font["prep"] = prep

    ttf_font["maxp"].maxStackElements = max(getattr(ttf_font["maxp"], "maxStackElements", 0), 2)


def audit_ufo_geometry(ufo: ufoLib2.Font) -> None:
    """
    Google-Fonts-grade outline & vertical-clipping audit across all contour & composite glyphs.
    """
    errors: list[str] = []
    for glyph in ufo:
        gname = glyph.name

        # Check vertical clipping bounds against OS/2 winAscent (980) & winDescent (-320)
        bpen = BoundsPen(ufo)
        glyph.draw(bpen)
        if bpen.bounds is not None:
            _, ymin, _, ymax = bpen.bounds
            if ymax > METRICS.win_ascent + 2 or ymin < -METRICS.win_descent - 2:
                errors.append(
                    f"{gname}: vertical bounds [{ymin:.0f}, {ymax:.0f}] exceed "
                    f"[-{METRICS.win_descent}, +{METRICS.win_ascent}]!"
                )

        if len(glyph.contours) == 0:
            continue

        # 1. Winding & overlap conservation check on contour glyphs
        apen = AreaPen(ufo)
        glyph.draw(apen)
        raw_total_area = apen.value
        if raw_total_area <= 0:
            errors.append(f"{gname}: net signed area <= 0 ({raw_total_area:.1f}), reversed outer winding!")

        sk_path = pathops.Path()
        glyph.draw(sk_path.getPen())
        simplified = pathops.simplify(sk_path, fix_winding=True)
        temp_s = ufoLib2.objects.Glyph()
        simplified.draw(temp_s.getPen())
        sapen = AreaPen(ufo)
        temp_s.draw(sapen)
        diff_ratio = abs(sapen.value - raw_total_area) / max(abs(raw_total_area), 1.0)
        if diff_ratio > 0.006:
            errors.append(
                f"{gname}: overlap, self-intersection, or reversed counter! "
                f"raw_area={raw_total_area:.1f}, simplified_area={sapen.value:.1f}"
            )

        # 2. Cubic Bezier extrema check
        for c_idx, contour in enumerate(glyph.contours):
            pts = list(contour.points)
            n = len(pts)
            on_indices = [i for i, pt in enumerate(pts) if pt.type is not None]
            for k, idx0 in enumerate(on_indices):
                idx1 = on_indices[(k + 1) % len(on_indices)]
                span = (idx1 - idx0) % n
                if span == 3:
                    p0 = (pts[idx0].x, pts[idx0].y)
                    p1 = (pts[(idx0 + 1) % n].x, pts[(idx0 + 1) % n].y)
                    p2 = (pts[(idx0 + 2) % n].x, pts[(idx0 + 2) % n].y)
                    p3 = (pts[idx1].x, pts[idx1].y)
                    bx0, by0, bx1, by1 = calcCubicBounds(p0, p1, p2, p3)
                    ex0, ex1 = min(p0[0], p3[0]), max(p0[0], p3[0])
                    ey0, ey1 = min(p0[1], p3[1]), max(p0[1], p3[1])
                    over = max(ex0 - bx0, bx1 - ex1, ey0 - by0, by1 - ey1)
                    if over > 1.0:
                        errors.append(
                            f"{gname} contour {c_idx}: missing extremum by {over:.2f}u "
                            f"on segment {p0}->{p3}"
                        )

    if errors:
        for e in errors[:25]:
            print("GEOMETRY ERROR:", e, file=sys.stderr)
        raise RuntimeError(f"Geometry audit failed with {len(errors)} error(s).")
    print(f"Geometry, extrema & clipping audit passed cleanly for {len(ufo)} glyphs.")


def _hb_shape(ttf_path: Path, text: str, feats: dict | None = None):
    blob = hb.Blob.from_file_path(str(ttf_path))
    face = hb.Face(blob)
    font = hb.Font(face)
    font.scale = (1000, 1000)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, feats or {})
    return list(zip(buf.glyph_infos or [], buf.glyph_positions or []))


def _verify_common_font_tables(
    otf_path: Path,
    ttf_path: Path,
    woff2_path: Path,
    req_gsub: set[str],
    req_gpos: set[str],
    expected_weight: int = 400,
    expected_italic: bool = False,
) -> None:
    otf = TTFont(str(otf_path))
    priv = otf["CFF "].cff.topDictIndex[0].Private
    assert getattr(priv, "BlueValues", None) and len(priv.BlueValues) >= 4, "Missing CFF BlueValues"
    assert getattr(priv, "OtherBlues", None) and len(priv.OtherBlues) >= 2, "Missing CFF OtherBlues"
    assert getattr(priv, "StemSnapH", None) and getattr(priv, "StemSnapV", None), "Missing CFF StemSnap"

    tt = TTFont(str(ttf_path))
    w2 = TTFont(str(woff2_path))
    for font_bin, tag in ((tt, "TTF"), (w2, "WOFF2")):
        assert "gasp" in font_bin, f"{tag}: no gasp"
        if "fpgm" in font_bin:   # hinted by ttfautohint
            assert font_bin["gasp"].gaspRange.get(0xFFFF) in (0x000F, 0x000A), f"{tag}: bad gasp"
        else:
            assert font_bin["gasp"].gaspRange.get(0xFFFF) == 0x000F, f"{tag}: bad gasp"
            assert "prep" in font_bin and list(font_bin["prep"].program.getBytecode()) == [
                0xB8, 0x01, 0xFF, 0x85, 0xB0, 0x04, 0x8D
            ], f"{tag}: bad prep"
        assert round(font_bin["head"].fontRevision, 3) == float(VERSION_STR), f"{tag}: bad version {font_bin['head'].fontRevision}"
        assert font_bin["OS/2"].achVendID == "LYT ", f"{tag}: bad achVendID"
        pan = vars(font_bin["OS/2"].panose)
        assert any(v != 0 for v in pan.values()), f"{tag}: Panose is all zeros"

    os2 = tt["OS/2"]
    hhea = tt["hhea"]
    post = tt["post"]
    assert os2.usWeightClass == expected_weight, f"usWeightClass={os2.usWeightClass} != {expected_weight}"
    assert bool(os2.fsSelection & 1) == expected_italic, f"fsSelection ITALIC bit={bool(os2.fsSelection & 1)} != {expected_italic}"
    assert bool(os2.fsSelection & (1 << 5)) == (expected_weight >= 700), "fsSelection BOLD bit mismatch"
    assert bool(os2.fsSelection & (1 << 6)) == (expected_weight < 700 and not expected_italic), (
        f"fsSelection REGULAR bit mismatch (fsSelection={bin(os2.fsSelection)}, w={expected_weight}, it={expected_italic})"
    )
    expected_mac = (1 if expected_weight >= 700 else 0) | (2 if expected_italic else 0)
    assert tt["head"].macStyle == expected_mac, f"head.macStyle={tt['head'].macStyle} != {expected_mac}"
    expected_angle = ITALIC_ANGLE if expected_italic else 0.0
    assert round(post.italicAngle, 1) == expected_angle, f"post.italicAngle={post.italicAngle} != {expected_angle}"
    expected_run = CARET_SLOPE_RUN if expected_italic else 0
    assert hhea.caretSlopeRun == expected_run, f"hhea.caretSlopeRun={hhea.caretSlopeRun} != {expected_run}"
    if expected_italic:
        assert hhea.caretSlopeRise == 1000, f"hhea.caretSlopeRise={hhea.caretSlopeRise} != 1000"
    if expected_weight == 500:
        n1 = tt["name"].getDebugName(1) or ""
        n2 = tt["name"].getDebugName(2) or ""
        n17 = tt["name"].getDebugName(17) or ""
        exp_n2 = "Italic" if expected_italic else "Regular"
        exp_n17 = "Medium Italic" if expected_italic else "Medium"
        assert n1.endswith(" Medium"), f"Medium NameID 1={n1!r} must end with ' Medium'"
        assert n2 == exp_n2, f"Medium NameID 2={n2!r} != {exp_n2!r}"
        assert n17 == exp_n17, f"Medium NameID 17={n17!r} != {exp_n17!r}"
    assert os2.sTypoAscender == hhea.ascent == 980
    assert os2.sTypoDescender == hhea.descent == -320
    assert os2.sTypoLineGap == hhea.lineGap == 0
    assert os2.usWinAscent == 980 and os2.usWinDescent == 320
    assert bool(os2.fsSelection & (1 << 7))

    # Fix #10: eth must have clean 2-contour outline (no trapped sliver)
    assert tt["glyf"]["eth"].numberOfContours == 2, f"eth contours={tt['glyf']['eth'].numberOfContours}"

    # Verify depth-1 composite flattening (no composite referencing another composite)
    glyf = tt["glyf"]
    for gname in tt.getGlyphOrder():
        g = glyf[gname]
        if g.isComposite():
            for comp in g.components:
                assert not glyf[comp.glyphName].isComposite(), f"Nested composite {gname} -> {comp.glyphName}"

    # Fix #2 & #3: complete Latin Extended-A (128/128), ẞ, 16 Pinyin precomposed, spaces & symbols
    cmap = tt.getBestCmap() or {}
    missing_lat_a = [cp for cp in range(0x0100, 0x0180) if cp not in cmap]
    assert not missing_lat_a, f"Missing Latin Extended-A codepoints: {[hex(x) for x in missing_lat_a]}"
    required_extra = (
        [0x1E9E, 0x2009, 0x202F, 0x2010, 0x2011, 0x20B9, 0x20A9, 0x20BD]
        + list(range(0x01CD, 0x01DD))
        + [0x2248, 0x221E, 0x221A, 0x03C0, 0x2206, 0x03A9, 0x2194, 0x21D2, 0x2713, 0x2717, 0x2030, 0x2032, 0x2033, 0x2116]
    )
    missing_extra = [cp for cp in required_extra if cp not in cmap]
    assert not missing_extra, f"Missing required codepoints: {[hex(x) for x in missing_extra]}"

    # Fix #2: Pinyin precomposition (NFC) AND propagated composite anchor stacking (ǟ, Ä́, ǟ)
    for seq in ("ü\u0304", "Ü\u0301", "u\u0308\u0304"):
        shaped = _hb_shape(ttf_path, seq)
        assert len(shaped) == 1, f"Expected precomposed Pinyin glyph on {seq!r}, got {len(shaped)}"
    for seq in ("ä\u0304", "Ä\u0301", "a\u0308\u0304"):
        shaped = _hb_shape(ttf_path, seq)
        assert len(shaped) == 2 and shaped[1][1].y_offset > 0, (
            f"Propagated composite mark stacking failed on {seq!r}: {[p.y_offset for _, p in shaped]}"
        )

    gsub_feats = {r.FeatureTag for r in tt["GSUB"].table.FeatureList.FeatureRecord}
    gpos_feats = {r.FeatureTag for r in tt["GPOS"].table.FeatureList.FeatureRecord}
    assert req_gsub.issubset(gsub_feats), f"Missing GSUB features: {req_gsub - gsub_feats}"
    assert req_gpos.issubset(gpos_feats), f"Missing GPOS features: {req_gpos - gpos_feats}"

    woff2_kb = woff2_path.stat().st_size / 1024.0
    assert woff2_kb < 100.0, f"WOFF2 size {woff2_kb:.1f} KB exceeds 100 KB target"
    print(
        f"OpenType & binary table audit PASSED ({ttf_path.name}): "
        f"LatExtA=128/128, gasp/prep/CFF=OK, v{VERSION_STR}, w={expected_weight}, it={expected_italic}, eth=2c, WOFF2={woff2_kb:.1f} KB."
    )


def verify_compiled_tables(
    otf_path: Path,
    ttf_path: Path,
    woff2_path: Path,
    expected_weight: int = 400,
    expected_italic: bool = False,
) -> None:
    _verify_common_font_tables(
        otf_path,
        ttf_path,
        woff2_path,
        req_gsub={"ccmp", "locl", "lnum", "pnum", "tnum", "zero", "case"},
        req_gpos={"kern", "mark", "mkmk"},
        expected_weight=expected_weight,
        expected_italic=expected_italic,
    )


def _write_weight_designspace(
    sources_dir: Path,
    ps_family: str,
    family_name: str,
    source_entries: list[tuple[str, int, Path]],
    *,
    is_italic: bool = False,
) -> Path:
    """Write a 3-source (Weight 400, 500, 700) DesignSpace v5 file."""
    ds = DesignSpaceDocument()
    w_axis = AxisDescriptor()
    w_axis.tag = "wght"
    w_axis.name = "Weight"
    w_axis.minimum = 400
    w_axis.default = 400
    w_axis.maximum = 700
    ds.addAxis(w_axis)

    for style_name, weight_class, ufo_path in source_entries:
        src = SourceDescriptor()
        src.path = str(ufo_path)
        src.filename = ufo_path.name
        src.familyName = family_name
        src.styleName = style_name
        src.location = {"Weight": weight_class}
        if weight_class == 400:
            src.copyLib = True
            src.copyInfo = True
            src.copyGroups = True
            src.copyFeatures = True
        ds.addSource(src)

        ps_style = style_name.replace(" ", "")
        inst = InstanceDescriptor()
        inst.name = f"{family_name} {style_name}"
        inst.familyName = family_name
        inst.styleName = style_name
        inst.postScriptFontName = f"{ps_family}-{ps_style}"
        inst.styleMapFamilyName = f"{family_name} Medium" if weight_class == 500 else family_name
        inst.styleMapStyleName = (
            ("italic" if is_italic else "regular") if weight_class == 500 else style_name.lower()
        )
        inst.location = {"Weight": weight_class}
        inst.filename = f"instance_ufos/{ps_family}-{ps_style}.ufo"   # needed by gftools builder
        ds.addInstance(inst)

    # Review 3 / Google Fonts: every named weight of the variable font needs an instance,
    # so SemiBold 600 (interpolated) is listed too.
    it = " Italic" if is_italic else ""
    inst = InstanceDescriptor()
    inst.familyName = family_name
    inst.styleName = f"SemiBold{it}"
    inst.name = f"{family_name} SemiBold{it}"
    inst.postScriptFontName = f"{ps_family}-SemiBold{it.strip()}"
    inst.styleMapFamilyName = f"{family_name} SemiBold"
    inst.styleMapStyleName = "italic" if is_italic else "regular"
    inst.location = {"Weight": 600}
    inst.filename = f"instance_ufos/{ps_family}-SemiBold{it.strip()}.ufo"
    ds.addInstance(inst)
    ds.instances.sort(key=lambda i: i.location["Weight"])

    suffix = "-Italic" if is_italic else ""
    ds_path = sources_dir / f"{ps_family}{suffix}.designspace"
    ds.write(str(ds_path))
    print(f"[{ps_family}{suffix}] Wrote 3-source DesignSpace (Weight 400, 500, 700) -> {ds_path}")
    return ds_path


def _populate_ufo_and_compile(
    ufo: ufoLib2.Font,
    stem: str,
    glyph_data: dict,
    sources_dir: Path,
    otf_dir: Path,
    ttf_dir: Path,
    woff2_dir: Path,
    *,
    attach_fn,
    kern_fn=None,
    fixed_width: int | None = None,
) -> tuple[Path, Path, Path, Path]:
    glyph_order: list[str] = []
    for gname, (width, uni, contours) in glyph_data.items():
        glyph_order.append(gname)
        g = ufo.newGlyph(gname)
        g.width = width
        if uni is not None:
            g.unicodes = [uni]
        pen = g.getPen()
        for cb in contours:
            clean_contour_nicks(cb).draw_to_pen(pen)

    ufo.lib["public.glyphOrder"] = glyph_order
    attach_fn(ufo)
    if kern_fn is not None:
        kern_fn(ufo)
    add_vietnamese(ufo)

    for cname in ("udieresis", "Udieresis", "adieresis", "Adieresis"):
        assert any(a.name == "top" for a in ufo[cname].anchors), f"{stem} missing propagated anchor on {cname}"
    audit_ufo_geometry(ufo)

    ufo_path = sources_dir / f"{stem}.ufo"
    ufo.save(ufo_path, overwrite=True)
    kern_note = f", {len(ufo.groups)} kern groups, {len(ufo.kerning)} class rules" if kern_fn else ", 600u fixed pitch"
    print(f"[{stem}] Saved UFO source ({len(ufo)} glyphs{kern_note}) -> {ufo_path}")

    otf_font: TTFont = ufo2ft.compileOTF(ufo, removeOverlaps=True, optimizeCFF=True)
    if fixed_width is not None:
        otf_font["OS/2"].xAvgCharWidth = fixed_width
    otf_path = otf_dir / f"{stem}.otf"
    otf_font.save(str(otf_path))
    autohint_otf(otf_path)

    ttf_font: TTFont = ufo2ft.compileTTF(ufo, removeOverlaps=True)
    if fixed_width is not None:
        ttf_font["OS/2"].xAvgCharWidth = fixed_width
    apply_ttf_nonhinting_tables(ttf_font)
    ttf_path = ttf_dir / f"{stem}.ttf"
    ttf_font.save(str(ttf_path))

    # the web font stays unhinted (browsers mostly ignore hints; they only add size)
    woff2_font = TTFont(str(ttf_path))
    woff2_font.flavor = "woff2"
    woff2_path = woff2_dir / f"{stem}.woff2"
    woff2_font.save(str(woff2_path))
    if not stem.startswith("AdmiraltySymbols"):
        autohint_ttf(ttf_path)
    print(f"[{stem}] Compiled OTF / TTF / WOFF2 -> {woff2_path}")
    return ufo_path, otf_path, ttf_path, woff2_path


def build_duplex_family_all_styles(
    family_name: str,
    style_specs: list[tuple[str, int, bool, dict]],
) -> dict[str, tuple[Path, Path]]:
    ps_family = family_name.replace(" ", "")

    sources_dir = ROOT / "sources"
    otf_dir = ROOT / "fonts" / "otf"
    ttf_dir = ROOT / "fonts" / "ttf"
    woff2_dir = ROOT / "fonts" / "woff2"
    for d in (sources_dir, otf_dir, ttf_dir, woff2_dir):
        d.mkdir(parents=True, exist_ok=True)

    outputs: dict[str, tuple[Path, Path]] = {}
    ds_upright: list[tuple[str, int, Path]] = []
    ds_italic: list[tuple[str, int, Path]] = []

    for style_name, weight_class, is_italic, glyph_data in style_specs:
        # 0.300: Google Fonts Latin Plus characters, built from this style's own glyphs
        glyph_data.update(build_latin_plus(glyph_data, "serif" if "Serif" in family_name else "sans", weight_class, is_italic))
        ps_style = style_name.replace(" ", "")
        stem = f"{ps_family}-{ps_style}"
        ufo = ufoLib2.Font()
        populate_ufo_metadata(
            ufo, family_name, style_name, is_monospace=False, weight_class=weight_class, is_italic=is_italic
        )
        ufo.features.text = OPEN_TYPE_FEATURES_FEA

        if is_italic:
            attach_fn = lambda u, wc=weight_class: attach_italic_anchors_and_composites(u, weight_class=wc, is_monospace=False)
            kern_fn = apply_italic_class_kerning
        elif weight_class == 400:
            attach_fn = attach_ufo_anchors_and_composites
            kern_fn = apply_class_kerning
        elif weight_class == 500:
            attach_fn = lambda u: attach_medium_anchors_and_composites(u, is_monospace=False)
            kern_fn = apply_medium_class_kerning
        else:
            attach_fn = lambda u: attach_bold_anchors_and_composites(u, is_monospace=False)
            kern_fn = apply_bold_class_kerning

        ufo_path, otf_path, ttf_path, woff2_path = _populate_ufo_and_compile(
            ufo, stem, glyph_data, sources_dir, otf_dir, ttf_dir, woff2_dir,
            attach_fn=attach_fn, kern_fn=kern_fn,
        )
        verify_compiled_tables(
            otf_path, ttf_path, woff2_path, expected_weight=weight_class, expected_italic=is_italic
        )
        outputs[style_name] = (ttf_path, woff2_path)
        (ds_italic if is_italic else ds_upright).append((style_name, weight_class, ufo_path))

    _write_weight_designspace(sources_dir, ps_family, family_name, ds_upright, is_italic=False)
    _write_weight_designspace(sources_dir, ps_family, family_name, ds_italic, is_italic=True)
    return outputs


def verify_duplex_zero_reflow(
    sans_ttf: Path,
    serif_ttf: Path,
    style_label: str = "Regular",
    *,
    is_italic: bool = False,
) -> None:
    """Assert 1:1 identical glyph advance widths and 0.0u HarfBuzz shaped reflow."""
    tt_sans = TTFont(str(sans_ttf))
    tt_serif = TTFont(str(serif_ttf))

    sans_order = tt_sans.getGlyphOrder()
    serif_order = tt_serif.getGlyphOrder()
    assert sans_order == serif_order, f"Glyph order mismatch between Sans and Serif ({style_label})!"

    hmtx_sans = tt_sans["hmtx"].metrics
    hmtx_serif = tt_serif["hmtx"].metrics
    mismatches = [
        (g, hmtx_sans[g][0], hmtx_serif[g][0])
        for g in sans_order
        if hmtx_sans[g][0] != hmtx_serif[g][0]
    ]
    assert not mismatches, f"Duplex hmtx advance width mismatch ({style_label}): {mismatches[:10]}"

    def _hb_adv(ttf_path: Path, text: str, feats: dict | None = None) -> int:
        blob = hb.Blob.from_file_path(str(ttf_path))
        face = hb.Face(blob)
        font = hb.Font(face)
        font.scale = (1000, 1000)
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf, feats or {})
        return sum(p.x_advance for p in (buf.glyph_positions or []))

    test_strings = [
        "Admiralty Personal Agent — Zero Layout Reflow Guaranteed (2026).",
        "WAVEY To Va Yo Ti Te LT P. F, \"Hello, world!\" $1,480.95 €290 £75 ¥3,600",
        "Voix ambiguë d'un cœur qui au zéphyr préfère les jattes de kiwis. Œuvre & Æther.",
        "Zażółć gęślą jaźń — Příliš žluťoučký kůň úpěl ďábelské ódy — Tiếng Việt đồng nhất.",
        "Section §4.2 · Copyright © 2026 · 1ª 2º · Navigate ← ↑ → ↓ ↗ ↩",
        "fV fW fY qj gj (f) [f] {f} 2011 1,111 nǐ hǎo ǖ ǘ ǚ ǜ Ǖ Ǘ Ǚ Ǜ ẞ Ĳ ĳ ĸ Ŀ ŀ ŉ Ŧ ŧ ſ ₹ ₩ ₽ ≈ ∞ √ π ∆ Ω ↔ ⇒ ✓ ✗ ‰ ′ ″ № ð",
    ]
    for s in test_strings:
        for feat in ({}, {"tnum": True, "zero": True}, {"case": True}):
            w1 = _hb_adv(sans_ttf, s, feat)
            w2 = _hb_adv(serif_ttf, s, feat)
            assert w1 == w2, f"HarfBuzz shaped advance mismatch ({style_label}) on {s!r} ({feat}): Sans={w1} vs Serif={w2}"

    for d in ("zero.tnum", "one.tnum", "two.tnum", "four.tnum", "eight.tnum"):
        assert hmtx_sans[d][0] == TABULAR_FIG_WIDTH and hmtx_serif[d][0] == TABULAR_FIG_WIDTH

    # Fix #7 + Italic (f clearance audit across Sans & Serif
    for fpath, fname in ((sans_ttf, f"Sans {style_label}"), (serif_ttf, f"Serif {style_label}")):
        for pair in ("fV", "fW", "fY", "gj"):
            w_kern = _hb_adv(fpath, pair, {"kern": True})
            w_raw = _hb_adv(fpath, pair, {"kern": False})
            assert w_kern - w_raw == 24, f"{fname} kern({pair!r}) expected +24, got {w_kern - w_raw}"
        if is_italic:
            for pair in ("(f", "[f", "{f"):
                w_kern = _hb_adv(fpath, pair, {"kern": True})
                w_raw = _hb_adv(fpath, pair, {"kern": False})
                assert w_kern - w_raw == 28, f"{fname} kern({pair!r}) expected +28, got {w_kern - w_raw}"

    print(
        f"Duplex Zero-Reflow Audit PASSED ({style_label}): all {len(sans_order)} glyphs and "
        f"{len(test_strings) * 3} shaped multilingual runs match to 0.0 units!"
    )


def build_admiralty_mono() -> dict[str, tuple[Path, Path]]:
    family_name = "Admiralty Mono"
    ps_family = "AdmiraltyMono"

    sources_dir = ROOT / "sources"
    otf_dir = ROOT / "fonts" / "otf"
    ttf_dir = ROOT / "fonts" / "ttf"
    woff2_dir = ROOT / "fonts" / "woff2"
    for d in (sources_dir, otf_dir, ttf_dir, woff2_dir):
        d.mkdir(parents=True, exist_ok=True)

    mono_specs = [
        ("Regular", 400, False, build_all_mono_glyphs(MONO_REGULAR)),
        ("Medium", 500, False, build_all_mono_medium_glyphs()),
        ("Bold", 700, False, build_all_mono_bold_glyphs()),
        ("Italic", 400, True, build_all_mono_italic_glyphs(400)),
        ("Medium Italic", 500, True, build_all_mono_italic_glyphs(500)),
        ("Bold Italic", 700, True, build_all_mono_italic_glyphs(700)),
    ]

    outputs: dict[str, tuple[Path, Path]] = {}
    ds_upright: list[tuple[str, int, Path]] = []
    ds_italic: list[tuple[str, int, Path]] = []

    for style_name, weight_class, is_italic, glyph_data in mono_specs:
        # 0.300: box drawing and block elements (upright in every style, as terminals expect)
        glyph_data.update(build_latin_plus(glyph_data, "mono", weight_class, is_italic))
        glyph_data.update(build_box_glyphs(weight_class))
        ps_style = style_name.replace(" ", "")
        stem = f"{ps_family}-{ps_style}"
        ufo = ufoLib2.Font()
        populate_ufo_metadata(
            ufo, family_name, style_name, is_monospace=True, weight_class=weight_class, is_italic=is_italic
        )
        ufo.features.text = MONO_FEATURES_FEA

        if is_italic:
            attach_fn = lambda u, wc=weight_class: attach_italic_anchors_and_composites(u, weight_class=wc, is_monospace=True)
        elif weight_class == 400:
            attach_fn = attach_mono_anchors_and_composites
        elif weight_class == 500:
            attach_fn = lambda u: attach_medium_anchors_and_composites(u, is_monospace=True)
        else:
            attach_fn = lambda u: attach_bold_anchors_and_composites(u, is_monospace=True)

        ufo_path, otf_path, ttf_path, woff2_path = _populate_ufo_and_compile(
            ufo, stem, glyph_data, sources_dir, otf_dir, ttf_dir, woff2_dir,
            attach_fn=attach_fn, kern_fn=None, fixed_width=MONO_WIDTH,
        )

        _verify_common_font_tables(
            otf_path,
            ttf_path,
            woff2_path,
            req_gsub={"ccmp", "locl", "zero", "case", "ss01"},
            req_gpos={"mark", "mkmk"},
            expected_weight=weight_class,
            expected_italic=is_italic,
        )

        # Strict Monospace & OpenType Verification
        tt = TTFont(str(ttf_path))
        os2 = tt["OS/2"]
        hhea = tt["hhea"]
        post = tt["post"]
        assert os2.sTypoAscender == hhea.ascent == 980
        assert os2.sTypoDescender == hhea.descent == -320
        assert os2.sTypoLineGap == hhea.lineGap == 0
        assert os2.usWinAscent == 980 and os2.usWinDescent == 320
        assert bool(os2.fsSelection & (1 << 7))
        assert post.isFixedPitch == 1, f"Expected post.isFixedPitch=1, got {post.isFixedPitch}"
        assert os2.panose.bProportion == 9, f"Expected Panose.bProportion=9, got {os2.panose.bProportion}"
        assert os2.xAvgCharWidth == MONO_WIDTH

        widths = {w for _, (w, _) in tt["hmtx"].metrics.items()}
        assert widths <= {0, MONO_WIDTH}, f"Non-monospace widths found in hmtx: {widths}"

        gsub_feats = {r.FeatureTag for r in tt["GSUB"].table.FeatureList.FeatureRecord}
        assert "ss01" in gsub_feats
        gpos_feats = {r.FeatureTag for r in tt["GPOS"].table.FeatureList.FeatureRecord}
        assert "kern" not in gpos_feats, "Monospace font must not have kerning!"

        # Measure Mono vertical stem thicknesses directly on flattened contours
        from fontTools.pens.recordingPen import RecordingPen

        def _scanline_stems(gname: str, y_probe: float) -> list[int]:
            rec = RecordingPen()
            ufo[gname].draw(rec)
            xs: list[float] = []
            cur = (0.0, 0.0)
            start = (0.0, 0.0)

            def _seg(p0: tuple[float, float], p1: tuple[float, float]) -> None:
                x0, y0 = p0
                x1, y1 = p1
                if (y0 <= y_probe < y1) or (y1 <= y_probe < y0):
                    xs.append(x0 + (y_probe - y0) * (x1 - x0) / (y1 - y0))

            for cmd, pts in rec.value:
                if cmd == "moveTo":
                    cur = start = pts[0]
                elif cmd == "lineTo":
                    _seg(cur, pts[0])
                    cur = pts[0]
                elif cmd == "curveTo":
                    p0, p1, p2, p3 = cur, pts[0], pts[1], pts[2]
                    prev = p0
                    for step in range(1, 33):
                        t = step / 32.0
                        mt = 1.0 - t
                        q = (
                            mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0],
                            mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1],
                        )
                        _seg(prev, q)
                        prev = q
                    cur = p3
                elif cmd == "closePath":
                    _seg(cur, start)
                    cur = start
            xs.sort()
            return [round(xs[i + 1] - xs[i]) for i in range(0, len(xs) - 1, 2)]

        if weight_class == 400 and not is_italic:
            cap_probes = {
                "B": (200.0, False), "D": (350.0, False), "E": (200.0, False), "F": (200.0, False),
                "H": (150.0, True), "I": (350.0, True), "J": (350.0, True), "K": (120.0, False),
                "L": (200.0, False), "M": (100.0, True), "N": (350.0, False), "P": (120.0, True),
                "R": (120.0, False), "U": (450.0, True),
            }
            for cap_g, (y_probe, check_all) in cap_probes.items():
                all_s = _scanline_stems(cap_g, y_probe)
                stems = all_s if check_all else [all_s[0]]
                assert all(s == 84 for s in stems), f"Mono cap {cap_g} stem {stems} (all={all_s}) != 84"
            lc_probes = {
                "b": (240.0, [0]), "d": (240.0, [-1]), "f": (240.0, [0]), "h": (240.0, [0, 1]),
                "i": (240.0, [0]), "j": (240.0, [0]), "k": (120.0, [0]), "l": (240.0, [0]),
                "m": (240.0, [0, 1, 2]), "n": (240.0, [0, 1]), "p": (240.0, [0]), "q": (240.0, [-1]),
                "r": (240.0, [0]), "t": (240.0, [0]), "u": (300.0, [0, 1]),
            }
            for lc_g, (y_probe, idxs) in lc_probes.items():
                all_s = _scanline_stems(lc_g, y_probe)
                stems = [all_s[i] for i in idxs]
                assert all(s == 86 for s in stems), f"Mono lc {lc_g} stems {stems} (all={all_s}) != 86"
            assert _scanline_stems("m", 240.0) == [86, 86, 86]
            stem_summary = "caps=84u, lc=86u (m=[86,86,86])"
        else:
            if weight_class == 400:
                cap_lo, cap_hi, lc_lo, lc_hi = 80, 88, 82, 90
            elif weight_class == 500:
                cap_lo, cap_hi, lc_lo, lc_hi = 92, 104, 94, 106
            else:
                cap_lo, cap_hi, lc_lo, lc_hi = 108, 122, 110, 124
            for cap_g, yp in (("H", 150.0), ("I", 350.0), ("L", 200.0)):
                stems = _scanline_stems(cap_g, yp)
                assert all(cap_lo <= s <= cap_hi for s in stems), f"{stem} cap {cap_g} stems {stems} out of {cap_lo}..{cap_hi}"
            for lc_g, yp in (("n", 200.0), ("l", 240.0), ("o", 260.0)):
                stems = _scanline_stems(lc_g, yp)
                assert all(lc_lo <= s <= lc_hi for s in stems), f"{stem} lc {lc_g} stems {stems} out of {lc_lo}..{lc_hi}"
            stem_summary = f"H={_scanline_stems('H', 150.0)[0]}u, n={_scanline_stems('n', 200.0)[0]}u, o={_scanline_stems('o', 260.0)[0]}u"

        # Verify 80-char code line is strictly 80 * 600 = 48000u with ss01 OFF and ON!
        code_80 = "const fn = (x: i32, y: i32) => x != 0 && x <= y ? x -> y : y <- x; // ID:Il1_O0!"
        assert len(code_80) == 80, f"Expected 80 chars, got {len(code_80)}"
        blob = hb.Blob.from_file_path(str(ttf_path))
        face = hb.Face(blob)
        font = hb.Font(face)
        font.scale = (1000, 1000)
        for feat in ({}, {"ss01": True, "zero": True}):
            buf = hb.Buffer()
            buf.add_str(code_80)
            buf.guess_segment_properties()
            hb.shape(font, buf, feat)
            adv = sum(p.x_advance for p in (buf.glyph_positions or []))
            assert adv == 80 * MONO_WIDTH, f"{stem} 80-char line advance {adv} != 48000 ({feat})"

        woff2_kb = woff2_path.stat().st_size / 1024.0
        assert woff2_kb < 100.0
        print(
            f"[{stem}] Monospace audit PASSED: isFixedPitch=1, Panose.bProportion=9, "
            f"{stem_summary}, widths={sorted(widths)}, 80-col=48000u, WOFF2={woff2_kb:.1f} KB."
        )
        outputs[style_name] = (ttf_path, woff2_path)
        (ds_italic if is_italic else ds_upright).append((style_name, weight_class, ufo_path))

    _write_weight_designspace(sources_dir, ps_family, family_name, ds_upright, is_italic=False)
    _write_weight_designspace(sources_dir, ps_family, family_name, ds_italic, is_italic=True)
    return outputs


if __name__ == "__main__":
    from build_symbols import build_all_symbols

    fonts_dir = ROOT / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "OFL.txt", fonts_dir / "OFL.txt")

    sans_styles = build_duplex_family_all_styles(
        "Admiralty Sans",
        [
            ("Regular", 400, False, build_all_sans_glyphs(SANS_REGULAR)),
            ("Medium", 500, False, build_all_sans_medium_glyphs()),
            ("Bold", 700, False, build_all_sans_bold_glyphs()),
            ("Italic", 400, True, build_all_sans_italic_glyphs(400)),
            ("Medium Italic", 500, True, build_all_sans_italic_glyphs(500)),
            ("Bold Italic", 700, True, build_all_sans_italic_glyphs(700)),
        ],
    )
    serif_styles = build_duplex_family_all_styles(
        "Admiralty Serif",
        [
            ("Regular", 400, False, build_all_serif_glyphs(SERIF_REGULAR)),
            ("Medium", 500, False, build_all_serif_medium_glyphs()),
            ("Bold", 700, False, build_all_serif_bold_glyphs()),
            ("Italic", 400, True, build_all_serif_italic_glyphs(400)),
            ("Medium Italic", 500, True, build_all_serif_italic_glyphs(500)),
            ("Bold Italic", 700, True, build_all_serif_italic_glyphs(700)),
        ],
    )
    for style_name, (_, _), is_it in (
        ("Regular", (None, None), False),
        ("Medium", (None, None), False),
        ("Bold", (None, None), False),
        ("Italic", (None, None), True),
        ("Medium Italic", (None, None), True),
        ("Bold Italic", (None, None), True),
    ):
        verify_duplex_zero_reflow(sans_styles[style_name][0], serif_styles[style_name][0], style_name, is_italic=is_it)

    mono_styles = build_admiralty_mono()
    sym_reg_ttf, sym_med_ttf, sym_bld_ttf, _ = build_all_symbols()

    all_woff2 = (
        [sans_styles[s][1] for s in sans_styles]
        + [serif_styles[s][1] for s in serif_styles]
        + [mono_styles[s][1] for s in mono_styles]
        + [
            ROOT / "fonts" / "woff2" / "AdmiraltySymbols-Regular.woff2",
            ROOT / "fonts" / "woff2" / "AdmiraltySymbols-Medium.woff2",
            ROOT / "fonts" / "woff2" / "AdmiraltySymbols-Bold.woff2",
        ]
    )
    assert len(all_woff2) == 21, f"Expected 21 static WOFF2 fonts, got {len(all_woff2)}"
    total_kb = sum(p.stat().st_size for p in all_woff2) / 1024.0
    assert total_kb < 1536.0, f"Full Suite WOFF2 total {total_kb:.1f} KB exceeds 1.5 MB budget!"
    print(
        f"ALL {len(all_woff2)} STATIC FONTS BUILT & AUDITED (v{VERSION_STR})! "
        f"Total 21-font WOFF2 bundle = {total_kb:.1f} KB / 1536.0 KB."
    )

    import os

    if os.environ.get("ADMIRALTY_SKIP_VARIABLE") == "1":
        print("ADMIRALTY_SKIP_VARIABLE=1: variable fonts were not rebuilt.")
    else:
        from build_variable import build_all_variable_fonts

        build_all_variable_fonts()
