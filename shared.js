// Shared helpers (no external dependencies)

export function getParam(name) {
  return new URLSearchParams(window.location.search).get(name);
}

export function pad2(n) {
  return String(n).padStart(2, "0");
}

// FNV-1a 32-bit (UTF-8), matches survey_new/build_bank.py
export function fnv1a32(str) {
  const data = new TextEncoder().encode(str);
  let hash = 0x811c9dc5;
  for (const b of data) {
    hash ^= b;
    hash = Math.imul(hash, 0x01000193) >>> 0;
  }
  return hash >>> 0;
}

// Deterministic PRNG (Mulberry32)
export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function shuffleInPlace(arr, rng) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

export async function loadJson(url) {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to load ${url}: ${res.status}`);
  }
  return await res.json();
}

export async function postJson(url, payload, mode = "cors") {
  const isNoCors = mode === "no-cors";
  const res = await fetch(url, {
    method: "POST",
    mode,
    // 在 no-cors 下不要发送 application/json（会触发 preflight / 被浏览器限制）
    headers: isNoCors ? undefined : { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  // When mode is "no-cors", response is opaque and unreadable. Treat as best-effort.
  if (mode === "no-cors") {
    return { ok: true, opaque: true };
  }

  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch (_) {
    data = { ok: res.ok, raw: text };
  }
  if (!res.ok) {
    throw new Error(`Submit failed: ${res.status} ${text}`);
  }
  return data;
}
