(function () {
  const LS_KEY = "reservedSeats"; // przechowujemy TWOJE zarezerwowane seatId
  const RETRIES_MS = [0, 150, 300, 600, 1000]; // kilka prób po wejściu / przebudowie

  function loadSet() {
    try { return new Set((JSON.parse(localStorage.getItem(LS_KEY) || "[]") || []).map(String)); }
    catch { return new Set(); }
  }
  function saveSet(s) {
    try { localStorage.setItem(LS_KEY, JSON.stringify(Array.from(s))); } catch {}
  }

  function addClassForSeat(seatId) {
    if (!seatId) return;
    const el = document.querySelector(`[data-seat-id="${CSS.escape(String(seatId))}"]`);
    if (!el) return;
    el.classList.add("seat-r"); // tylko klasa — nie dotykamy innerHTML
  }
  function removeClassForSeat(seatId) {
    if (!seatId) return;
    const el = document.querySelector(`[data-seat-id="${CSS.escape(String(seatId))}"]`);
    if (!el) return;
    el.classList.remove("seat-r");
  }

  function renderAllOnce() {
    const set = loadSet();
    set.forEach(id => addClassForSeat(id));
  }
  function scheduleRenderAll() {
    RETRIES_MS.forEach(ms => setTimeout(renderAllOnce, ms));
  }

  window.addEventListener("reservation:created", (e) => {
    const d = e.detail || {};
    const seat = d.seat_id || d.seat || d.place || d.seatId || d.id_seat;
    if (!seat) return;
    const set = loadSet(); set.add(String(seat)); saveSet(set);
    addClassForSeat(seat);
  });

  window.addEventListener("reservation:deleted", (e) => {
    const d = e.detail || {};
    const seat = d.seat_id || d.seat || d.place || d.seatId || d.id_seat;
    if (!seat) return;
    const set = loadSet(); set.delete(String(seat)); saveSet(set);
    removeClassForSeat(seat);
  });

  if (document.readyState === "complete") scheduleRenderAll();
  else window.addEventListener("load", scheduleRenderAll);
  window.addEventListener("pageshow", scheduleRenderAll);
})();
