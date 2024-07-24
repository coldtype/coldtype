
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
    font.setScale(size, size); // Optional, if not given will be in font upem
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

    buffer.destroy();
    font.destroy();
    face.destroy();
    blob.destroy();

    var hb_glyphs = [];
    var ax = 0;
    var ay = 0;

    result.map((x) => {
      let p = new skia.Path();
      let commands = [];
      glyphs[x.g].map((g) => {
        commands.push(g);
        if (g.type == "M") {
          p.moveTo(...g.values);
        } else if (g.type == "Q") {
          p.quadTo(...g.values);
        } else if (g.type == "Z") {
          p.close();
        }
      });
      console.log(p);
      
      hb_glyphs.push(new HBGlyph(ax+x.dx, ay+x.dy, commands));
      ax += x.ax;
      ay += x.ay;
    });

    return hb_glyphs;
  }
}

function updateResult() {
  let variations = {};
  document.querySelectorAll("input[type='range']").forEach((el) => {
    variations[el.id] = el.value;
  });

  let paths = window.hbFont.getGlyphs(text.value, 1000, variations);
  console.log(paths);
}

async function loadWasmAndFont() {
  window.skia = await CanvasKitInit({locateFile: (file) => 'https://unpkg.com/canvaskit-wasm@0.19.0/bin/'+file});
  window.hbFont = await HBFont.loadFont(fontName.innerHTML);
  updateResult();

  let p = new skia.Path();
  p.moveTo(100, 200);

  console.log(p);
}

loadWasmAndFont();

// let font, hbFont;

// async function preload() {
//   font = loadFont("assets/fonts/PolymathVar.woff2");
//   hbFont = await HBFont.loadFont(fontName.innerHTML);
// }

// function setup() {
//   createCanvas(800, 400);
// }

// function draw() {
//   if (hbFont == undefined) {
//     return;
//   }

//   let glyphs = hbFont.getGlyphs("ASDF", 1000, {wght:100});

//   background(250);

//   glyphs.forEach((glyph) => {
//     let points = [];
//     let path = new g.Path(glyph.commands);
//     path = g.resampleByLength(path, 5);
    
//     for (let i=0; i<path.commands.length; i++) {
//       if (path.commands[i].type == "M") { points.push([]); }
      
//       if (path.commands[i].type != "Z") {
//         points[points.length-1].push(createVector(path.commands[i].x, path.commands[i].y));
//       }
//     }
  
//     translate(glyph.x, glyph.y);
//     for (let i=0; i<points.length; i++) {
//       fill("deeppink");
//       for (let j=0; j<points[i].length; j++) {
//         ellipse(points[i][j].x, points[i][j].y, 2, 2);
//       }
//     }
//   });
// }