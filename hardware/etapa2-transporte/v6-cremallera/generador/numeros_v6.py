import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v6 as v
circ = 2 * math.pi * v.RP
spm = 3200 / circ
print(f'circunferencia primitiva {circ:.2f} mm/vuelta; {spm:.2f} micropasos/mm (1/16); carrera {v.U_MAX:.0f} mm = {v.U_MAX*spm:,.0f} pasos')
print(f'vaso (38 mm) {38*spm:,.0f} pasos; rechazo (342 mm) {342*spm:,.0f} pasos; cero IR en u = {v.IR_X + v.LEN/2 - v.X_CTR0:.1f} mm = {(v.IR_X + v.LEN/2 - v.X_CTR0)*spm:,.0f} pasos')
print(f'empuje máximo {0.4/ (v.RP/1000):.1f} N con 0,4 N·m; juego entre flancos ≈ {2*v.BL*math.tan(v.ALFA):.2f} mm')
print(f'dientes: {v.N_DIENTES} de {v.X_V0:.1f} a {v.X_R1:.1f}; módulo {v.M}, paso {v.PASO:.3f}; piñón de {v.NZ} dientes, punta {v.RP+v.HA:.1f} mm')
print('cortes de los tramos (centro de valle):', [round(c, 2) for c in v.CORTES])
xs = v.X_CTR0
print(f'piñón engrana con la cremallera de u = {v.X_V0 + 12 - v.X_CTR0:.0f} a {v.X_R1 - 12 - v.X_CTR0:.0f} mm (carrera 0 a {v.U_MAX:.0f})')
print(f'riel de {v.RIEL_X0} a {v.RIEL_X1}; carro de {xs - v.LEN/2:.0f} a {xs + v.U_MAX + v.LEN/2:.0f}')
