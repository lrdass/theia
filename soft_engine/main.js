// import * as BABYLON from "babylonjs";

// import { CameraInputsManager } from "babylonjs";

class Camera {
  constructor() {
    this.position = BABYLON.Vector3.Zero();
    this.target = BABYLON.Vector3.Zero();
  }
}

class Device {
  constructor(canvas) {
    this.canvas = canvas;
    this.width = canvas.width;
    this.height = canvas.height;
    this.context = canvas.getContext("2d");
    this.depthBuffer = new Array(this.width * this.height);
  }

  drawLine(point1, point2) {
    // const distance = point2.subtract(point1).length();

    // if (distance < 2) {
    //   return;
    // }

    // const middlePoint = point1.add(point2.subtract(point1).scale(0.5));

    // this.drawPoint(middlePoint);

    // this.drawLine(point1, middlePoint);
    // this.drawLine(middlePoint, point2);

    var x0 = point1.x >> 0;
    var y0 = point1.y >> 0;
    var x1 = point2.x >> 0;
    var y1 = point2.y >> 0;
    var dx = Math.abs(x1 - x0);
    var dy = Math.abs(y1 - y0);
    var sx = x0 < x1 ? 1 : -1;
    var sy = y0 < y1 ? 1 : -1;
    var err = dx - dy;
    while (true) {
      this.drawPoint(new BABYLON.Vector2(x0, y0));
      if (x0 == x1 && y0 == y1) {
        break;
      }
      var e2 = 2 * err;
      if (e2 > -dy) {
        err -= dy;
        x0 += sx;
      }
      if (e2 < dx) {
        err += dx;
        y0 += sy;
      }
    }
  }

  clear() {
    this.context.clearRect(0, 0, this.width, this.height);
    this.backBuffer = this.context.getImageData(0, 0, this.width, this.height);

    for (var i = 0; i < this.depthBuffer.length; i++) {
      // Max possible value
      this.depthBuffer[i] = 10000000;
    }
  }
  present() {
    this.context.putImageData(this.backBuffer, 0, 0);
  }
  putPixel(x, y, z, color) {
    // https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Pixel_manipulation_with_canvas
    let index = (x >> 0) + (y >> 0) * this.width;

    if (this.depthBuffer[index] < z) {
      return; // Discard
    }

    this.depthBuffer[index] = z;

    index *= 4;

    this.backBuffer.data[index] = color.r * 60;
    this.backBuffer.data[index + 1] = color.g * 255;
    this.backBuffer.data[index + 2] = color.b * 255;
    this.backBuffer.data[index + 3] = color.a * 255;
  }

  drawPoint(point, color) {
    if (
      point.x >= 0 &&
      point.y >= 0 &&
      point.x <= this.width &&
      point.y <= this.height
    ) {
      this.putPixel(point.x, point.y, point.z, color);
    }
  }

  render(camera, meshes) {
    const viewMatrix = BABYLON.Matrix.LookAtLH(
      camera.position,
      camera.target,
      BABYLON.Vector3.Up()
    );
    const projectionMatrix = BABYLON.Matrix.PerspectiveFovLH(
      0.78,
      this.width / this.height,
      0.01,
      1.0
    );

    meshes.forEach((mesh) => {
      // apply rotation before translation
      // https://doc.babylonjs.com/resources/rotation_conventions
      const worldMatrix = BABYLON.Matrix.RotationYawPitchRoll(
        mesh.rotation.y,
        mesh.rotation.x,
        mesh.rotation.z
      ).multiply(
        BABYLON.Matrix.Translation(
          mesh.position.x,
          mesh.position.y,
          mesh.position.z
        )
      );

      const transformMatrix = worldMatrix
        .multiply(viewMatrix)
        .multiply(projectionMatrix);

      mesh.faces.forEach((faceVertexIndexes, index) => {
        const firstVertex = mesh.vertices[faceVertexIndexes[0]];
        const secondVertex = mesh.vertices[faceVertexIndexes[1]];
        const thirdVertex = mesh.vertices[faceVertexIndexes[2]];

        const point1 = this.project(firstVertex, transformMatrix);
        const point2 = this.project(secondVertex, transformMatrix);
        const point3 = this.project(thirdVertex, transformMatrix);

        // this.drawLine(point1, point2);
        // this.drawLine(point2, point3);
        // this.drawLine(point3, point1);
        let color =
          0.25 + ((index % mesh.faces.length) / mesh.faces.length) * 0.75;
        this.drawTriangle(
          point1,
          point2,
          point3,
          new BABYLON.Color4(color, color, color, 1)
        );
      });
    });
  }

