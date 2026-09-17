/* The camera is only a projection; it never mutates the laboratory state. */
(function (root) {
  "use strict";

  function drawScene(canvas, snapshot, camera, ratio, B) {
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("Canvas 2D is unavailable; use the numerical readouts.");
    const bounds = canvas.getBoundingClientRect(), w = bounds.width, h = bounds.height;
    canvas.width = Math.round(w * ratio);
    canvas.height = Math.round(h * ratio);
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, w, h);
    const project = (v) => B.project(v, camera, w, h);
    const center = project([0, 0, 0]), radius = Math.min(w, h) * .32 * camera.zoom;
    const gradient = ctx.createRadialGradient(w * .43, h * .38, 0, w / 2, h / 2, radius);
    gradient.addColorStop(0, "#28444a");
    gradient.addColorStop(1, "#14262d");
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(center[0], center[1], radius, 0, 2 * Math.PI);
    ctx.fill();
    ctx.strokeStyle = "#75929b";
    ctx.lineWidth = 1;
    ctx.stroke();

    const segments = [];
    function ring(pointAt, equator = false) {
      for (let i = 0; i < 96; i++) {
        const a = project(pointAt(i * 2 * Math.PI / 96));
        const b = project(pointAt((i + 1) * 2 * Math.PI / 96));
        segments.push({a, b, depth: (a[2] + b[2]) / 2, equator});
      }
    }
    ring((t) => [Math.cos(t), Math.sin(t), 0], true);
    for (let i = 0; i < 6; i++) {
      const longitude = i * Math.PI / 6;
      ring((t) => [Math.sin(t) * Math.cos(longitude), Math.sin(t) * Math.sin(longitude), Math.cos(t)]);
    }
    function line(a, b, color, width = 1, dashed = false) {
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      ctx.setLineDash(dashed ? [3, 5] : []);
      ctx.beginPath();
      ctx.moveTo(a[0], a[1]);
      ctx.lineTo(b[0], b[1]);
      ctx.stroke();
      ctx.setLineDash([]);
    }
    segments.sort((a, b) => a.depth - b.depth).forEach(({a, b, depth, equator}) => {
      line(a, b, depth < 0 ? "#3b555e" : (equator ? "#b6cbd2" : "#6b8a94"),
        equator ? 1.4 : .8, depth < 0);
    });
    ctx.font = "14px system-ui";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    const axes = [
      {vector: [1, 0, 0], color: "#eda897", label: "X"},
      {vector: [0, 1, 0], color: "#acc5fc", label: "Y"},
      {vector: [0, 0, 1], color: "#d6dfc2", label: "Z"},
    ];
    for (const {vector, color, label} of axes) {
      line(project(vector.map((n) => -n * 1.12)), project(vector.map((n) => n * 1.12)), color);
      for (const sign of [-1, 1]) {
        const position = project(vector.map((n) => n * 1.24 * sign));
        ctx.fillStyle = color;
        const basis = label === "Z" ? (sign > 0 ? " / |0⟩" : " / |1⟩") : "";
        ctx.fillText(`${sign > 0 ? "+" : "−"}${label}${basis}`, position[0], position[1]);
      }
    }
    line([center[0] - 4, center[1]], [center[0] + 4, center[1]], "#b4c6cc");
    line([center[0], center[1] - 4], [center[0], center[1] + 4], "#b4c6cc");
    if (snapshot.marker !== null) {
      const tip = project(snapshot.marker);
      const color = snapshot.mode === "evidence" ? "#9ae0c0" : "#ffd18c";
      line(center, tip, color, 3, tip[2] < 0);
      const dx = tip[0] - center[0], dy = tip[1] - center[1], length = Math.hypot(dx, dy);
      if (length > 15) {
        const ux = dx / length, uy = dy / length;
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.moveTo(tip[0], tip[1]);
        ctx.lineTo(tip[0] - 13 * ux - 5 * uy, tip[1] - 13 * uy + 5 * ux);
        ctx.lineTo(tip[0] - 13 * ux + 5 * uy, tip[1] - 13 * uy - 5 * ux);
        ctx.closePath();
        ctx.fill();
      }
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(tip[0], tip[1], 6, 0, 2 * Math.PI);
      ctx.fill();
      ctx.strokeStyle = "#101d22";
      ctx.lineWidth = 2;
      ctx.stroke();
    }
    ctx.textAlign = "left";
    ctx.fillStyle = snapshot.mode === "evidence" ? "#9ae0c0" : "#ffd18c";
    ctx.font = "12px system-ui";
    ctx.fillText(snapshot.marker === null ? "UNAVAILABLE · no evidence marker" :
      snapshot.mode === "evidence" ? "DIAGONAL-STATE EVIDENCE VIEW" : "USER PURE STATE · NOT RUN EVIDENCE", 14, 22);
  }

  function mount(document, window, data, B) {
    const lab = new B.Lab(data);
    const $ = (id) => document.getElementById(id);
    const camera = {yaw: -.65, pitch: .38, zoom: 1};
    const canvas = $("sphere");
    const fmt = (number) => number === null ? "Unknown" : (Math.abs(number) < .000005 ? 0 : number).toFixed(5);
    const text = (id, value) => { $(id).textContent = value; };
    function option(value, label) {
      const element = document.createElement("option");
      element.value = value;
      element.textContent = label;
      return element;
    }
    $("problem").replaceChildren(...lab.problems.map((p) =>
      option(p.id, `${p.id.slice(0, 2)} · ${p.title}${p.archived ? " [archived]" : ""}`)));
    $("problem").value = lab.problem.id;

    function updateBits() {
      $("bit").replaceChildren(...lab.problem.marginals.map((m) =>
        option(String(m.bit), lab.problem.measurement_width === null ? "Unavailable" : `Returned bit ${m.bit}`)));
      $("bit").value = String(lab.bit);
      $("bit").disabled = lab.problem.measurement_width === null || lab.problem.measurement_width === 1;
    }

    function updateInputs() {
      const explore = lab.mode === "explore";
      $("explore-controls").querySelectorAll("button, input, select").forEach((el) => { el.disabled = !explore; });
      const customState = $("initial-state").value === "custom";
      const customAxis = $("rotation-axis").value === "custom";
      $("initial-angles").hidden = !customState;
      $("custom-axis").hidden = !customAxis;
      ["initial-theta", "initial-phi"].forEach((id) => { $(id).disabled = !explore || !customState; });
      ["axis-x", "axis-y", "axis-z"].forEach((id) => { $(id).disabled = !explore || !customAxis; });
      $("undo").disabled = !lab.canUndo;
    }

    function draw() {
      try {
        drawScene(canvas, lab.snapshot(), camera, Math.min(window.devicePixelRatio || 1, 2), B);
      } catch (error) {
        $("fatal").hidden = false;
        text("fatal", error.message);
      }
    }

    function render() {
      const view = lab.snapshot(), explore = view.mode === "explore";
      document.body.dataset.mode = view.mode;
      $("evidence-mode").setAttribute("aria-pressed", String(!explore));
      $("explore-mode").setAttribute("aria-pressed", String(explore));
      $("evidence-controls").hidden = explore;
      $("explore-controls").hidden = !explore;
      text("mode-note", explore
        ? "Exploration only. Independent user-created pure state; no transformations were observed in the selected run."
        : "Evidence only. Z = P(0) − P(1); X/Y and phase are unknown. Diagonal-state view, not tomography.");
      text("mode-badge", explore ? "EXPLORATION" : "EVIDENCE");
      text("scene-title", explore ? "Your pure-state laboratory" : "Measurement-derived Z polarization");
      text("scene-caption", explore
        ? `Independent initialization: ${view.initial.label}. State vector on the unit sphere.`
        : "Marker (0, 0, z): X/Y drawn as zero only by convention, not measured. Marker length is not original-state purity.");
      for (const axis of ["x", "y", "z"]) text(`read-${axis}`, view[axis] === null
        ? (axis === "z" ? "Unavailable" : "Unknown") : fmt(view[axis]));
      text("read-theta", explore ? `${fmt(view.theta)}°` : "Unknown");
      text("read-phi", explore ? (view.phi === null ? "Undefined (pole)" : `${fmt(view.phi)}°`) : "Unknown");
      text("angle-note", explore
        ? "θ from +Z; φ from +X toward +Y. At a pole φ is undefined. Amplitudes use a real nonnegative α; global phase omitted."
        : "State θ/φ cannot be recovered from Z counts alone. No amplitudes or phase are inferred.");
      $("amplitudes").hidden = !explore;
      text("amplitudes", explore
        ? `|ψ⟩ = α|0⟩ + β|1⟩; α = ${fmt(view.amplitudes.alpha[0])}; β = ${fmt(view.amplitudes.beta[0])} ${view.amplitudes.beta[1] < 0 ? "−" : "+"} ${fmt(Math.abs(view.amplitudes.beta[1]))}i`
        : "");
      if (explore) {
        text("explore-summary", `${view.initial.label}; ${view.operations.length} applied operations.`);
        $("history").replaceChildren(...(view.operations.length ? view.operations : ["No gates applied."]).map((label) => {
          const item = document.createElement("li");
          item.textContent = label;
          return item;
        }));
      } else {
        const {marginal: m, run} = view, problem = lab.problem;
        text("problem-meta", `${problem.archived ? "Archived" : "Active"} · Stage ${problem.stage}`);
        text("evidence-summary", m.status === "available"
          ? `Returned bit ${m.bit}: ${m.counts["0"]} zeros, ${m.counts["1"]} ones / ${m.shots} shots. z = ${fmt(m.z)}.`
          : `Unavailable: ${m.reason}. No marker is drawn.`);
        text("p0", m.p0 === null ? "Unavailable" : fmt(m.p0));
        text("p1", m.p1 === null ? "Unavailable" : fmt(m.p1));
        $("p0-bar").parentElement.hidden = m.status !== "available";
        $("p0-bar").style.width = m.p0 === null ? "0%" : `${100 * m.p0}%`;
        const provenance = [
          ["Target", run.target ?? "Unavailable"], ["Kernel", run.entry_point ?? "Unavailable"],
          ["Source snapshot time (not job time)", run.source_generated_utc ?? "Unavailable"],
          ["Source path", run.source?.path ?? "Unavailable"], ["Source SHA-256", run.source?.sha256 ?? "Unavailable"],
        ];
        $("provenance").replaceChildren(...provenance.flatMap(([label, value]) => {
          const dt = document.createElement("dt"), dd = document.createElement("dd");
          dt.textContent = label; dd.textContent = value;
          return [dt, dd];
        }));
        $("warnings").replaceChildren(...problem.warnings.map((warning) => {
          const li = document.createElement("li"); li.textContent = warning; return li;
        }));
      }
      updateInputs();
      draw();
    }

    function action(callback) {
      return (event) => {
        event.preventDefault();
        text("input-error", "");
        try { callback(event); render(); }
        catch (error) { text("input-error", error.message); }
      };
    }
    function numeric(id) {
      const raw = $(id).value.trim(), value = Number(raw);
      if (!raw || !Number.isFinite(value)) throw new Error("Enter a finite number in every required field.");
      return value;
    }
    $("problem").addEventListener("change", action(() => { lab.selectProblem($("problem").value); updateBits(); }));
    $("bit").addEventListener("change", action(() => lab.selectBit(Number($("bit").value))));
    $("evidence-mode").addEventListener("click", action(() => lab.setMode("evidence")));
    $("explore-mode").addEventListener("click", action(() => lab.setMode("explore")));
    $("initial-state").addEventListener("change", updateInputs);
    $("rotation-axis").addEventListener("change", updateInputs);
    $("initial-form").addEventListener("submit", action(() => {
      const state = $("initial-state").value;
      lab.start(state, state === "custom" ? numeric("initial-theta") : 0,
        state === "custom" ? numeric("initial-phi") : 0);
    }));
    document.querySelectorAll("[data-gate]").forEach((button) => {
      button.addEventListener("click", action(() => lab.gate(button.dataset.gate)));
    });
    $("rotation-form").addEventListener("submit", action(() => {
      const axis = $("rotation-axis").value;
      lab.rotation(axis === "custom" ? ["axis-x", "axis-y", "axis-z"].map(numeric) :
        {x: [1, 0, 0], y: [0, 1, 0], z: [0, 0, 1]}[axis], numeric("rotation-angle"));
    }));
    $("undo").addEventListener("click", action(() => lab.undo()));
    $("reset-state").addEventListener("click", action(() => lab.reset()));
    $("export").addEventListener("click", action(() => {
      const view = lab.snapshot();
      const payload = {format: "qgc-bloch-view-1.0", ...view};
      const blob = new window.Blob([JSON.stringify(payload, null, 2) + "\n"], {type: "application/json"});
      const url = window.URL.createObjectURL(blob), link = document.createElement("a");
      link.href = url;
      link.download = view.mode === "evidence" ? `evidence-${view.problem_id}-bit-${view.bit}.json` : "exploration-not-run-evidence.json";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(() => window.URL.revokeObjectURL(url), 1000);
    }));

    function cameraAction(name) {
      if (name === "left") camera.yaw -= .15;
      if (name === "right") camera.yaw += .15;
      if (name === "up") camera.pitch += .12;
      if (name === "down") camera.pitch -= .12;
      if (name === "in") camera.zoom *= 1.1;
      if (name === "out") camera.zoom /= 1.1;
      if (name === "reset") Object.assign(camera, {yaw: -.65, pitch: .38, zoom: 1});
      camera.pitch = B.clamp(camera.pitch, -1.4, 1.4);
      camera.zoom = B.clamp(camera.zoom, .55, 1.8);
      draw();
    }
    document.querySelectorAll("[data-camera]").forEach((button) => {
      button.addEventListener("click", () => cameraAction(button.dataset.camera));
    });
    canvas.addEventListener("keydown", (event) => {
      const name = {ArrowLeft: "left", ArrowRight: "right", ArrowUp: "up", ArrowDown: "down",
        "+": "in", "=": "in", "-": "out", Home: "reset"}[event.key];
      if (name) { event.preventDefault(); cameraAction(name); }
    });
    canvas.addEventListener("wheel", (event) => {
      event.preventDefault();
      camera.zoom *= Math.exp(-B.clamp(event.deltaY, -100, 100) * .003);
      cameraAction("");
    }, {passive: false});
    const pointers = new Map();
    const span = () => {
      const [a, b] = [...pointers.values()];
      return a && b ? Math.hypot(a.x - b.x, a.y - b.y) : 0;
    };
    canvas.addEventListener("pointerdown", (event) => {
      if (event.pointerType === "mouse" && event.button !== 0) return;
      canvas.focus({preventScroll: true});
      canvas.setPointerCapture(event.pointerId);
      pointers.set(event.pointerId, {x: event.clientX, y: event.clientY});
    });
    canvas.addEventListener("pointermove", (event) => {
      const previous = pointers.get(event.pointerId);
      if (!previous) return;
      const oldSpan = span();
      pointers.set(event.pointerId, {x: event.clientX, y: event.clientY});
      if (pointers.size === 1) {
        camera.yaw += (event.clientX - previous.x) * .007;
        camera.pitch += (event.clientY - previous.y) * .007;
      } else if (oldSpan > 0) {
        camera.zoom *= span() / oldSpan;
      }
      cameraAction("");
    });
    for (const name of ["pointerup", "pointercancel", "lostpointercapture"]) {
      canvas.addEventListener(name, (event) => pointers.delete(event.pointerId));
    }
    window.addEventListener("resize", draw);
    const observer = window.ResizeObserver ? new window.ResizeObserver(draw) : null;
    observer?.observe(canvas);
    updateBits();
    render();
    return {lab, camera, render};
  }

  if (typeof module === "object" && module.exports) module.exports = {mount, drawScene};
  else {
    try { mount(root.document, root, root.BLOCH_EVIDENCE, root.Bloch); }
    catch (error) {
      const fatal = root.document.getElementById("fatal");
      fatal.hidden = false;
      fatal.textContent = `Viewer could not load evidence: ${error.message}`;
      root.document.querySelectorAll("button, select, input").forEach((el) => { el.disabled = true; });
    }
  }
})(globalThis);
