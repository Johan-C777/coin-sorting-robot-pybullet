import numpy as np, math
XM=-267; XP=703; D=970   # tambor, polea, tramo inferior
def compl(x):            # mm/N por unidad de EA(N): a*r/(a+r)
    a=x-XM; r=(XP-x)+D; return a*r/(a+r)
# x de trabajo del carro: u=0..774 desde X_CTR0 (-168)
xs=np.linspace(-168,-168+774,5)
print("Compliancia mm por N de carga, segun EA del hilo (N):")
hilos={'costura 1 cabo (EA~60)':60,'costura doblada x2 (~120)':120,'costura x4 (~240)':240,
       'nylon liso 0,4 mm (~350)':350,'trenzado PE caña (~3000)':3000}
print("hilo".ljust(28)+"  ".join(f"u={x+168:4.0f}" for x in xs))
for n,EA in hilos.items():
    print(n.ljust(28)+"  ".join(f"{compl(x)/EA:5.1f}" for x in xs)," (mm por N)")
# simulacion dinamica: carro masa m con resorte (hilo) y friccion Coulomb
def sim(EA,Fc,m,dist,a=0.5,vmax=0.15,x0=-168):
    dt=2e-4; k=lambda x:EA/compl(x)*1000   # N/m
    # perfil trapezoidal de la posicion deseada (m)
    d=dist/1000; ta=vmax/a
    if d<vmax*ta: ta=math.sqrt(d/a); vm=a*ta; tc=0
    else: vm=vmax; tc=(d-vmax*ta)/vmax
    T=2*ta+tc; t=np.arange(0,T+1.5,dt)
    def xd(t):
        if t<ta: return .5*a*t*t
        if t<ta+tc: return .5*a*ta*ta+vm*(t-ta)
        if t<T: s=T-t; return d-.5*a*s*s
        return d
    x=0.;v=0.;Fmax=0;Tmax=0
    for ti in t:
        xdt=xd(ti); kk=k(x0+x*1000)
        Fd=kk*(xdt-x); Fmax=max(Fmax,abs(Fd))
        Fnet=Fd-Fc*np.sign(v) if (abs(v)>1e-5 or abs(Fd)>Fc) else 0
        if abs(v)<=1e-5 and abs(Fd)<=Fc: v=0
        v+=Fnet/m*dt - 0.3*v*dt  # amort. interno pequeño
        x+=v*dt
    return (d-x)*1000, Fmax
print("\nError final de posicion del carro (mm, positivo = se queda corto) tras mover 38 mm, m=0,6 kg")
for Fc in (1.0,2.5,5.0):
    print(f"-- friccion del carro Fc={Fc} N")
    for n,EA in hilos.items():
        r=[sim(EA,Fc,0.6,38,x0=x0)[0] for x0 in (-168,-168+300,-168+700)]
        print("  "+n.ljust(28),"  ".join(f"{e:5.1f}" for e in r),"  (u=0,300,700)")
print("\nFuerza maxima en el hilo (N) en movimiento largo 342 mm, Fc=2,5, m=0,6 kg, a=0,5 m/s2")
for n,EA in hilos.items():
    e,F=sim(EA,2.5,0.6,342); print("  "+n.ljust(28),f"{F:4.1f} N")
print("\nTension minima del lazo T0 (N) para que no patine en el tambor, 3 vueltas, carga F=Fc+m*a=5,8 N")
F=5.8
for mu,n in ((0.3,'0,3'),(0.2,'0,2'),(0.12,'0,12 (trenzado liso)'),(0.08,'0,08 (muy liso)')):
    R=math.exp(mu*6*math.pi); print(f"  mu={n}: razon max {R:6.1f} -> T0 >= {F/2*(R+1)/(R-1):.2f} N")
