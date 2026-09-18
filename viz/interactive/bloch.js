/* Original Bloch geometry and state model. No browser or rendering dependencies. */
(function (root) {
  "use strict";
  const EPS = 1e-10;
  const DEG = Math.PI / 180;
  const clone = (value) => JSON.parse(JSON.stringify(value));
  const close = (a, b) => Number.isFinite(a) && Math.abs(a - b) < EPS;
  const clamp = (n, low, high) => Math.min(high, Math.max(low, n));
  const clean = (n) => Math.abs(n) < EPS ? 0 : n;

  function freeze(value) {
    if (value && typeof value === "object") {
      Object.values(value).forEach(freeze);
      Object.freeze(value);
    }
    return value;
  }

  function validateEvidence(data) {
    if (data?.kind !== "qgc-bloch-evidence" || data.schema_version !== "1.0" ||
        !Array.isArray(data.problems) || !data.problems.length) {
      throw new Error("Unsupported evidence file. Regenerate with python -m viz.build interactive.");
    }
    const ids = new Set();
    for (const problem of data.problems) {
      if (typeof problem.id !== "string" || ids.has(problem.id)) throw new Error("Invalid problem IDs");
      ids.add(problem.id);
      const width = problem.measurement_width;
      if (width !== null && (!Number.isSafeInteger(width) || width < 1)) {
        throw new Error("Invalid returned measurement width");
      }
      if (!Array.isArray(problem.marginals) || problem.marginals.length !== (width ?? 1)) {
        throw new Error("Incomplete returned-bit evidence");
      }
      problem.marginals.forEach((m, bit) => {
        if (m.bit !== bit || m.measurement_width !== width || m.x !== null || m.y !== null ||
            "amplitudes" in m || "phase" in m ||
            m.representation !== "measurement-derived diagonal-state representation") {
          throw new Error("Evidence cannot contain a reconstructed pure state or transverse components");
        }
        if (m.status === "unavailable") {
          if (!m.reason || ["z", "p0", "p1", "counts", "shots"].some((key) => m[key] !== null)) {
            throw new Error("Unavailable evidence must have no measured values");
          }
          return;
        }
        if (m.status !== "available" || width === null ||
            problem.run?.execution !== "local-simulator" ||
            problem.run?.target !== "local-simulator" || problem.run?.status !== "available") {
          throw new Error("Unsupported measurement contract");
        }
        const n0 = m.counts?.["0"], n1 = m.counts?.["1"];
        if (![m.shots, n0, n1].every(Number.isSafeInteger) || m.shots <= 0 ||
            n0 < 0 || n1 < 0 || n0 + n1 !== m.shots || m.shots !== problem.run.shots ||
            !close(m.p0, n0 / m.shots) || !close(m.p1, n1 / m.shots) ||
            !close(m.z, (n0 - n1) / m.shots)) {
          throw new Error("Invalid Z evidence: expected (n0 - n1) / shots");
        }
      });
    }
    return data;
  }

  function unit(vector) {
    if (!Array.isArray(vector) || vector.length !== 3 || !vector.every(Number.isFinite)) {
      throw new Error("Axis must have three finite coordinates");
    }
    const length = Math.hypot(...vector);
    if (!Number.isFinite(length) || length < EPS) throw new Error("Choose a nonzero finite axis");
    return vector.map((n) => n / length);
  }

  function rotate(vector, axis, degrees) {
    if (!Number.isFinite(degrees)) throw new Error("Rotation angle must be finite");
    const [nx, ny, nz] = unit(axis), [x, y, z] = unit(vector);
    const angle = (degrees % 360) * DEG, c = Math.cos(angle), s = Math.sin(angle);
    const dot = nx * x + ny * y + nz * z;
    return unit([
      x * c + (ny * z - nz * y) * s + nx * dot * (1 - c),
      y * c + (nz * x - nx * z) * s + ny * dot * (1 - c),
      z * c + (nx * y - ny * x) * s + nz * dot * (1 - c),
    ]).map(clean);
  }

  function fromAngles(theta, phi) {
    if (!Number.isFinite(theta) || !Number.isFinite(phi) || theta < 0 || theta > 180) {
      throw new Error("Theta must be 0–180 degrees and phi must be finite");
    }
    const t = theta * DEG, p = (phi % 360) * DEG;
    return [Math.sin(t) * Math.cos(p), Math.sin(t) * Math.sin(p), Math.cos(t)].map(clean);
  }

  function pureReadout(vector) {
    const [x, y, z] = unit(vector).map(clean);
    const theta = Math.acos(clamp(z, -1, 1)) / DEG;
    const phi = Math.hypot(x, y) < EPS ? null : (Math.atan2(y, x) / DEG + 360) % 360;
    const alpha = Math.sqrt(Math.max(0, (1 + z) / 2));
    const betaSize = Math.sqrt(Math.max(0, (1 - z) / 2));
    const phase = (phi ?? 0) * DEG;
    return {
      x, y, z, theta, phi,
      amplitudes: {
        alpha: [alpha, 0],
        beta: [clean(betaSize * Math.cos(phase)), clean(betaSize * Math.sin(phase))],
      },
    };
  }

  const STATES = freeze({
    zero: {label: "|0⟩ (+Z)", vector: [0, 0, 1]},
    one: {label: "|1⟩ (−Z)", vector: [0, 0, -1]},
    plus: {label: "|+⟩ (+X)", vector: [1, 0, 0]},
    minus: {label: "|−⟩ (−X)", vector: [-1, 0, 0]},
    plusi: {label: "|+i⟩ (+Y)", vector: [0, 1, 0]},
    minusi: {label: "|−i⟩ (−Y)", vector: [0, -1, 0]},
  });
  const GATES = freeze({
    X: [[1, 0, 0], 180], Y: [[0, 1, 0], 180], Z: [[0, 0, 1], 180],
    H: [[1, 0, 1], 180], S: [[0, 0, 1], 90], Sdg: [[0, 0, 1], -90],
    T: [[0, 0, 1], 45], Tdg: [[0, 0, 1], -45],
  });

  class Lab {
    #data;
    #mode = "evidence";
    #problem;
    #bit = 0;
    #initial = {label: "Explicit default convention: |0⟩ (+Z)", vector: [0, 0, 1]};
    #history = [];

    constructor(data) {
      this.#data = freeze(clone(validateEvidence(data)));
      this.#problem = this.#data.problems.find((p) => p.id === "16_error_correction") ??
        this.#data.problems[0];
      this.#history = [clone(this.#initial)];
    }
    get problems() { return this.#data.problems; }
    get problem() { return this.#problem; }
    get bit() { return this.#bit; }
    get mode() { return this.#mode; }
    get canUndo() { return this.#mode === "explore" && this.#history.length > 1; }

    selectProblem(id) {
      const problem = this.problems.find((p) => p.id === id);
      if (!problem) throw new Error("Unknown problem");
      this.#problem = problem;
      this.#bit = 0;
    }
    selectBit(bit) {
      if (!Number.isInteger(bit) || bit < 0 || bit >= this.#problem.marginals.length) {
        throw new Error("Returned bit unavailable");
      }
      this.#bit = bit;
    }
    setMode(mode) {
      if (!["evidence", "explore"].includes(mode)) throw new Error("Unknown mode");
      this.#mode = mode;
    }
    #requireExplore() {
      if (this.#mode !== "explore") throw new Error("Gates and state edits are only allowed in exploration");
    }
    start(state, theta = 0, phi = 0) {
      this.#requireExplore();
      const initial = state === "custom"
        ? {label: `User pure state: θ=${theta}°, φ=${phi}°`, vector: fromAngles(theta, phi)}
        : STATES[state];
      if (!initial) throw new Error("Unknown initial pure state");
      this.#initial = clone(initial);
      this.#history = [clone(initial)];
    }
    rotation(axis, degrees, label = null) {
      this.#requireExplore();
      const current = this.#history.at(-1);
      const vector = rotate(current.vector, axis, degrees);
      this.#history.push({vector, label: label ?? `R(${axis.join(", ")}) ${degrees}°`});
    }
    gate(name) {
      this.#requireExplore();
      if (!GATES[name]) throw new Error("Unknown gate");
      this.rotation(...GATES[name], name.replace("dg", "†"));
    }
    undo() {
      this.#requireExplore();
      if (this.canUndo) this.#history.pop();
    }
    reset() {
      this.#requireExplore();
      this.#history = [clone(this.#initial)];
    }
    snapshot() {
      if (this.#mode === "evidence") {
        const marginal = this.#problem.marginals[this.#bit];
        return {
          mode: "evidence", problem_id: this.#problem.id, bit: this.#bit,
          label: "Evidence · diagonal-state view, not tomography",
          marker: marginal.status === "available" ? [0, 0, marginal.z] : null,
          x: null, y: null, z: marginal.z, theta: null, phi: null, amplitudes: null,
          marginal: clone(marginal), run: clone(this.#problem.run),
        };
      }
      const vector = this.#history.at(-1).vector;
      return {
        mode: "explore", label: "Exploration · user-created pure state, NOT run evidence",
        initial: clone(this.#initial), operations: this.#history.slice(1).map((s) => s.label),
        marker: [...vector], ...pureReadout(vector),
      };
    }
  }

  function project(point, camera, width, height) {
    const [x, y, z] = point, c = Math.cos(camera.yaw), s = Math.sin(camera.yaw);
    const horizontal = c * x - s * y, back = s * x + c * y;
    const vertical = Math.cos(camera.pitch) * z - Math.sin(camera.pitch) * back;
    const depth = Math.sin(camera.pitch) * z + Math.cos(camera.pitch) * back;
    const radius = Math.min(width, height) * 0.32 * camera.zoom;
    return [width / 2 + horizontal * radius, height / 2 - vertical * radius, depth];
  }

  const api = {Lab, STATES, GATES, validateEvidence, rotate, fromAngles, pureReadout, project, clamp};
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.Bloch = api;
})(globalThis);
