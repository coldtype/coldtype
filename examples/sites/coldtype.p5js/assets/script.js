
'use strict';
var hb, fontBlob;

class HBFont {
  constructor(fontURL, fontBlob) {
    this.fontURL = fontURL;
    this.fontBlob = fontBlob;
  }

  static async loadFont(fontUrl) {
    if (window.hb === undefined) {
      const wasmResponse = await fetch("assets/hb.wasm");
      const wasmArrayBuffer = await wasmResponse.arrayBuffer();
      const wasmResult = await WebAssembly.instantiate(wasmArrayBuffer);
      window.hb = hbjs(wasmResult.instance);
    }
    
    const fontResponse = await fetch(fontPath);
    const fontArrayBuffer = await fontResponse.arrayBuffer();
    
    return new HBFont(fontURL, new Uint8Array(fontArrayBuffer));
  }

  // Method to get paths
  getPaths(text, size) {
    // Stub for getting paths
    // You can implement the actual logic to generate paths for the given text and size
    console.log(`Getting paths for text: "${text}" with size: ${size}`);
    return []; // Stub return with an empty array
  }
}

function updateResult() {
  var blob = hb.createBlob(fontBlob);
  var face = hb.createFace(blob, 0);
  var font = hb.createFont(face);
  font.setScale(1000, 1000); // Optional, if not given will be in font upem

  let variations = {};
  document.querySelectorAll("input[type='range']").forEach((el) => {
    variations[el.id] = el.value;
  });

  //font.setVariations({"wght": 900, "opsz": 72, "ital": 1});
  font.setVariations(variations);

  var buffer = hb.createBuffer();
  buffer.addText(text.value);
  buffer.guessSegmentProperties();
  // buffer.setDirection('ltr'); // optional as can be by guessSegmentProperties also
  hb.shape(font, buffer); // features are not supported yet
  var result = buffer.json(font);

  // returns glyphs paths, totally optional
  var glyphs = {};
  result.forEach(function (x) {
    if (glyphs[x.g]) return;
    glyphs[x.g] = font.glyphToJson(x.g);
  });

  buffer.destroy();
  font.destroy();
  face.destroy();
  blob.destroy();

  var xmin = 10000;
  var xmax = -10000;
  var ymin = 10000;
  var ymax = -10000;
  var ax = 0;
  var ay = 0;
  var path = pathToRelative(result.map(function (x) {
    var result = glyphs[x.g].filter(function (command) {
      return command.type !== 'Z';
    }).map(function (command) {
      var result = command.values.map(function (p, i) {
        // apply ax/ay/dx/dy to coords
        return i % 2 ? -(p + ay + x.dy) : p + ax + x.dx;
      }).map(function (x, i) {
        // bbox calc
        if (i % 2) {
          if (x < ymin) ymin = x;
          if (x > ymax) ymax = x;
        } else {
          if (x < xmin) xmin = x;
          if (x > xmax) xmax = x;
        }
        return x;
      });
      return [command.type].concat(result);
    });
    ax += x.ax; ay += x.ay;
    return result;
  }).reduce((acc, val) => acc.concat(val), [])).map(x => x[0] + x.slice(1).join(' ')).join('').replace(/ -/g, '-');
  
  var width = xmax - xmin;
  var height = ymax - ymin;
  var bbox = xmin + ' ' + ymin + ' ' + width + ' ' + height;

  svgResult.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" height="128" viewBox="' + bbox + '">' +
    '<path d="' + path + '" /></svg>';
}

const fontPath = fontName.innerHTML;

async function loadWasmAndFont() {
  const wasmResponse = await fetch("assets/hb.wasm");
  const wasmArrayBuffer = await wasmResponse.arrayBuffer();
  const wasmResult = await WebAssembly.instantiate(wasmArrayBuffer);
  
  window.hb = hbjs(wasmResult.instance);
  
  const fontResponse = await fetch(fontPath);
  const fontArrayBuffer = await fontResponse.arrayBuffer();
  
  window.fontBlob = new Uint8Array(fontArrayBuffer);
  updateResult();
}

loadWasmAndFont();

document.getElementById('text').addEventListener('keyup', function(e) {
  updateResult();
});

document.querySelectorAll("input[type='range']").forEach((el) => {
  el.addEventListener("input", (e) => {
    updateResult();
  });
});

// Totally optional, https://github.com/adobe-webplatform/Snap.svg/blob/7abe4d1/src/path.js#L532
function pathToRelative(pathArray) {
  if (!pathArray.length) return [];
  var x = pathArray[0][1], y = pathArray[0][2];
  var prevCmd = '';
  return [["M", x, y]].concat(pathArray.slice(1).map(function (pa) {
    var r = [prevCmd === pa[0] ? ' ' : pa[0].toLowerCase()].concat(pa.slice(1).map(function (z, i) {
      return z - ((i % 2) ? y : x);
    }));
    var lastPoint = r.slice(-2);
    x += lastPoint[0];
    y += lastPoint[1];
    prevCmd = pa[0];
    return r;
  }));
}