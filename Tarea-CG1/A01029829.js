/*
 * CG Homework 1
 *
 * Luis Emilio Veledíaz Flores
 * A01029829
 * 
 * 14-11-2025
 */


'use strict';

import * as twgl from 'twgl-base.js';
import { shapeC, shapePivot, shapeEye, shapeSmile } from './libs/A01029829_shapes.js';
import { M3 } from './libs/2d-lib.js';
import GUI from 'lil-gui';

// Define the shader code, using GLSL 3.00

const vsGLSL = `#version 300 es
in vec2 a_position;

uniform vec2 u_resolution;
uniform mat3 u_transforms;

void main() {
    // Multiply the matrix by the vector, adding 1 to the vector to make
    // it the correct size. Then keep only the two first components
    vec2 position = (u_transforms * vec3(a_position, 1)).xy;

    // Convert the position from pixels to 0.0 - 1.0
    vec2 zeroToOne = position / u_resolution;

    // Convert from 0->1 to 0->2
    vec2 zeroToTwo = zeroToOne * 2.0;

    // Convert from 0->2 to -1->1 (clip space)
    vec2 clipSpace = zeroToTwo - 1.0;

    // Invert Y axis
    //gl_Position = vec4(clipSpace[0], clipSpace[1] * -1.0, 0, 1);
    gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);
}
`;

const fsGLSL = `#version 300 es
precision highp float;

uniform vec4 u_color;

out vec4 outColor;

void main() {
    outColor = u_color;
}
`;


// Structure for the global data of all objects
// This data will be modified by the UI and used by the renderer
const objects = {
    model: {
        transforms: {
            t: { // translation in screen space
                x: 550,
                y: 255,
                z: 0,
            },
            rr: { // rotation in radians
                x: 0,
                y: 0,
                z: 0,
            },
            s: { // model scale
                x: 1,
                y: 1,
                z: 1,
            }
        },
        color: [0.94, 0.85, 0.24, 1], // initial face color
    },

    pivot: {
        transforms: { // pivot world position
            t: { 
                x: 512, 
                y: 384, 
                z: 0 
            }, 
            rr: { 
                x: 0, 
                y: 0, 
                z: 0 
            },
            s: { 
                x: 1, 
                y: 1, 
                z: 1 
            }
        },
        color: [1, 0, 0, 1], // red pivot color
    }
}

let vao, bufferInfo, pivotVAO, pivotBufferInfo;

// Initialize the WebGL environmnet
function main() {
    const canvas = document.querySelector('canvas');
    const gl = canvas.getContext('webgl2');
    twgl.resizeCanvasToDisplaySize(gl.canvas);
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

    setupUI(gl); // create the GUI interface

    // Build shader program
    const programInfo = twgl.createProgramInfo(gl, [vsGLSL, fsGLSL]);

    // Create geometry for the main face circle
    const arrays = shapeC();

    // Create eye geometry
    const eyeArrays = shapeEye();
    const eyeBufferInfo = twgl.createBufferInfoFromArrays(gl, eyeArrays);
    const eyeVAO = twgl.createVAOFromBufferInfo(gl, programInfo, eyeBufferInfo);

    // Create mouth geometry
    const smileArrays = shapeSmile();
    const smileBufferInfo = twgl.createBufferInfoFromArrays(gl, smileArrays);
    const smileVAO = twgl.createVAOFromBufferInfo(gl, programInfo, smileBufferInfo);

    // Create face VAO
    const bufferInfo = twgl.createBufferInfoFromArrays(gl, arrays);
    vao = twgl.createVAOFromBufferInfo(gl, programInfo, bufferInfo);

    // Create pivot VAO
    const pivotArrays = shapePivot();
    pivotBufferInfo = twgl.createBufferInfoFromArrays(gl, pivotArrays);
    pivotVAO = twgl.createVAOFromBufferInfo(gl, programInfo, pivotBufferInfo);

    // Start render loop
    drawScene(gl, vao, programInfo, bufferInfo, pivotVAO, pivotBufferInfo, eyeVAO, eyeBufferInfo, smileVAO, smileBufferInfo);
}

