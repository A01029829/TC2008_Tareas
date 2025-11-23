// Tarea CG2
// por: Luis Emilio Velediaz Flores - A01029829

// genera un archivo OBJ de un edificio cilíndrico con parámetros customizables
// lee argumentos (lados, altura, radio base, radio cima) y crea un modelo 3D con vértices, normales y caras triangulares

const fs = require('fs');

// indices para acceder a coordenadas
const x = 0;
const y = 1;
const z = 2;

// parse de argumentos
const [sidesArg, heightArg, radiusBottomArg, radiusTopArg] = process.argv.slice(2);

// convertir a números o usar valores por defecto
let sides = Number(sidesArg) || 8;
let height = Number(heightArg) || 6.0;
let radiusBottom = Number(radiusBottomArg) || 1.0;
let radiusTop = Number(radiusTopArg) || 0.8;

// validar que los valores estén en rangos válidos
if (sides < 3) sides = 3;
if (sides > 36) sides = 36;
if (height <= 0) height = 6.0;
if (radiusBottom <= 0) radiusBottom = 1.0;
if (radiusTop <= 0) radiusTop = 0.8;

function makeShape(sides, height, radiusBottom, radiusTop) {
  // generar geometría del edificio
  const obj = createGeometry(sides, height, radiusBottom, radiusTop);
  const fileName = `building_${sides}_${height}_${radiusBottom}_${radiusTop}.obj`;
  writeObj(fileName, obj);
}

function createGeometry(sides, height, radiusBottom, radiusTop) {
  // arreglos para almacenar vértices, normales y caras
  const vertices = [null];
  const vertexLines = [];
  const normalLines = [];
  const faceLines = [];

  // normalizar un vector
  function normalize(vx, vy, vz) {
    const len = Math.sqrt(vx * vx + vy * vy + vz * vz);
    if (len === 0) return [0, 0, 0];
    return [vx / len, vy / len, vz / len];
  }

  // calcular normal de un triángulo con producto cruz
  function calcNormal(v0, v1, v2) {
    const ux = v1[x] - v0[x];
    const uy = v1[y] - v0[y];
    const uz = v1[z] - v0[z];
    const vx = v2[x] - v0[x];
    const vy = v2[y] - v0[y];
    const vz = v2[z] - v0[z];
    const nx = uy * vz - uz * vy;
    const ny = uz * vx - ux * vz;
    const nz = ux * vy - uy * vx;
    return normalize(nx, ny, nz);
  }

  // agregar vértice a los arreglos
  function addVertex(vx, vy, vz) {
    vertices.push([vx, vy, vz]);
    vertexLines.push(`v ${vx} ${vy} ${vz}`);
  }

  // agregar normal a los arreglos
  function addNormal(nx, ny, nz) {
    normalLines.push(`vn ${nx} ${ny} ${nz}`);
    return normalLines.length;
  }

  // agregar cara triangular a los arreglos
  function addFace(v1, v2, v3, n) {
    faceLines.push(`f ${v1}//${n} ${v2}//${n} ${v3}//${n}`);
  }

  // centro inferior y superior
  addVertex(0, 0, 0);
  addVertex(0, height, 0);

  // vértices alrededor del cilindro
  for (let i = 0; i < sides; i++) {
    const angle = (2 * Math.PI * i) / sides;
    addVertex(radiusBottom * Math.cos(angle), 0, radiusBottom * Math.sin(angle));
    addVertex(radiusTop * Math.cos(angle), height, radiusTop * Math.sin(angle));
  }

  // caras inferiores
  for (let i = 0; i < sides; i++) {
    const current = 3 + 2 * i;
    const next = 3 + 2 * ((i + 1) % sides);
    const n = addNormal(0, -1, 0);
    addFace(next, 1, current, n);
  }

  // caras superiores
  for (let i = 0; i < sides; i++) {
    const current = 4 + 2 * i;
    const next = 4 + 2 * ((i + 1) % sides);
    const n = addNormal(0, 1, 0);
    addFace(current, 2, next, n);
  }

  // caras laterales (2 triángulos por lado)
  for (let i = 0; i < sides; i++) {
    const b0 = 3 + 2 * i;
    const t0 = 4 + 2 * i;
    const b1 = 3 + 2 * ((i + 1) % sides);
    const t1 = 4 + 2 * ((i + 1) % sides);

    // crimer triángulo del lado
    const [nx1, ny1, nz1] = calcNormal(vertices[b1], vertices[b0], vertices[t0]);
    const n1 = addNormal(nx1, ny1, nz1);
    addFace(b1, b0, t0, n1);

    // segundo triángulo del lado
    const [nx2, ny2, nz2] = calcNormal(vertices[t0], vertices[t1], vertices[b1]);
    const n2 = addNormal(nx2, ny2, nz2);
    addFace(t0, t1, b1, n2);
  }

  return { vertices: vertexLines, normals: normalLines, faces: faceLines };
}

// escribir archivo OBJ
function writeObj(fileName, obj) {
  let content = obj.vertices.join('\n') + '\n' + obj.normals.join('\n') + '\n' + obj.faces.join('\n');
  fs.writeFileSync(fileName, content);
  console.log(`File generated: ${fileName}`);
}

makeShape(sides, height, radiusBottom, radiusTop);