// Extrae del simulador web las funciones del planificador de obstáculos y las
// evalúa en Node, sin navegador. Lo usa software/tests/test_obstaculos.py para
// comprobar que el modelo de Python y el de la página son el mismo.
//
//     node scripts/verificar_simulador.js docs/simulacion_sistema_completo.html
'use strict';
const fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');

function funcion(nombre) {
  const i = html.indexOf('function ' + nombre + '(');
  if (i < 0) throw new Error('no está la función ' + nombre);
  let prof = 0;
  for (let k = html.indexOf('{', i); k < html.length; k++) {
    if (html[k] === '{') prof++;
    else if (html[k] === '}' && --prof === 0) return html.slice(i, k + 1);
  }
  throw new Error('función sin cerrar: ' + nombre);
}
function constante(nombre) {
  // admite 'var A = 1;' y también 'var A = 1, B = 2;'
  const m = html.match(new RegExp('(?:var\\s+|,\\s*)' + nombre + '\\s*=\\s*([^;,]+)[;,]'));
  if (!m) throw new Error('no está la constante ' + nombre);
  return 'var ' + nombre + ' = ' + m[1] + ';';
}

const obst = html.slice(html.indexOf('var NIVELES'), html.indexOf('var MARGEN'));
const codigo = [
  'var GR = Math.PI/180;',
  ...['R_ARCO', 'Z_AGARRE', 'Z_SEGURA', 'Z_BAJO', 'GRASP_DZ', 'VASO_H', 'VASO_R',
      'RHO_MIN', 'RHO_MAX', 'MARGEN'].map(constante),
  'var THREE = {Vector3: function(x, y, z){ this.x = x; this.y = y; this.z = z; }};',
  'var brazo = {vaso: true}, sim = {vObst: 45};',
  obst,
  'OBST.forEach(function(o){ o.esferas = []; for (var b = 0; b < o.brazos; b++) ' +
    'o.esferas.push({angBase: 2*Math.PI*b/o.brazos}); });',
  ...['puntoArco', 'aEscena', 'tcpDeArco', 'posEsfera', 'holgura', 'holguraMinima',
      'alturaBajoObstaculo', 'radioInterior', 'zonaAngular', 'maniobra'].map(funcion),
].join('\n');

const salida = new Function(codigo + `
  var res = {obstaculos: [], plan: [], holguras: []};
  OBST.forEach(function(o){
    res.obstaculos.push({nombre: o.nombre, nivel: o.nivel, yaw: o.yaw, zona: zonaAngular(o),
                         bajo: alturaBajoObstaculo(o), interior: radioInterior(o)});
  });
  for (var yaw = -60; yaw <= 86; yaw += 1) {
    var m = maniobra(yaw);
    res.plan.push([yaw, m.modo, m.z, m.rho, m.obst ? m.obst.nombre.slice(0, 2) : '']);
  }
  var semilla = 7;
  function azar(){ semilla = (semilla*16807) % 2147483647; return semilla/2147483647; }
  for (var i = 0; i < 400; i++) {
    var o = OBST[i % OBST.length];
    o.angulo = azar()*2*Math.PI;
    var yaw = -60 + azar()*146, h = 6 + azar()*18, r = 7 + azar()*18;
    res.holguras.push([o.nombre.slice(0, 2), o.angulo, yaw, h, r,
                       holguraMinima(o, tcpDeArco(yaw, h, r), 0)]);
  }
  return res;`)();
console.log(JSON.stringify(salida));
