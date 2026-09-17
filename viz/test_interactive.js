"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const test = require("node:test");
const B = require("./interactive/bloch.js");
const {mount, drawScene} = require("./interactive/app.js");
const assets = path.join(__dirname, "interactive");
const scope = {};
vm.runInNewContext(fs.readFileSync(path.join(assets, "evidence.js"), "utf8"), scope);
const data = JSON.parse(JSON.stringify(scope.BLOCH_EVIDENCE));
const copy = (value) => JSON.parse(JSON.stringify(value));
const near = (actual, expected) => assert.ok(Math.abs(actual - expected) < 1e-9, `${actual} != ${expected}`);
const vector = (actual, expected) => { assert.equal(actual.length, 3); actual.forEach((n, i) => near(n, expected[i])); };

function fixture(zero = 8, one = 2) {
  const shots = zero + one, problem = copy(data.problems[0]);
  problem.id = "16_error_correction";
  problem.measurement_width = 1;
  problem.run = {...problem.run, status: "available", execution: "local-simulator", target: "local-simulator",
    shots, histogram: [{outcome: "[Zero]", count: zero}, {outcome: "[One]", count: one}]};
  problem.marginals = [{
    status: "available", reason: null, bit: 0, measurement_width: 1, shots,
    counts: {"0": zero, "1": one}, p0: zero / shots, p1: one / shots,
    z: (zero - one) / shots, x: null, y: null,
    representation: "measurement-derived diagonal-state representation",
  }];
  return {...copy(data), problems: [problem]};
}

function missingFixture() {
  const result = fixture();
  const problem = result.problems[0];
  problem.measurement_width = null;
  problem.run = {...problem.run, status: "missing", shots: null, histogram: []};
  problem.marginals[0] = {...problem.marginals[0], status: "unavailable", reason: "No matching simulator run",
    measurement_width: null, shots: null, counts: null, z: null, p0: null, p1: null};
  return result;
}

test("all twenty delivered problems: every bit has honest Z-only evidence", () => {
  const lab = new B.Lab(data);
  assert.equal(lab.problems.length, 20);
  assert.equal(lab.mode, "evidence");
  for (const p of lab.problems) {
    lab.selectProblem(p.id);
    for (const m of p.marginals) {
      lab.selectBit(m.bit);
      const view = lab.snapshot();
      for (const key of ["x", "y", "theta", "phi", "amplitudes"]) assert.equal(view[key], null);
      if (m.status === "available") {
        const n0 = p.run.histogram.reduce((sum, row) => sum +
          (row.outcome.replace(/[\[\]]/g, "").split(",")[m.bit].trim() === "Zero" ? row.count : 0), 0);
        near(view.z, (2 * n0 - p.run.shots) / p.run.shots);
        vector(view.marker, [0, 0, view.z]);
      } else assert.equal(view.marker, null);
    }
  }
});

test("positive, negative, balanced and unavailable markers are distinct", () => {
  for (const [n0, n1, z] of [[8, 2, .6], [2, 8, -.6], [5, 5, 0], [0, 10, -1]]) {
    const lab = new B.Lab(fixture(n0, n1));
    vector(lab.snapshot().marker, [0, 0, z]);
    assert.equal(lab.snapshot().amplitudes, null);
  }
  const missing = new B.Lab(missingFixture()).snapshot();
  assert.equal(missing.marker, null);
  assert.equal(missing.z, null);
});

test("data validation rejects wrong signs, transverse fabrication and unsupported evidence", () => {
  for (const mutate of [
    (p) => { p.marginals[0].z *= -1; },
    (p) => { p.marginals[0].x = .8; },
    (p) => { p.marginals[0].y = 0; },
    (p) => { p.marginals[0].amplitudes = [1, 0]; },
    (p) => { p.marginals[0].p0 = .2; },
    (p) => { p.run.target = "ionq.simulator"; },
    (p) => { p.marginals[0].counts["0"] = -8; },
    (p) => { p.marginals[0].shots = Number.MAX_SAFE_INTEGER + 1; },
  ]) {
    const invalid = fixture(); mutate(invalid.problems[0]);
    assert.throws(() => new B.Lab(invalid));
  }
  const missing = missingFixture();
  missing.problems[0].marginals[0].z = 0;
  assert.throws(() => new B.Lab(missing), /Unavailable/);
});

