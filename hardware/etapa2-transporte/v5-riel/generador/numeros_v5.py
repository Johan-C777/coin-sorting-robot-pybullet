"""Cálculos de la v5 (riel impreso, carro e hilo de casa). Imprime y devuelve un dict para la hoja y el visor."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v5 as v

def calc(hilo_d=0.5):
    r = {}
    r_ef = v.R_T + hilo_d / 2
    r['r_ef'] = r_ef
    r['mm_rev'] = 2 * math.pi * r_ef
    r['steps_mm'] = 3200 / r['mm_rev']
    r['carrera_pasos'] = v.U_MAX * r['steps_mm']
    r['vaso_pasos'] = 38 * r['steps_mm']
    r['rechazo_pasos'] = 342 * r['steps_mm']
    r['u_ref'] = (v.IR_X + v.LEN / 2) - v.X_CTR0                      # el borde trasero del carro llega al haz
    r['ref_pasos'] = r['u_ref'] * r['steps_mm']
    r['rozamiento_N'] = 5.0                                            # supuesto alto: 0,35 kg x 0,4 = 1,4 N + aceleración + margen
    r['par_necesario'] = r['rozamiento_N'] * r_ef / 1000
    r['par_motor'] = 0.40
    r['margen_par'] = r['par_motor'] / r['par_necesario']
    r['abrazo'] = math.exp(0.2 * 3 * 2 * math.pi)
    L_sup = v.X_P - v.XM
    r['hilo_m'] = (2 * L_sup + 3 * 2 * math.pi * v.R_T + math.pi * v.R_T) / 1000 + 0.35
    r['riel_largo'] = v.RIEL_X1 - v.RIEL_X0
    r['carrera_util'] = v.U_MAX
    r['aprieto_max_mm'] = v.SLOT
    return r

if __name__ == '__main__':
    for k, x in calc().items(): print(k, round(x, 3))
