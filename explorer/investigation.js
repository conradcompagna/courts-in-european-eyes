(() => {
  const D = window.LAB_DATA, passages = D.passages, explorer = window.courtExplorer;
  const body = document.getElementById("taskBody");
  const byId = new Map(passages.map((p) => [p.id, p]));
  const sources = Object.fromEntries(D.sources.map((s) => [s.unit, s]));
  const storageKey = "courts-neighbor-reading-v1";
  const publicSite = location.hostname === "conradcompagna.github.io";
  const publicHint = "Saving and submitting are unavailable on the public site. Writing stays in this browser.";
  let work = { previewAnchor: "", workByAnchor: {}, studentId: "" };
  try {
    const old = JSON.parse(localStorage.getItem(storageKey) || "{}");
    work = { previewAnchor: old.previewAnchor || old.savedAnchor || "", workByAnchor: old.workByAnchor || {}, studentId: old.studentId || "" };
  } catch (_) {}
  if (!work.workByAnchor || typeof work.workByAnchor !== "object") work.workByAnchor = {};
  if (!byId.has(work.previewAnchor)) work.previewAnchor = "";
  const save = () => { try { localStorage.setItem(storageKey, JSON.stringify(work)); } catch (_) {} };
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const words = (s) => (String(s || "").trim().match(/\S+/g) || []).length;
  const source = (p) => sources[p.u];
  const details = (p) => `${source(p).author} · ${p.c} · p. ${p.p}`;
  const neighbours = (p) => p.nn.slice(0, 5).map(([index, score]) => ({ passage: passages[index], score }));
  const clusterName = (p) => window.COURT_CLUSTER_NAMES?.[p.k] || `Cluster ${p.k}`;
  function current() {
    if (!work.previewAnchor) return null;
    const entry = work.workByAnchor[work.previewAnchor] ||= { notes: {}, essay: "" };
    if (!entry.notes || typeof entry.notes !== "object") entry.notes = {};
    return entry;
  }
  function ready() {
    if (!work.previewAnchor) return false;
    const entry = current(), p = byId.get(work.previewAnchor);
    return [p, ...neighbours(p).map(({ passage }) => passage)].every((passage) => words(entry.notes[passage.id]) >= 100) &&
      words(entry.essay) >= 500;
  }
  function render() {
    const p = byId.get(work.previewAnchor), entry = current();
    if (!p) {
      body.innerHTML = `<h2>Read a passage and its neighbours</h2><p class="note empty-state">Click a dot in the map.</p>`;
      return;
    }
    const reading = [{ passage: p, score: null }, ...neighbours(p)];
    body.innerHTML = `<h2>${esc(p.id)} and its five nearest passages</h2>
      <p class="task-copy">Summarize each passage in at least 100 words, then write a 500-word interpretation of their similarity.</p>
      <div class="reading-list">${reading.map(({ passage: q, score }, i) => {
        const note = entry.notes[q.id] || "", s = source(q);
        const tcp = `https://github.com/textcreationpartnership/${s.tcp}/blob/master/${s.tcp}.xml`;
        return `<article class="reading-card">
          <p class="eyebrow">${i === 0 ? "Selected passage" : `Neighbour ${i} · cosine ${score.toFixed(3)}`} · ${esc(clusterName(q))}</p>
          <h3>${esc(details(q))}</h3>
          <p class="note">${esc(q.id)} · ${esc(s.vehicle)} · <a href="${tcp}" target="_blank" rel="noopener">Source</a></p>
          <p class="source-text">${esc(q.t)}</p>
          <label class="task-field">What is the main thing this passage describes? Summarize it in your own words and identify one specific detail.
            <textarea data-note="${esc(q.id)}" placeholder="At least 100 words…">${esc(note)}</textarea>
          </label>
          <p class="word-count" data-count="${esc(q.id)}">${words(note)} / 100 words</p>
        </article>`;
      }).join("")}</div>
      <section class="synthesis">
        <h3>Interpret the similarity</h3>
        <p class="task-copy">Use your six summaries to identify the pattern connecting these passages. Why might their embeddings be similar? Does the resemblance point to a recurring practice in the societies described, to shared features of the European accounts (word choice, narrative style, or translation), or to both? Support your answer with evidence from the passages.</p>
        <label class="task-field">Synthesis<textarea id="essay" placeholder="At least 500 words…">${esc(entry.essay)}</textarea></label>
        <p class="word-count" id="essayCount">${words(entry.essay)} / 500 words</p>
        ${publicSite ? `<div class="task-row">
          <span class="disabled-action" tabindex="0" title="${esc(publicHint)}"><button class="action" id="saveDraft" disabled>Save draft</button></span>
          <span class="disabled-action" tabindex="0" title="${esc(publicHint)}"><button class="action primary" id="upload" disabled>Upload completed assignment</button></span>
        </div>` : `<label class="task-field">Student name or ID<input id="studentId" type="text" maxlength="80" autocomplete="name" value="${esc(work.studentId)}" required></label>
        <div class="task-row">
          <button class="action" id="saveDraft">Save draft</button>
          <button class="action primary" id="upload" ${ready() ? "" : "disabled"}>Upload completed assignment</button>
        </div>
        <p class="note" id="activityStatus" role="status" aria-live="polite"></p>`}
      </section>`;
  }
  function submission(kind) {
    const p = byId.get(work.previewAnchor), entry = current();
    if (!p || !entry) return null;
    const passageIds = [p.id, ...neighbours(p).map(({ passage }) => passage.id)];
    return { kind, studentId: work.studentId.trim(), anchorId: p.id, passageIds,
      notes: Object.fromEntries(passageIds.map((id) => [id, entry.notes[id] || ""])), essay: entry.essay };
  }
  const status = (message) => { const el = body.querySelector("#activityStatus"); if (el) el.textContent = message; };
  async function sendSubmission(kind) {
    if (publicSite) return;
    save();
    const payload = submission(kind);
    if (!payload) return;
    if (!payload.studentId) { status("Enter your name or ID before saving."); body.querySelector("#studentId")?.focus?.(); return; }
    if (kind === "completed" && !ready()) return;
    if (location.protocol === "file:") {
      status("Open this explorer through the classroom server to save to the project folder.");
      return;
    }
    const button = body.querySelector(kind === "draft" ? "#saveDraft" : "#upload");
    if (button) button.disabled = true;
    status(kind === "draft" ? "Saving draft…" : "Uploading assignment…");
    try {
      const response = await fetch("/api/submissions", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Server rejected the submission.");
      if (work.previewAnchor === payload.anchorId) {
        status(kind === "draft" ? "Draft saved in the project submissions folder." : "Completed assignment uploaded to the project submissions folder.");
      }
    } catch (error) {
      if (work.previewAnchor === payload.anchorId) status(`Could not save: ${error.message || "server unavailable"}`);
    } finally {
      if (button) button.disabled = kind === "completed" ? !ready() : false;
    }
  }
  body.addEventListener("click", (e) => {
    const b = e.target.closest("button"); if (!b) return;
    if (b.id === "saveDraft") void sendSubmission("draft");
    else if (b.id === "upload" && ready()) void sendSubmission("completed");
  });
  body.addEventListener("input", (e) => {
    const entry = current(); if (!entry) return;
    if (e.target.dataset.note) {
      const id = e.target.dataset.note;
      entry.notes[id] = e.target.value;
      const counter = body.querySelector(`[data-count="${id}"]`);
      if (counter) counter.textContent = `${words(e.target.value)} / 100 words`;
    } else if (e.target.id === "essay") {
      entry.essay = e.target.value;
      body.querySelector("#essayCount").textContent = `${words(e.target.value)} / 500 words`;
    } else if (e.target.id === "studentId") {
      work.studentId = e.target.value;
    }
    save();
    const button = body.querySelector("#upload");
    if (button) button.disabled = !ready();
  });
  window.courtInvestigation = {
    markedIds: () => {
      const p = byId.get(work.previewAnchor);
      return p ? [p.id, ...neighbours(p).map(({ passage }) => passage.id)] : [];
    },
    preview(id) {
      if (!byId.has(id)) return;
      work.previewAnchor = id; save(); render(); explorer.refresh();
    },
    clear() {
      work.previewAnchor = "";
      save(); render(); explorer.refresh();
    },
  };
  render();
  if (work.previewAnchor) explorer.selectId(work.previewAnchor);
  else explorer.refresh();
})();