test("gates have correct Bloch handedness, including both dagger gates", () => {
  const r = Math.SQRT1_2;
  for (const [initial, gate, expected] of [
    ["zero", "X", [0, 0, -1]], ["zero", "Y", [0, 0, -1]], ["plus", "Z", [-1, 0, 0]],
    ["zero", "H", [1, 0, 0]], ["one", "H", [-1, 0, 0]], ["plusi", "H", [0, -1, 0]],
    ["plus", "S", [0, 1, 0]], ["plus", "Sdg", [0, -1, 0]],
    ["plus", "T", [r, r, 0]], ["plus", "Tdg", [r, -r, 0]],
  ]) {
    const lab = new B.Lab(data); lab.setMode("explore"); lab.start(initial); lab.gate(gate);
    vector(lab.snapshot().marker, expected);
  }
});

test("arbitrary normalized axes, finite inputs and repeated rotations preserve a pure state", () => {
  vector(B.rotate([0, 0, 1], [1, 0, 0], 90), [0, -1, 0]);
  vector(B.rotate([0, 0, 1], [0, 9, 0], 90), [1, 0, 0]);
  vector(B.rotate([0, 0, 1], [1, 0, 1], 180), [1, 0, 0]);
  vector(B.rotate([0, 0, 1], [1, 2, 3], 360), [0, 0, 1]);
  for (const axis of [[0, 0, 0], [NaN, 0, 1], [Infinity, 0, 0], [1, 0]]) {
    assert.throws(() => B.rotate([0, 0, 1], axis, 90));
  }
  assert.throws(() => B.rotate([0, 0, 1], [1, 0, 0], NaN));
  let current = B.fromAngles(64, -21);
  for (let i = 0; i < 300; i++) current = B.rotate(current, [1, 2, 3], 13);
  near(Math.hypot(...current), 1);
});

test("pure theta/phi and complex amplitudes agree, with explicit pole convention", () => {
  for (const [theta, phi] of [[37, 63], [90, -90], [90, 360], [120, 270], [180, 45], [0, 20]]) {
    const v = B.fromAngles(theta, phi), state = B.pureReadout(v);
    near(state.theta, theta);
    if (theta === 0 || theta === 180) assert.equal(state.phi, null);
    else near(state.phi, (phi % 360 + 360) % 360);
    const [a] = state.amplitudes.alpha, [br, bi] = state.amplitudes.beta;
    near(a * a + br * br + bi * bi, 1);
    vector([2 * a * br, 2 * a * bi, a * a - br * br - bi * bi], v);
  }
});

test("exploration cannot mutate evidence, even through exported or caller-owned objects", () => {
  const original = fixture(), lab = new B.Lab(original), before = lab.snapshot();
  for (const action of [() => lab.gate("H"), () => lab.rotation([1, 0, 0], 90),
    () => lab.start("plus"), () => lab.undo(), () => lab.reset()]) assert.throws(action, /only allowed/);
  lab.setMode("explore");
  vector(lab.snapshot().marker, [0, 0, 1]);
  assert.match(lab.snapshot().initial.label, /Explicit default convention/);
  lab.gate("H"); lab.gate("S");
  assert.equal(lab.snapshot().problem_id, undefined);
  lab.setMode("evidence");
  assert.deepEqual(lab.snapshot(), before);
  const exported = lab.snapshot(); exported.marginal.z = 1; exported.marker[0] = 1;
  original.problems[0].marginals[0].z = 1;
  assert.deepEqual(lab.snapshot(), before);
  assert.throws(() => { lab.problem.marginals[0].z = 1; }, TypeError);
  lab.setMode("explore");
  vector(lab.snapshot().marker, [0, 1, 0]);
});

