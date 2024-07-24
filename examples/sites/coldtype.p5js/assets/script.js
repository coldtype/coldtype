
//'use strict';
var hb, fontBlob;

class HBGlyph {
  constructor(x, y, path) {
    this.x = x;
    this.y = y;
    this.commands = path;
  }
}

class HBFont {
  constructor(fontURL, fontBlob) {
    this.fontURL = fontURL;
    this.fontBlob = fontBlob;
  }

  static async loadFont(_fontURL) {
    if (window.hb === undefined) {
      const wasmResponse = await fetch("assets/hb.wasm");
      const wasmArrayBuffer = await wasmResponse.arrayBuffer();
      const wasmResult = await WebAssembly.instantiate(wasmArrayBuffer);
      window.hb = hbjs(wasmResult.instance);
    }
    
    const fontResponse = await fetch(_fontURL);
    const fontArrayBuffer = await fontResponse.arrayBuffer();
    
    return new HBFont(_fontURL, new Uint8Array(fontArrayBuffer));
  }

  getGlyphs(text, size, variations={}) {
    var blob = hb.createBlob(this.fontBlob);
    var face = hb.createFace(blob, 0);
    var font = hb.createFont(face);
    font.setScale(1000, 1000); // Optional, if not given will be in font upem
    font.setVariations(variations);

    var buffer = hb.createBuffer();
    buffer.addText(text);
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


    // var paths = {};
    // result.forEach(function (x) {
    //   if (glyphs[x.g]) return;
    //   let jg = font.glyphToJson(x.g);
    //   let fcs = [];
    //   jg.forEach((g) => {
    //     let fc = {type:g.type};
    //     if (g.values) {
    //       g.values.forEach((v, idx) => {
    //         let i = Math.floor(idx/2);
    //         if (idx%2 == 0) {
    //           fc[`x${i==0?'':i}`] = v;
    //         } else {
    //           fc[`y${i==0?'':i}`] = v;
    //         }
    //       });
    //     }
    //     fcs.push(fc);
    //   });
    //   let path = new window.g.Path(fcs)
    //   glyphs[x.g] = ;
    // });

    buffer.destroy();
    font.destroy();
    face.destroy();
    blob.destroy();

    var hb_glyphs = [];
    var ax = 0;
    var ay = 0;

    result.map((x) => {
      let fcs = [];
      glyphs[x.g].map((v) => {
        let fc = {type:g.type};
        if (g.values) {
          g.values.forEach((v, idx) => {
            let i = Math.floor(idx/2);
            if (idx%2 == 0) {
              fc[`x${i==0?'':i}`] = v;
            } else {
              fc[`y${i==0?'':i}`] = v;
            }
          });
        }
        fcs.push(fc);
      });
      hb_glyphs.push(new HBGlyph(ax+x.dx, ay+x.dy, fcs));
      ax += x.ax;
      ay += x.ay;
    });

    return hb_glyphs;

    // result.map(function (x) {
    //   var result = glyphs[x.g].filter(function (command) {
    //     return command.type !== 'Z';
    //   }).map(function (command) {
    //     var result = command.values.map(function (p, i) {
    //       // apply ax/ay/dx/dy to coords
    //       return i % 2 ? -(p + ay + x.dy) : p + ax + x.dx;
    //     });
    //     return [command.type].concat(result);
    //   });
    //   ax += x.ax; ay += x.ay;
    //   return result;
    // });

    //.reduce((acc, val) => acc.concat(val), [])).map(x => x[0] + x.slice(1).join(' ')).join('').replace(/ -/g, '-');

    return paths;
  }

  glyphsToSVG(glyphs) {
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
    
    return '<svg xmlns="http://www.w3.org/2000/svg" height="128" viewBox="' + bbox + '">' +
    '<path d="' + path + '" /></svg>';
  }
}

function updateResult() {
  let variations = {};
  document.querySelectorAll("input[type='range']").forEach((el) => {
    variations[el.id] = el.value;
  });

  let paths = window.hbFont.getGlyphs(text.value, 1000, variations);
  console.log(paths);

  //let svg = window.hbFont.glyphsToSVG(glyphs);
  //svgResult.innerHTML = svg;
}

const fontPath = fontName.innerHTML;

async function loadWasmAndFont() {
  window.hbFont = await HBFont.loadFont(fontName.innerHTML);
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