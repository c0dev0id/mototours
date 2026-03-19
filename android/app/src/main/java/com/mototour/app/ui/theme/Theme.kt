package com.mototour.app.ui.theme

import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// Colors matching the PDF companion guide
val Green = Color(0xFF2C5530)
val GreenLight = Color(0xFF4A7C50)
val Accent = Color(0xFFC8611A)
val AccentLight = Color(0xFFE8944D)
val Blue = Color(0xFF2B547E)
val Dark = Color(0xFF333333)
val Surface = Color(0xFFF8F6F0)

private val LightColors = lightColorScheme(
    primary = Green,
    onPrimary = Color.White,
    primaryContainer = Color(0xFFD4E8D6),
    onPrimaryContainer = Green,
    secondary = Accent,
    onSecondary = Color.White,
    secondaryContainer = Color(0xFFFDE0C8),
    onSecondaryContainer = Accent,
    tertiary = Blue,
    onTertiary = Color.White,
    background = Surface,
    surface = Color.White,
    onBackground = Dark,
    onSurface = Dark
)

@Composable
fun MotoTourTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = LightColors,
        content = content
    )
}