test("undo and reset retain the explicitly selected initial state; invalid edits are atomic", () => {
  const lab = new B.Lab(data); lab.setMode("explore"); lab.start("one");
  lab.gate("X"); lab.gate("H"); lab.undo();
  vector(lab.snapshot().marker, [0, 0, 1]);
  lab.reset(); vector(lab.snapshot().marker, [0, 0, -1]); assert.equal(lab.canUndo, false);
  lab.start("custom", 90, 45);
  const before = lab.snapshot();
  for (const action of [() => lab.start("custom", -1, 0), () => lab.start("missing"),
    () => lab.rotation([0, 0, 0], 1), () => lab.gate("missing"), () => lab.selectBit(-1)]) {
    assert.throws(action); assert.deepEqual(lab.snapshot(), before);
  }
  lab.gate("Tdg"); lab.undo(); assert.deepEqual(lab.snapshot(), before);
});

// Minimal DOM/Canvas event harness: runs the actual app handlers without a DOM package.
class Element {
  constructor(tag, attrs = {}) {
    this.tag = tag; this.attrs = attrs; this.children = []; this.listeners = {};
    this.style = {}; this.dataset = {}; this._value = attrs.value ?? null;
    this.hidden = "hidden" in attrs; this.disabled = "disabled" in attrs;
    for (const [key, value] of Object.entries(attrs)) if (key.startsWith("data-")) this.dataset[key.slice(5)] = value;
  }
  get value() { return this._value ?? (this.tag === "select" ? this.children[0]?.value : "") ?? ""; }
  set value(value) { this._value = String(value); }
  set textContent(value) { this.text = String(value); this.children = []; }
  get textContent() { return this.text ?? this.children.map((c) => c.textContent).join(""); }
  setAttribute(key, value) { this.attrs[key] = value; }
  appendChild(child) { child.parentElement = this; this.children.push(child); return child; }
  replaceChildren(...children) { this.children = []; this.text = null; children.forEach((child) => this.appendChild(child)); }
  remove() { this.parentElement.children = this.parentElement.children.filter((c) => c !== this); }
  addEventListener(event, handler) { (this.listeners[event] ??= []).push(handler); }
  fire(name, props = {}) {
    const event = {preventDefault() { this.prevented = true; }, ...props};
    for (const handler of this.listeners[name] ?? []) handler(event);
    return event;
  }
  click() { if (!this.disabled) this.fire("click"); }
  focus() {}
  setPointerCapture() {}
  querySelectorAll(selector) {
    const matches = (node) => selector.split(",").some((s) => {
      s = s.trim();
      return s.startsWith("[") ? s.slice(1, -1) in node.attrs : node.tag === s;
    });
    return this.children.flatMap((child) => [...(matches(child) ? [child] : []), ...child.querySelectorAll(selector)]);
  }
  getBoundingClientRect() { return {width: 800, height: 600}; }
  getContext() { return this.context; }
}

class Context {
  constructor() { this.fills = []; this.strokes = []; }
  setTransform() {}
  clearRect() { this.fills = []; this.strokes = []; }
  createRadialGradient() { return {addColorStop() {}}; }
  beginPath() { this.path = []; }
  arc(...args) { this.path.push({arc: args}); }
  moveTo(...args) { this.path.push({move: args}); }
  lineTo(...args) { this.path.push({line: args}); }
  closePath() {}
  fill() { this.fills.push({style: this.fillStyle, path: copy(this.path)}); }
  stroke() { this.strokes.push({style: this.strokeStyle, path: copy(this.path), width: this.lineWidth}); }
  setLineDash() {}
  fillText() {}
}

