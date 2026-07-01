// Firebase Firestore 기반 댓글 (무료·광고 없음, 로그인 불필요)
import { firebaseConfig } from "./firebase-config.js";

const root = document.getElementById("comments");

if (root && firebaseConfig && firebaseConfig.projectId) {
  init().catch((e) => console.error("[comments]", e));
}

async function init() {
  const { initializeApp } = await import("https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js");
  const { getFirestore, collection, addDoc, query, where, getDocs, serverTimestamp } =
    await import("https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js");

  const db = getFirestore(initializeApp(firebaseConfig));
  const postId = root.dataset.postId;
  const listEl = document.getElementById("comment-list");
  const countEl = document.getElementById("c-count");
  const form = document.getElementById("comment-form");
  const msg = document.getElementById("c-msg");
  root.hidden = false;

  const esc = (s) => { const d = document.createElement("div"); d.textContent = s; return d.innerHTML; };
  const fmt = (ts) => {
    if (!ts) return "";
    const d = ts.toDate ? ts.toDate() : new Date(ts);
    return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")}`;
  };

  async function load() {
    listEl.innerHTML = '<p class="c-empty">댓글을 불러오는 중…</p>';
    try {
      const snap = await getDocs(query(collection(db, "comments"), where("postId", "==", postId)));
      const items = snap.docs
        .map((d) => d.data())
        .sort((a, b) => (b.createdAt?.seconds || 0) - (a.createdAt?.seconds || 0));
      countEl.textContent = items.length ? `(${items.length})` : "";
      listEl.innerHTML = items.length
        ? items.map((c) => `<div class="comment"><div class="comment-head"><span class="comment-name">${esc(c.name)}</span><span class="comment-date">${fmt(c.createdAt)}</span></div><p class="comment-text">${esc(c.text)}</p></div>`).join("")
        : '<p class="c-empty">첫 댓글을 남겨보세요.</p>';
    } catch (e) {
      listEl.innerHTML = '<p class="c-empty">댓글을 불러오지 못했습니다.</p>';
      console.error("[comments]", e);
    }
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("c-name").value.trim();
    const text = document.getElementById("c-text").value.trim();
    if (!name || !text) { msg.textContent = "이름과 댓글을 모두 입력해주세요."; msg.className = "c-msg err"; return; }
    const btn = form.querySelector(".c-submit");
    btn.disabled = true; btn.textContent = "등록 중…";
    try {
      await addDoc(collection(db, "comments"), { postId, name, text, createdAt: serverTimestamp() });
      document.getElementById("c-text").value = "";
      msg.textContent = "댓글이 등록되었습니다."; msg.className = "c-msg ok";
      await load();
    } catch (err) {
      msg.textContent = "등록에 실패했습니다. 잠시 후 다시 시도해주세요."; msg.className = "c-msg err";
      console.error("[comments]", err);
    }
    btn.disabled = false; btn.textContent = "댓글 남기기";
  });

  load();
}
