#pragma once
// ============================================================================================
//  VALORES DE FÁBRICA DE LA CALIBRACIÓN FÍSICA
//  Cada parámetro lleva una etiqueta [CAL-xx]. El procedimiento de cada una está en
//  firmware/etapa1_clasificador/README.md#calibración y en TODO.md (fase 3).
//  Los valores calibrados con monedas reales se guardan en NVS con el comando 'g' y tienen
//  prioridad sobre estos al arrancar. 'F' vuelve a estos valores.
// ============================================================================================
#include "Calibracion.h"

constexpr clasif::Calibracion CAL_FABRICA = {
    // [CAL-01] Separación real entre los dos haces. Nominal del CAD: 24,0 mm (L01, 105 -> 129 mm).
    //          >>> Medir con calibrador pie de rey entre los centros de los agujeros Ø5,2 de L01.
    /* sep_barreras_mm   */ 24.0f,
    // [CAL-02] Altura efectiva del haz sobre la repisa. Nominal del CAD: 10,0 mm (H_BAR).
    //          >>> Se ajusta solo con el comando 'C' tras pasar monedas conocidas ('c<vaso>').
    /* h_haz_mm          */ 10.0f,
    // [CAL-03] Ancho efectivo del haz (ventana Ø1,6 + umbral del fototransistor). Nominal 0.
    //          >>> Lo ajusta 'C' junto con [CAL-02].
    /* ancho_haz_mm      */ 0.0f,
    // [CAL-04] Tolerancia máxima en diámetro. La de cada clase es min(esta, vecino/2 − margen).
    //          >>> Ajustar si el error RMS que reporta 'C' supera 0,10 mm.
    /* tolerancia_max_mm */ 0.60f,
    /* margen_vecino_mm  */ 0.05f,
    // [CAL-05] Umbral de "dorada" del TCS3200, razón (R+G)/2B.
    //          >>> Monitor 'm' con una $500 antigua y una nueva frente a A01; poner el punto medio.
    /* umbral_dorado     */ 1.30f,
    // Física plausible, márgenes amplios. Rodadura pura a 22°: a = 2/3·g·sen 22° ≈ 2,45 m/s².
    // [CAL-06] >>> Revisar con las líneas "#D" de la consola (v y a reales) y cerrar estos rangos.
    /* v_min, v_max      */ 50.0f, 2000.0f,
    /* a_min, a_max      */ -2000.0f, 9810.0f,
};