// Function to do the actual display of the objects
function drawScene(gl, vao, programInfo, bufferInfo, pivotVAO, pivotBufferInfo, eyeVAO, eyeBufferInfo, smileVAO, smileBufferInfo) {

    // Model data (current position, rotation, scale)
    const modelX = objects.model.transforms.t.x;
    const modelY = objects.model.transforms.t.y;
    const angle  = objects.model.transforms.rr.z;
    const scale  = [objects.model.transforms.s.x, objects.model.transforms.s.y];

    // Pivot data
    const pivotX = objects.pivot.transforms.t.x;
    const pivotY = objects.pivot.transforms.t.y;

    // Rotate model's relative position around pivot
    const dx = modelX - pivotX;
    const dy = modelY - pivotY;

    const cosA = Math.cos(angle);
    const sinA = Math.sin(angle);

    const rdx = dx * cosA - dy * sinA;
    const rdy = dx * sinA + dy * cosA;

    const finalX = pivotX + rdx;
    const finalY = pivotY + rdy;

    // Transformation Matrix
    const scaMat = M3.scale(scale);
    const rotLocal = M3.rotation(0);
    const traMat = M3.translation([finalX, finalY]);

    let transforms = M3.identity();
    transforms = M3.multiply(transforms, traMat);
    transforms = M3.multiply(transforms, rotLocal);
    transforms = M3.multiply(transforms, scaMat);

    // Draw main model (face)
    let uniforms =
    {
        u_resolution: [gl.canvas.width, gl.canvas.height],
        u_transforms: transforms,
        u_color: objects.model.color,
    };

    gl.useProgram(programInfo.program);
    twgl.setUniforms(programInfo, uniforms);

    gl.bindVertexArray(vao);
    twgl.drawBufferInfo(gl, bufferInfo);

    // Draw Left Eye
    const eyeScale = M3.scale([0.15, 0.25]);

    let leftEyeTransform = M3.multiply(
        transforms,
        M3.multiply(
            M3.translation([-35, 5]),
            eyeScale
        )
    );

    twgl.setUniforms(programInfo, {
        u_resolution: [gl.canvas.width, gl.canvas.height],
        u_transforms: leftEyeTransform,
        u_color: [0, 0, 0, 1],
    });
    gl.bindVertexArray(eyeVAO);
    twgl.drawBufferInfo(gl, eyeBufferInfo);

    // Draw Right Eye
    let rightEyeTransform = M3.multiply(
        transforms,
        M3.multiply(
            M3.translation([35, 5]),
            eyeScale
        )
    );

    twgl.setUniforms(programInfo, {
        u_resolution: [gl.canvas.width, gl.canvas.height],
        u_transforms: rightEyeTransform,
        u_color: [0, 0, 0, 1],
    });
    gl.bindVertexArray(eyeVAO);
    twgl.drawBufferInfo(gl, eyeBufferInfo);

    // Draw Pivot
    const pivotScale = [objects.pivot.transforms.s.x, objects.pivot.transforms.s.y];
    const pivotTranslate = [pivotX, pivotY];

    const pivotScaMat = M3.scale(pivotScale);
    const pivotTraMat = M3.translation(pivotTranslate);

    let pivotTransforms = M3.identity();
    pivotTransforms = M3.multiply(pivotTransforms, pivotTraMat);
    pivotTransforms = M3.multiply(pivotTransforms, pivotScaMat);

    let pivotUniforms = {
        u_resolution: [gl.canvas.width, gl.canvas.height],
        u_transforms: pivotTransforms,
        u_color: objects.pivot.color,
    };

    twgl.setUniforms(programInfo, pivotUniforms);
    gl.bindVertexArray(pivotVAO);
    twgl.drawBufferInfo(gl, pivotBufferInfo);

    // Draw mouth

    // Mouth size
    const mouthScale = M3.scale([0.4, 0.5]);

    // Mouth position
    let mouthTransform = M3.multiply(
        transforms,
        M3.multiply(
            M3.translation([0, 50]), 
            mouthScale
        )
    );

    twgl.setUniforms(programInfo, {
        u_resolution: [gl.canvas.width, gl.canvas.height],
        u_transforms: mouthTransform,
        u_color: [0, 0, 0, 1],
    });

    gl.bindVertexArray(smileVAO);
    twgl.drawBufferInfo(gl, smileBufferInfo);

    // Loop redraw
    requestAnimationFrame(() =>
    drawScene(gl, vao, programInfo, bufferInfo, pivotVAO, pivotBufferInfo, eyeVAO, eyeBufferInfo, smileVAO, smileBufferInfo)
);

}

function setupUI(gl)
{
    const gui = new GUI();

    // Face translation controls
    const traFolder = gui.addFolder('Translation');
    traFolder.add(objects.model.transforms.t, 'x', 0, gl.canvas.width); 
    traFolder.add(objects.model.transforms.t, 'y', 0, gl.canvas.height);

    // Face rotation controls
    const rotFolder = gui.addFolder('Rotation');
    rotFolder.add(objects.model.transforms.rr, 'z', 0, Math.PI * 2);

    // Face scale controls
    const scaFolder = gui.addFolder('Scale');
    scaFolder.add(objects.model.transforms.s, 'x', -5, 5);
    scaFolder.add(objects.model.transforms.s, 'y', -5, 5);

    gui.addColor(objects.model, 'color');

    // Pivot controls
    const pivotFolder = gui.addFolder('Pivot');
    pivotFolder.add(objects.pivot.transforms.t, 'x', 0, gl.canvas.width);
    pivotFolder.add(objects.pivot.transforms.t, 'y', 0, gl.canvas.height);
    pivotFolder.addColor(objects.pivot, 'color');
}

main()
