import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v7 as v
circ = 2 * math.pi * v.RP
spm = 3200 / circ
U = 774.0
print(f'circunferencia primitiva {circ:.2f} mm/vuelta; {spm:.3f} micropasos/mm (1/16); carrera {U:.0f} mm = {U*spm:,.0f} pasos')
print(f'vaso (38 mm) {38*spm:,.0f} pasos; rechazo (342 mm) {342*spm:,.0f} pasos')
print(f'empuje máximo {0.4/(v.RP/1000):.1f} N con 0,4 N·m; juego entre flancos ≈ {2*v.BL*math.tan(v.ALFA)+2*v.TD:.2f} mm')
print(f'dientes: {v.N_DIENTES} de valle {v.X_T0:.1f} a {v.X_T1:.1f}; módulo {v.M}, paso {v.PASO:.3f}; piñón de {v.NZ} dientes, punta {v.RP+v.HA:.2f}, raíz {v.RP-v.HF:.2f}')
print('cortes de la barra (centros de valle):', [round(v.valle(j*v.N_TRAMO),2) for j in range(5)], 'tramo', round(v.N_TRAMO*v.PASO,1), 'mm')
print(f'barra: x de {v.X_T0:.1f} a {v.X_T1+U:.1f} con u=0..{U:.0f} -> largo total {v.N_DIENTES*v.PASO:.1f} mm; piñón en x={v.XP}')
print(f'cola de la barra: de x={v.X_T0:.0f} (u=0) a x={v.X_T0+0:.0f}; con u=774 la cola sale {v.X_T0+U:.0f} y la punta llega a {v.X_T1+U:.0f}')
print(f'riel: {v.RIEL_X0} a {v.RIEL_X1}; el piñón engrana con la barra a lo largo de toda la carrera: dientes bajo el piñón de u=0 a 774')
span = (v.X_T1 + U + 14) - (v.X_T0 - 0)
print(f'extensión en X de la barra + piñón: {span:.0f} mm; mesa necesaria desde x={min(v.X_T0, v.RIEL_X0):.0f} hasta {max(v.RIEL_X1, v.X_T1+U):.0f} -> {max(v.RIEL_X1, v.X_T1+U)-min(v.X_T0, v.RIEL_X0):.0f} mm')