  drawTriangle(p1, p2, p3, color) {
    // let orderedPoints = [point1, point2, point3].sort((p1, p2) => p2.y - p1.y);

    // const fillTopFlatTriangle = (p1, p2, p3) => {
    //   const m1 = (p3.x - p1.x) / (p3.y - p1.y);
    //   const m2 = (p3.x - p2.x) / (p3.y - p2.y);

    //   let b1 = p3.x;
    //   let b2 = p3.x;
    //   for (let y = p3.y; y > p1.y; y--) {
    //     let firstPoint = new BABYLON.Vector2(b1 >> 0, y);
    //     let secondPoint = new BABYLON.Vector2(b2 >> 0, y);
    //     b1 -= m1;
    //     b2 -= m2;
    //     debugger;
    //     this.drawLine(firstPoint, secondPoint);
    //   }
    // };

    // const fillBottomFlatTriangle = (p1, p2, p3) => {
    //   const m1 = (p2.x - p1.x) / (p2.y - p1.y);
    //   const m2 = (p3.x - p1.x) / (p3.y - p1.y);

    //   let b1 = p1.x;
    //   let b2 = p1.x;

    //   for (let y = p1.y; y <= p2.y; y++) {
    //     let firstPoint = new BABYLON.Vector2(b1 >> 0, y);
    //     let secondPoint = new BABYLON.Vector2(b2 >> 0, y);
    //     b1 += m1;
    //     b2 += m2;
    //     debugger;
    //     this.drawLine(firstPoint, secondPoint);
    //   }
    // };

    // const [p1, p2, p3] = orderedPoints;
    // if (p2.y === p3.y) {
    //   fillBottomFlatTriangle(p1, p2, p3);
    // } else if (p1.y === p2.y) {
    //   fillTopFlatTriangle(p1, p2, p3);
    // } else {
    //   const x4 = ((p3.x - p1.x) * (p2.y - p1.y)) / (p3.y, p1.y) + p1.x;
    //   const p4 = new BABYLON.Vector2(x4 >> 0, p2.y);
    //   debugger;
    //   fillBottomFlatTriangle(p1, p2, p4);
    //   fillTopFlatTriangle(p2, p4, p3);
    // }
    const clamp = (value, min, max) => {
      if (typeof min === "undefined") {
        min = 0;
      }
      if (typeof max === "undefined") {
        max = 1;
      }
      return Math.max(min, Math.min(value, max));
    };

    const interpolate = (min, max, gradient) => {
      return min + (max - min) * clamp(gradient);
    };

    const processScanLine = (y, pa, pb, pc, pd, color) => {
      // Thanks to current Y, we can compute the gradient to compute others values like
      // the starting X (sx) and ending X (ex) to draw between
      // if pa.Y == pb.Y or pc.Y == pd.Y, gradient is forced to 1
      var gradient1 = pa.y != pb.y ? (y - pa.y) / (pb.y - pa.y) : 1;
      var gradient2 = pc.y != pd.y ? (y - pc.y) / (pd.y - pc.y) : 1;

      var sx = interpolate(pa.x, pb.x, gradient1) >> 0;
      var ex = interpolate(pc.x, pd.x, gradient2) >> 0;

      var z1 = interpolate(pa.z, pb.z, gradient1);
      var z2 = interpolate(pc.z, pd.z, gradient2);
      // drawing a line from left (sx) to right (ex)
      for (var x = sx; x < ex; x++) {
        var gradient = (x - sx) / (ex - sx);
        var z = interpolate(z1, z2, gradient);
        this.drawPoint(new BABYLON.Vector3(x, y, z), color);
      }
    };

    if (p1.y > p2.y) {
      var temp = p2;
      p2 = p1;
      p1 = temp;
    }
    if (p2.y > p3.y) {
      var temp = p2;
      p2 = p3;
      p3 = temp;
    }
    if (p1.y > p2.y) {
      var temp = p2;
      p2 = p1;
      p1 = temp;
    }

    // inverse slopes
    var dP1P2;
    var dP1P3;

    // http://en.wikipedia.org/wiki/Slope
    // Computing slopes
    if (p2.y - p1.y > 0) {
      dP1P2 = (p2.x - p1.x) / (p2.y - p1.y);
    } else {
      dP1P2 = 0;
    }

    if (p3.y - p1.y > 0) {
      dP1P3 = (p3.x - p1.x) / (p3.y - p1.y);
    } else {
      dP1P3 = 0;
    }

    // First case where triangles are like that:
    // P1
    // -
    // --
    // - -
    // -  -
    // -   - P2
    // -  -
    // - -
    // -
    // P3
    if (dP1P2 > dP1P3) {
      for (var y = p1.y >> 0; y <= p3.y >> 0; y++) {
        if (y < p2.y) {
          processScanLine(y, p1, p3, p1, p2, color);
        } else {
          processScanLine(y, p1, p3, p2, p3, color);
        }
      }
    }
    // First case where triangles are like that:
    //       P1
    //        -
    //       --
    //      - -
    //     -  -
    // P2 -   -
    //     -  -
    //      - -
    //        -
    //       P3
    else {
      for (var y = p1.y >> 0; y <= p3.y >> 0; y++) {
        if (y < p2.y) {
          processScanLine(y, p1, p2, p1, p3, color);
        } else {
          processScanLine(y, p2, p3, p1, p3, color);
        }
      }
    }
  }

