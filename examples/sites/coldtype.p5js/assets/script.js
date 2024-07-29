print = console.log

//'use strict';
var hb, fontBlob;

function pathToRelative(pathArray) {
  return pathArray;
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
    var os2 = face.reference_table("OS/2");
    console.log(os2);
    var string = new TextDecoder().decode(os2);
    console.log(string);
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

    var xmin = 10000;
    var xmax = -10000;
    var ymin = 10000;
    var ymax = -10000;
    ax = 0;
    ay = 0;
    var path = pathToRelative(result.map(function (x) {
      var result = glyphs[x.g].filter(function (command) {
        return command.type !== 'Z';
      }).map(function (command) {
        var result = command.values.map(function (p, i) {
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
    }).reduce((acc, val) => acc.concat(val), [])).map(x => x[0] + x.slice(1).join(' ')).join('').replace(/ -/g, ' -');
    var width = xmax - xmin;
    var height = ymax - ymin;

    var bbox = xmin + ' ' + ymin + ' ' + width + ' ' + height;

    svgResult.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" height="128" viewBox="' + bbox + '">' +
      '<path fill="#fff" d="' + path + '" /></svg>';

    // var hb_glyphs = [];
    // var ax = 0;
    // var ay = 0;

    // result.map((x) => {
    //   let commands = [];
    //   glyphs[x.g].map((g) => {
    //     commands.push(g);
    //   });
      
    //   hb_glyphs.push(new HBGlyph(ax+x.dx, ay+x.dy, commands));
    //   ax += x.ax;
    //   ay += x.ay;
    // });

    // return hb_glyphs;
  }
}

let font;
let hbFont;
let textInput;
let sampleFactorSlider;
let zSlider;
let animateCheckbox;
let bounds;
let zPos = 0;

function updateResult() {
  let paths = hbFont.getGlyphs("abc", 1000, {wght:900,opsz:72});
  console.log(paths);
}

async function preload() {
  // console.log("preload");
  let fontName = "assets/fonts/PolymathVar.woff2";
  // font = loadFont(fontName);
  hbFont = await HBFont.loadFont(fontName);
  //console.log(">", hbFont);
  updateResult();

  opentype.load(fontName, function(err, f) {
    if (err) {
      console.log(err);
    } else {
      font = f;
    }
    
    fontPath = font.getPath("a", 0, 0, 100);
    console.log(fontPath);
  });
}

function setup() {
  //createCanvas(windowWidth, windowHeight, WEBGL);
  return;

  textInput = createInput("abc");
  createElement("br");
  sampleFactorSlider = createSlider(0.01, 10, 2, 0.01);
  createElement("br");
  zSlider = createSlider(0, 1200, 0);
  animateCheckbox = createCheckbox("animate", true);
  // animateCheckbox.changed(autoAnimate);

  textInput.position(8, 8);
  sampleFactorSlider.position(8, 32);
  zSlider.position(8, 52);
  animateCheckbox.position(8, 72);
}

function draw() {
  return;
  if (hbFont == undefined) {
    return;
  }

  background(0);

  // animate automatically
  //autoAnimate();

  orbitControl();

  word = " " + textInput.value() + " ";

  //console.log(font);

  let pts = font.textToPoints(word, 0, 0, 10, {
    sampleFactor: sampleFactorSlider.value()*0.5,
    simplifyThreshold: 0,
  });

  let bounds = font.textBounds(word, 0, 0, 10);

  let multiplier = width / bounds.w;
  translate(-width / 4 - (bounds.w * multiplier) / 4, 0);
  translate(0, (bounds.h * multiplier) / 2);
  randomSeed(0);

  for (let i = 0; i < pts.length; i++) {
    stroke(255);

    point(
      pts[i].x * multiplier,
      pts[i].y * multiplier,
      zPos - zSlider.value() * random(0, 2.5)
    );
  }

  // let glyphs = hbFont.getGlyphs("ASDF", 1000, {wght:100});

  // background(250);

  // glyphs.forEach((glyph) => {
  //   let points = [];
  //   let path = new g.Path(glyph.commands);
  //   path = g.resampleByLength(path, 5);
    
  //   for (let i=0; i<path.commands.length; i++) {
  //     if (path.commands[i].type == "M") { points.push([]); }
      
  //     if (path.commands[i].type != "Z") {
  //       points[points.length-1].push(createVector(path.commands[i].x, path.commands[i].y));
  //     }
  //   }
  
  //   translate(glyph.x, glyph.y);
  //   for (let i=0; i<points.length; i++) {
  //     fill("deeppink");
  //     for (let j=0; j<points[i].length; j++) {
  //       ellipse(points[i][j].x, points[i][j].y, 2, 2);
  //     }
  //   }
  // });
}

function autoAnimate() {
  if (animateCheckbox.checked()) {
    sampleFactorSlider.value(map(sin(frameCount * 0.02), -1, 1, 0.01, 10));
    zSlider.value(map(sin(frameCount * 0.02), -1, 1, 1200, 0));
  }
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight, WEBGL);
}