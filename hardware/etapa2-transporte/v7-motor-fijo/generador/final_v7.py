import tolerancias_v7 as t
print('hinchazón por lado e (mm) -> solape máximo piñón/barra (mm3); 0 = gira libre; engrane nuevo BL=0,35 y dientes de barra -0,10')
for e in (0.0, 0.05, 0.08, 0.10, 0.12, 0.15):
    print(e, round(t.interferencia(e, e, 0.0), 2), '| solo la barra engorda', round(t.interferencia(0.0, e, 0.0), 2), flush=True)
