/*
Function to create the vertex and color information for simple shapes
These can be used in multiple examples.

Gilberto Echeverria
2024-09-15
*/

// Create the data for the vertices of a polygon with the shape of the
// letter F. This is useful to view the transformations on the object.
function shapeF() {
    let arrays = {
        a_position: {
            numComponents: 2,
            data: [
                // Letter F
                0, 0,
                0, 200,
                40, 200,
                40, 0,
                40, 40,
                200, 40,
                200, 0,
                40, 120,
                150, 120,
                150, 80,
                40, 80,
            ]
        },
        indices: {
            numComponents: 3,
            data: [
                // Front face
                0, 1, 2,
                2, 3, 0,
                3, 4, 5,
                5, 6, 3, 
                7, 8, 9,
                9, 10, 7,
            ]
        }
    };

    return arrays;
}

function diamond(size) {
    let arrays = {
        a_position: {
            numComponents: 2,
            data: [
                // A diamond shape
                size, 0,
                0, size,
                -size, 0,
                0, -size,
            ]
        },
        indices: {
            numComponents: 3,
            data: [
                // Front face
                0, 1, 2,
                2, 3, 0,
            ]
        }
    };

    return arrays;
}

function car2D() {
    let arrays = {
        a_position: {
            numComponents: 2,
            data: [
                -100,  -40,
                 -40,  -40,
                  40,  -40,
                 100,  -40,
                 100,  -20,
                  40,   10,
                 -40,   10,
                -100,   20,
                 -30,   40,
                  24,   30,
            ]
        },
        indices: {
            numComponents: 3,
            data: [
                0, 1, 6,      0, 6, 7,    // Car back
                1, 2, 5,      1, 5, 6,    // Car middle
                2, 3, 4,      2, 4, 5,    // Car front
                6, 5, 9,      6, 9, 8     // Car top
            ]
        }
    }

    return arrays;
}


// Create the data for a cube where each face has a different color
function cubeFaceColors(size) {
    let arrays = {
        a_position: {
            numComponents: 3,
            data: [
                // Front Face
                -1.0, -1.0,  1.0,
                1.0, -1.0,  1.0,
                1.0,  1.0,  1.0,
                -1.0,  1.0,  1.0,

                // Back face
                -1.0, -1.0, -1.0,
                -1.0,  1.0, -1.0,
                1.0,  1.0, -1.0,
                1.0, -1.0, -1.0,

                // Top face
                -1.0,  1.0, -1.0,
                -1.0,  1.0,  1.0,
                1.0,  1.0,  1.0,
                1.0,  1.0, -1.0,

                // Bottom face
                -1.0, -1.0, -1.0,
                1.0, -1.0, -1.0,
                1.0, -1.0,  1.0,
                -1.0, -1.0,  1.0,

                // Right face
                1.0, -1.0, -1.0,
                1.0,  1.0, -1.0,
                1.0,  1.0,  1.0,
                1.0, -1.0,  1.0,

                // Left face
                -1.0, -1.0, -1.0,
                -1.0, -1.0,  1.0,
                -1.0,  1.0,  1.0,
                -1.0,  1.0, -1.0
            ].map(e => size * e)
        },
        a_normal: {
            numComponents: 3,
            data: [
                // Front Face
                0, 0, 1,
                0, 0, 1,
                0, 0, 1,
                0, 0, 1,

                // Back face
                0, 0, -1,
                0, 0, -1,
                0, 0, -1,
                0, 0, -1,

                // Top face
                0, 1, 0,
                0, 1, 0,
                0, 1, 0,
                0, 1, 0,

                // Bottom face
                0, -1, 0,
                0, -1, 0,
                0, -1, 0,
                0, -1, 0,

                // Right face
                1, 0, 0,
                1, 0, 0,
                1, 0, 0,
                1, 0, 0,

                // Left face
                -1, 0, 0,
                -1, 0, 0,
                -1, 0, 0,
                -1, 0, 0,
            ]
        },
        a_color: {
            numComponents: 4,
            data: [
                // Front face
                1, 0, 0, 1, // v_1
                1, 0, 0, 1, // v_1
                1, 0, 0, 1, // v_1
                1, 0, 0, 1, // v_1
                // Back Face
                0, 1, 0, 1, // v_2
                0, 1, 0, 1, // v_2
                0, 1, 0, 1, // v_2
                0, 1, 0, 1, // v_2
                // Top Face
                0, 0, 1, 1, // v_3
                0, 0, 1, 1, // v_3
                0, 0, 1, 1, // v_3
                0, 0, 1, 1, // v_3
                // Bottom Face
                1, 1, 0, 1, // v_4
                1, 1, 0, 1, // v_4
                1, 1, 0, 1, // v_4
                1, 1, 0, 1, // v_4
                // Right Face
                0, 1, 1, 1, // v_5
                0, 1, 1, 1, // v_5
                0, 1, 1, 1, // v_5
                0, 1, 1, 1, // v_5
                // Left Face
                1, 0, 1, 1, // v_6
                1, 0, 1, 1, // v_6
                1, 0, 1, 1, // v_6
                1, 0, 1, 1, // v_6
            ]
        },
        indices: {
            numComponents: 3,
            data: [
                0, 1, 2,      0, 2, 3,    // Front face
                4, 5, 6,      4, 6, 7,    // Back face
                8, 9, 10,     8, 10, 11,  // Top face
                12, 13, 14,   12, 14, 15, // Bottom face
                16, 17, 18,   16, 18, 19, // Right face
                20, 21, 22,   20, 22, 23  // Left face
            ]
        }
    };

    return arrays;
}

