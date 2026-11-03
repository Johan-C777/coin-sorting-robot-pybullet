"""Cálculos de la v4 (carro sobre varillas + hilo). Imprime y devuelve un dict para la hoja y el visor."""
import os
import math, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v4 as v

def calc(d_rod=9.525, hilo_d=0.5):
    r = {}
    r_ef = v.R_TAMB + hilo_d/2
    r['mm_rev'] = 2*math.pi*r_ef
    r['steps_mm'] = 3200/r['mm_rev']
    r['steps_mm_nominal'] = 3200/(2*math.pi*v.R_EFF)
    r['carrera_pasos'] = v.U_MAX*r['steps_mm_nominal']
    r['vaso_pasos'] = 38*r['steps_mm_nominal']
    r['rechazo_pasos'] = 342*r['steps_mm_nominal']
    L = v.X_TORRE_MAX - v.X_TORRE_MIN            # luz libre de las varillas
    E = 200e3; I = math.pi*d_rod**4/64
    A = math.pi*d_rod**2/4; w = A*7.85e-6*9.81   # N/mm
    P = 0.5*9.81/2                               # carro+cartucho+monedas 0,5 kg, mitad por varilla, N
    r['luz'] = L; r['flecha_carga'] = P*L**3/(48*E*I); r['flecha_peso'] = 5*w*L**4/(384*E*I)
    r['flecha'] = r['flecha_carga'] + r['flecha_peso']
    r['masa_varilla_g'] = A*1000*7.85e-3
    F_fric = 5.0                                 # N, supuesto conservador (incluye roce por desalineación)
    r['par_necesario'] = F_fric*r_ef/1000        # N·m
    r['par_motor'] = 0.40                        # N·m, 17HS típico por debajo de 0,5 N·m con el A4988 a ~1 A
    r['margen_par'] = r['par_motor']/r['par_necesario']
    r['abrazo'] = math.exp(0.2*3*2*math.pi)
    r['hilo_m'] = (2*(v.X_POL - v.XM) + 2*math.pi*v.R_TAMB*1.5 + 3*2*math.pi*v.R_TAMB)/1000 + 0.4
    r['rod_largo'] = v.ROD_X1 - v.ROD_X0
    return r

if __name__ == '__main__':
    for d in (9.525, 10, 12, 12.7):
        r = calc(d)
        print(d, 'flecha %.2f mm (carga %.2f + peso %.2f)' % (r['flecha'], r['flecha_carga'], r['flecha_peso']), 'varilla %.0f g' % r['masa_varilla_g'])
    r = calc()
    for k, x in r.items(): print(k, round(x, 3))
