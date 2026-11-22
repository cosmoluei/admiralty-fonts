"""Identify punctuation outlines in the text families, including OpenType alternates."""
import unicodedata


DOT_ROLES = {
    "period": "all", "periodcentered": "all", "colon": "all",
    "ellipsis": "all", "bullet": "all",
    "semicolon": "top", "questiondown": "top", "exclamdown": "top",
    "question": "bottom", "exclam": "bottom",
}


def dot_contours(name, bounds):
    """Indices of detached circular dots, given (xmin, ymin, xmax, ymax) per contour."""
    role = DOT_ROLES.get(name.removesuffix(".case"))
    if role is None or not bounds:
        return ()
    if role == "all":
        return tuple(range(len(bounds)))
    # The inverted signs put the dot above the stem; the semicolon's other
    # contour includes the comma tail. Contour ordering varies by font format.
    find = max if role == "top" else min
    return (find(range(len(bounds)), key=lambda i: bounds[i][1] + bounds[i][3]),)


def punctuation_names(cmap, glyph_order):
    """Return Unicode punctuation, its named alternates and complete Mono ligature cells."""
    # U+00AD is a format character, but it has a visible hyphen at a line break.
    encoded = {name for codepoint, name in cmap.items()
               if codepoint == 0x00AD or unicodedata.category(chr(codepoint)).startswith("P")}
    # A Mono programming ligature substitutes one glyph in *each* input cell.
    # Include the operator halves too so a joined sign keeps its alignment.
    return {name for name in glyph_order
            if name.partition(".")[0] in encoded or ".lig_" in name}
