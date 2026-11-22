// Generated (Admiralty 0.600). Licensed under the SIL Open Font License 1.1.
package io.github.cosmoluei.admiralty

/**
 * Font family resources (Regular 400, Medium 500, Bold 700 and their italics).
 *
 * XML:     android:fontFamily="@font/admiralty_sans"
 * Views:   textView.typeface = ResourcesCompat.getFont(context, AdmiraltyFonts.SANS)
 * Compose: see AGENTS.md in the Admiralty repository for a ready FontFamily.
 */
object AdmiraltyFonts {
    /** Interface text and the user's messages. */
    val SANS: Int get() = R.font.admiralty_sans
    /** The agent's messages; same widths as Sans, so switching never changes line breaks. */
    val SERIF: Int get() = R.font.admiralty_serif
    /** Code, logs and IDs (fixed width). */
    val MONO: Int get() = R.font.admiralty_mono
}
