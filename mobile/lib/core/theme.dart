import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Thème CacaoSat — palette du drapeau de la Côte d'Ivoire.
class CacaoTheme {
  const CacaoTheme._();

  static const orange = Color(0xFFFF7A00);
  static const green = Color(0xFF00A651);
  static const night = Color(0xFF08130E);
  static const night2 = Color(0xFF0E211A);
  static const sand = Color(0xFFF4EAD5);
  static const cacao = Color(0xFF7B3F00);

  static const riskLow = Color(0xFF00A651);
  static const riskMedium = Color(0xFFE8A33D);
  static const riskHigh = Color(0xFFC0392B);

  static ThemeData get dark {
    final base = ThemeData(
      brightness: Brightness.dark,
      useMaterial3: true,
      colorScheme: const ColorScheme.dark(
        primary: orange,
        secondary: green,
        surface: night2,
        error: riskHigh,
        onPrimary: Colors.white,
        onSurface: sand,
      ),
      scaffoldBackgroundColor: night,
    );
    return base.copyWith(
      textTheme: GoogleFonts.interTextTheme(base.textTheme).apply(
        bodyColor: sand.withValues(alpha: 0.92),
        displayColor: Colors.white,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: night,
        elevation: 0,
        titleTextStyle: GoogleFonts.poppins(
          fontSize: 18,
          fontWeight: FontWeight.w700,
          color: Colors.white,
        ),
      ),
      cardTheme: CardThemeData(
        color: night2,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(18),
          side: BorderSide(color: Colors.white.withValues(alpha: 0.08)),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: night,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.15)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.15)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: orange, width: 1.4),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: orange,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 18),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          textStyle: GoogleFonts.inter(fontWeight: FontWeight.w600),
        ),
      ),
    );
  }

  static Color riskColor(String? level) => switch (level) {
        'low' => riskLow,
        'medium' => riskMedium,
        'high' => riskHigh,
        _ => sand.withValues(alpha: 0.4),
      };

  static Color eudrColor(String? status) => switch (status) {
        'compliant' => riskLow,
        'at_risk' => riskMedium,
        'non_compliant' => riskHigh,
        _ => sand.withValues(alpha: 0.4),
      };

  static String eudrLabel(String? status) => switch (status) {
        'compliant' => 'Conforme',
        'at_risk' => 'À vérifier',
        'non_compliant' => 'Non conforme',
        _ => 'Non évaluée',
      };
}