  project(coordinates, transformationMatrix) {
    const point = BABYLON.Vector3.TransformCoordinates(
      coordinates,
      transformationMatrix
    );
    // The transformed coordinates will be based on coordinate system
    // starting on the center of the screen. But drawing on screen normally starts
    // from top left. We then need to transform them again to have x:0, y:0 on top left.
    // to archieve that, I'm going to move -h/2 and -w/2
    const x = (point.x * this.width + this.width / 2) >> 0;
    const y = (-point.y * this.height + this.height / 2) >> 0;

    return new BABYLON.Vector3(x, y, point.z);
  }
}

class Mesh {
  constructor(name) {
    this.name = name;
    this.vertices = [];
    this.faces = [];
    this.rotation = BABYLON.Vector3.Zero();
    this.position = BABYLON.Vector3.Zero();
  }
}

const LoadJSONFileAsync = function (fileName, callback) {
  var jsonObject = {};
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.open("GET", fileName, true);
  xmlhttp.onreadystatechange = function () {
    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
      jsonObject = JSON.parse(xmlhttp.responseText);
      callback(CreateMeshesFromJSON(jsonObject));
    }
  };
  xmlhttp.send(null);
};

const CreateMeshesFromJSON = function (jsonObject) {
  var meshes = [];
  for (var meshIndex = 0; meshIndex < jsonObject.meshes.length; meshIndex++) {
    var verticesArray = jsonObject.meshes[meshIndex].vertices;
    // Faces
    var indicesArray = jsonObject.meshes[meshIndex].indices;

    var uvCount = jsonObject.meshes[meshIndex].uvCount;
    var verticesStep = 1;

    // Depending of the number of texture's coordinates per vertex
    // we're jumping in the vertices array  by 6, 8 & 10 windows frame
    switch (uvCount) {
      case 0:
        verticesStep = 6;
        break;
      case 1:
        verticesStep = 8;
        break;
      case 2:
        verticesStep = 10;
        break;
    }

    // the number of interesting vertices information for us
    var verticesCount = verticesArray.length / verticesStep;
    // number of faces is logically the size of the array divided by 3 (A, B, C)
    var facesCount = indicesArray.length / 3;
    var mesh = new Mesh(jsonObject.meshes[meshIndex].name);

    // Filling the Vertices array of our mesh first
    for (var index = 0; index < verticesCount; index++) {
      var x = verticesArray[index * verticesStep];
      var y = verticesArray[index * verticesStep + 1];
      var z = verticesArray[index * verticesStep + 2];
      mesh.vertices[index] = new BABYLON.Vector3(x, y, z);
    }

    // Then filling the Faces array
    for (var index = 0; index < facesCount; index++) {
      var a = indicesArray[index * 3];
      var b = indicesArray[index * 3 + 1];
      var c = indicesArray[index * 3 + 2];
      mesh.faces[index] = [a, b, c];
    }

    // Getting the position you've set in Blender
    var position = jsonObject.meshes[meshIndex].position;
    mesh.position = new BABYLON.Vector3(position[0], position[1], position[2]);
    meshes.push(mesh);
  }
  return meshes;
};

function loadJSONCompleted(meshesLoaded) {
  meshes = meshesLoaded;
  // Calling the HTML5 rendering loop
  requestAnimationFrame(render);
}

let canvas;
let mera;
let device;
let meshes = [];
document.addEventListener("DOMContentLoaded", init, false);

function render() {
  device.clear();

  for (var i = 0; i < meshes.length; i++) {
    // rotating slightly the mesh during each frame rendered
    meshes[i].rotation.y += 0.01;
  }

  device.render(mera, meshes);
  device.present();

  requestAnimationFrame(render);
}

function init() {
  canvas = document.getElementById("canvas");
  mera = new Camera();
  device = new Device(canvas);
  mera.position = new BABYLON.Vector3(0, 0, 10);
  mera.target = new BABYLON.Vector3(0, 0, 0);
  LoadJSONFileAsync("monkey.babylon", loadJSONCompleted);
}