// Create the data for a cube with each vertex in a different color
function cubeVertexColors(size) {
    let arrays = {
        a_position: {
            numComponents: 3,
            data: [
                1,  1,  1, // v_0
                1, -1,  1, // v_1
                -1, -1,  1, // v_2
                -1,  1,  1, // v_3
                1,  1, -1, // v_4
                1, -1, -1, // v_5
                -1, -1, -1, // v_6
                -1,  1, -1, // v_7
            ].map(e => size * e)
        },
        a_color: {
            numComponents: 4,
            data: [
                1, 1, 1, 1, // v_0
                1, 0, 0, 1, // v_1
                0, 1, 0, 1, // v_2
                0, 0, 1, 1, // v_3
                0, 0, 0, 1, // v_4
                1, 1, 0, 1, // v_5
                0, 1, 1, 1, // v_6
                1, 0, 1, 1, // v_7
            ]
        },
        indices: {
            numComponents: 3,
            data: [
                // Front face
                0, 2, 1,
                2, 0, 3,
                // Top face
                0, 5, 4,
                5, 0, 1,
                // Left face
                1, 6, 5,
                6, 1, 2,
                // Right face
                0, 7, 3,
                7, 0, 4,
                // Bottom face
                2, 7, 6,
                7, 2, 3,
                // Back face
                4, 6, 7,
                6, 4, 5,
            ]
        }
    };

    return arrays;
}

// Yellow circle - Face
function shapeC() {
    return generateData(64, [1, 1, 0, 1]);
}

function generateData(sides, color = [1, 1, 1, 1]) {
    let arrays = {
        a_position: { numComponents: 2, data: [] },
        a_color:    { numComponents: 4, data: [] },
        indices:    { numComponents: 3, data: [] }
    };

    arrays.a_position.data.push(0);
    arrays.a_position.data.push(0);
    arrays.a_color.data.push(color[0]);
    arrays.a_color.data.push(color[1]);
    arrays.a_color.data.push(color[2]);
    arrays.a_color.data.push(color[3]);

    let angleStep = 2 * Math.PI / sides;
    let radius = 100;
    
    for (let s = 0; s < sides; s++) {
        let angle = angleStep * s;
        let x = Math.cos(angle) * radius;
        let y = Math.sin(angle) * radius;
        arrays.a_position.data.push(x);
        arrays.a_position.data.push(y);
        arrays.a_color.data.push(color[0]);
        arrays.a_color.data.push(color[1]);
        arrays.a_color.data.push(color[2]);
        arrays.a_color.data.push(color[3]);
        arrays.indices.data.push(0);
        arrays.indices.data.push(s + 1);
        arrays.indices.data.push(((s + 2) <= sides) ? (s + 2) : 1);
    }

    return arrays;
}

// Red circle - Pivot
function shapePivot() {
    let arrays = {
        a_position: { numComponents: 2, data: [] },
        a_color:    { numComponents: 4, data: [] },
        indices:    { numComponents: 3, data: [] }
    };

    const pivotRadius = 10;
    const pivotSegments = 16;

    // Pivot's center
    arrays.a_position.data.push(0, 0);
    arrays.a_color.data.push(1, 0, 0, 1);

    for (let i = 0; i < pivotSegments; i++) {
        const angle = (i / pivotSegments) * Math.PI * 2;
        const x = Math.cos(angle) * pivotRadius;
        const y = Math.sin(angle) * pivotRadius;
        arrays.a_position.data.push(x, y);
        arrays.a_color.data.push(1, 0, 0, 1);
    }

    for (let i = 1; i <= pivotSegments; i++) {
        const next = (i % pivotSegments) + 1;
        arrays.indices.data.push(0, i, next);
    }

    return arrays;
}

function shapeEye() {
    return generateData(32, [0, 0, 0, 1]);
}

function shapeSmile() {
    let arrays = {
        a_position: { numComponents: 2, data: [] },
        indices:    { numComponents: 3, data: [] },
        a_color:    { numComponents: 4, data: [] }
    };

    const radius = 60;
    const segments = 32;
    const color = [0, 0, 0, 1];

    arrays.a_position.data.push(0, 0);
    arrays.a_color.data.push(color);

    const start = Math.PI * 0.1;
    const end   = Math.PI * 0.9;
    const step  = (end - start) / segments;

    for (let i = 0; i <= segments; i++) {
        let angle = start + i * step;
        let x = Math.cos(angle) * radius;
        let y = Math.sin(angle) * radius * 0.2;
        arrays.a_position.data.push(x, y);
        arrays.a_color.data.push(color);

        if (i < segments) {
            arrays.indices.data.push(0, i + 1, i + 2);
        }
    }

    return arrays;
}

export { shapeF, diamond, cubeFaceColors, cubeVertexColors, car2D, shapeC, shapePivot, shapeEye, shapeSmile };