function harness(evidence = data) {
  const document = new Element("document"), stack = [document], ids = new Map();
  const html = fs.readFileSync(path.join(assets, "index.html"), "utf8");
  for (const match of html.matchAll(/<(\/?)([a-z][\w-]*)([^>]*)>/gi)) {
    const [, closing, tag, raw] = match;
    if (closing) { if (stack.at(-1).tag === tag) stack.pop(); continue; }
    const attrs = {};
    for (const a of raw.matchAll(/([\w-]+)(?:="([^"]*)")?/g)) attrs[a[1]] = a[2] ?? "";
    const element = new Element(tag, attrs);
    stack.at(-1).appendChild(element);
    if (attrs.id) ids.set(attrs.id, element);
    if (tag === "body") document.body = element;
    if (!["input", "meta", "link", "br"].includes(tag)) stack.push(element);
  }
  document.getElementById = (id) => { assert.ok(ids.has(id), `Unknown UI ID: ${id}`); return ids.get(id); };
  document.createElement = (tag) => new Element(tag);
  const canvas = ids.get("sphere"); canvas.context = new Context();
  const downloads = [];
  const window = {
    devicePixelRatio: 1.5, Blob, addEventListener() {}, setTimeout(callback) { callback(); },
    URL: {createObjectURL(blob) { downloads.push(blob); return "blob:local-test"; }, revokeObjectURL() {}},
  };
  const app = mount(document, window, evidence, B);
  return {app, document, window, downloads, canvas, $: (id) => ids.get(id)};
}

test("Canvas draws the actual signed interior marker, not a normalized or fabricated vector", () => {
  for (const [n0, n1, z] of [[8, 2, .6], [2, 8, -.6], [5, 5, 0]]) {
    const canvas = new Element("canvas"); canvas.context = new Context();
    const camera = {yaw: .5, pitch: .4, zoom: 1};
    drawScene(canvas, new B.Lab(fixture(n0, n1)).snapshot(), camera, 1, B);
    const markers = canvas.context.fills.filter((fill) =>
      fill.style === "#9ae0c0" && fill.path[0]?.arc?.[2] === 6);
    assert.equal(markers.length, 1);
    const [x, y] = markers[0].path[0].arc;
    near(x, 400); near(y, 300 - 600 * .32 * z * Math.cos(.4));
  }
  const h = harness(missingFixture());
  assert.equal(h.canvas.context.fills.filter((f) => f.path[0]?.arc?.[2] === 6).length, 0);
  assert.match(h.$("evidence-summary").textContent, /Unavailable.*No marker/);
  assert.equal(h.$("read-z").textContent, "Unavailable");
});

test("actual UI selectors, mode buttons, gates, readouts and reset/undo remain separated", () => {
  const {$, document, app} = harness();
  assert.equal($("problem").children.length, 20);
  assert.equal($("read-x").textContent, "Unknown");
  assert.equal($("amplitudes").hidden, true);
  $("problem").value = "01_hubbard"; $("problem").fire("change");
  assert.equal($("bit").children.length, 2);
  $("bit").value = "1"; $("bit").fire("change");
  const expected = app.lab.snapshot();
  assert.equal($("read-z").textContent, expected.z.toFixed(5));
  $("explore-mode").click();
  assert.equal($("evidence-controls").hidden, true);
  assert.equal(document.body.dataset.mode, "explore");
  vector(app.lab.snapshot().marker, [0, 0, 1]);
  const gates = document.querySelectorAll("[data-gate]");
  gates.find((b) => b.dataset.gate === "H").click();
  assert.equal($("read-x").textContent, "1.00000");
  assert.equal($("amplitudes").hidden, false);
  $("undo").click(); assert.equal($("read-z").textContent, "1.00000");
  gates.find((b) => b.dataset.gate === "X").click();
  $("reset-state").click(); assert.equal($("read-z").textContent, "1.00000");
  $("evidence-mode").click();
  assert.deepEqual(app.lab.snapshot(), expected);
  assert.equal($("amplitudes").textContent, "");
  assert.equal($("read-theta").textContent, "Unknown");
  assert.equal($("read-phi").textContent, "Unknown");
  assert.equal($("explore-controls").hidden, true);
  assert.ok(gates.every((b) => b.disabled));
  gates[0].fire("click");
  assert.match($("input-error").textContent, /only allowed/);
  assert.deepEqual(app.lab.snapshot(), expected);
});

test("camera keyboard, buttons, pointer orbit, pinch and wheel alter projection only", () => {
  const {app, canvas, document} = harness(fixture());
  const before = app.lab.snapshot(), initial = {...app.camera};
  assert.equal(canvas.fire("keydown", {key: "ArrowRight"}).prevented, true);
  assert.notEqual(app.camera.yaw, initial.yaw);
  canvas.fire("wheel", {deltaY: -60}); assert.ok(app.camera.zoom > 1);
  canvas.fire("pointerdown", {pointerId: 1, pointerType: "touch", clientX: 50, clientY: 50});
  canvas.fire("pointermove", {pointerId: 1, clientX: 80, clientY: 60});
  assert.notEqual(app.camera.pitch, initial.pitch);
  canvas.fire("pointerdown", {pointerId: 2, pointerType: "touch", clientX: 120, clientY: 60});
  const zoom = app.camera.zoom;
  canvas.fire("pointermove", {pointerId: 2, clientX: 140, clientY: 60});
  assert.ok(app.camera.zoom > zoom);
  canvas.fire("pointercancel", {pointerId: 1}); canvas.fire("pointerup", {pointerId: 2});
  document.querySelectorAll("[data-camera]").find((b) => b.dataset.camera === "reset").click();
  assert.deepEqual(app.camera, initial);
  assert.deepEqual(app.lab.snapshot(), before);
});

test("custom-state and arbitrary-axis form events validate before changing state", () => {
  const {$, app} = harness();
  $("explore-mode").click();
  $("initial-state").value = "custom"; $("initial-state").fire("change");
  assert.equal($("initial-angles").hidden, false);
  $("initial-theta").value = "90"; $("initial-phi").value = "90"; $("initial-form").fire("submit");
  vector(app.lab.snapshot().marker, [0, 1, 0]);
  $("rotation-axis").value = "custom"; $("rotation-axis").fire("change");
  $("axis-x").value = "0"; $("axis-y").value = "0"; $("axis-z").value = "1";
  $("rotation-angle").value = "90"; $("rotation-form").fire("submit");
  vector(app.lab.snapshot().marker, [-1, 0, 0]);
  const before = app.lab.snapshot();
  $("axis-z").value = "0"; $("rotation-form").fire("submit");
  assert.match($("input-error").textContent, /nonzero/);
  assert.deepEqual(app.lab.snapshot(), before);
  $("rotation-angle").value = ""; $("rotation-form").fire("submit");
  assert.match($("input-error").textContent, /finite number/);
  assert.deepEqual(app.lab.snapshot(), before);
});

test("export click produces labeled JSON with no evidence/exploration value leakage", async () => {
  const {$, app, downloads} = harness(fixture());
  $("export").click();
  const evidence = JSON.parse(await downloads[0].text());
  assert.equal(evidence.mode, "evidence"); assert.equal(evidence.amplitudes, null);
  assert.equal(evidence.x, null); near(evidence.z, .6);
  $("explore-mode").click(); app.lab.gate("H"); $("export").click();
  const exploration = JSON.parse(await downloads[1].text());
  assert.equal(exploration.mode, "explore");
  assert.match(exploration.label, /NOT run evidence/);
  assert.equal(exploration.run, undefined); assert.equal(exploration.problem_id, undefined);
  assert.ok(exploration.amplitudes); vector(exploration.marker, [1, 0, 0]);
  $("evidence-mode").click(); $("export").click();
  assert.deepEqual(JSON.parse(await downloads[2].text()), evidence);
});

test("regression guards demonstrably kill wrong-sign and evidence/exploration-mixing mutants", () => {
  const source = fs.readFileSync(path.join(assets, "bloch.js"), "utf8");
  function load(text) {
    const context = {module: {exports: {}}};
    vm.runInNewContext(text, context);
    return context.module.exports;
  }
  const checks = [
    (Module) => {
      const lab = new Module.Lab(fixture());
      vector(lab.snapshot().marker, [0, 0, .6]);
    },
    (Module) => {
      const lab = new Module.Lab(fixture()); lab.setMode("explore"); lab.gate("H"); lab.setMode("evidence");
      vector(lab.snapshot().marker, [0, 0, .6]);
    },
    (Module) => assert.throws(() => new Module.Lab(fixture()).gate("H"), /only allowed/),
  ];
  const mutants = [
    source.replace("[0, 0, marginal.z]", "[0, 0, -marginal.z]"),
    source.replace("[0, 0, marginal.z]", "this.#history.at(-1).vector"),
    source.replace('if (this.#mode !== "explore")', "if (false)"),
  ];
  checks.forEach((check, i) => {
    check(load(source));
    assert.notEqual(mutants[i], source);
    const mutant = load(mutants[i]); // Syntax/runtime-load errors do not count as catching a regression.
    assert.throws(() => check(mutant), {name: "AssertionError"});
  });
});
