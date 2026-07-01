// Firebase Firestore 기반 댓글 (무료·광고 없음, 로그인 불필요) + 페이지네이션
import { firebaseConfig } from "./firebase-config.js";

const PAGE_SIZE = 3;
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
  const pagEl = document.getElementById("comment-pagination");
  const countEl = document.getElementById("c-count");
  const form = document.getElementById("comment-form");
  const msg = document.getElementById("c-msg");
  root.hidden = false;

  let all = [];
  let page = 0;

  const esc = (s) => { const d = document.createElement("div"); d.textContent = s; return d.innerHTML; };
  const fmt = (ts) => {
    if (!ts) return "";
    const d = ts.toDate ? ts.toDate() : new Date(ts);
    return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")}`;
  };

  function renderPage() {
    const pages = Math.ceil(all.length / PAGE_SIZE);
    if (page >= pages) page = Math.max(0, pages - 1);
    const slice = all.slice(page * PAGE_SIZE, page * PAGE_SIZE + PAGE_SIZE);
    listEl.innerHTML = slice.length
      ? slice.map((c) => `<div class="comment"><div class="comment-head"><span class="comment-name">${esc(c.name)}</span><span class="comment-date">${fmt(c.createdAt)}</span></div><p class="comment-text">${esc(c.text)}</p></div>`).join("")
      : '<p class="c-empty">첫 댓글을 남겨보세요.</p>';
    renderPagination(pages);
  }

  function renderPagination(pages) {
    if (pages <= 1) { pagEl.innerHTML = ""; return; }
    let h = `<button class="pg-btn pg-arrow" data-pg="${page - 1}"${page === 0 ? " disabled" : ""} aria-label="이전">&lsaquo;</button>`;
    for (let i = 0; i < pages; i++) {
      h += `<button class="pg-btn pg-num${i === page ? " active" : ""}" data-pg="${i}">${i + 1}</button>`;
    }
    h += `<button class="pg-btn pg-arrow" data-pg="${page + 1}"${page === pages - 1 ? " disabled" : ""} aria-label="다음">&rsaquo;</button>`;
    pagEl.innerHTML = h;
    pagEl.querySelectorAll(".pg-btn").forEach((b) => b.addEventListener("click", () => {
      const p = parseInt(b.dataset.pg, 10);
      if (p >= 0 && p < pages && p !== page) {
        page = p;
        renderPage();
        root.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }));
  }

  async function load() {
    listEl.innerHTML = '<p class="c-empty">댓글을 불러오는 중…</p>';
    pagEl.innerHTML = "";
    try {
      const snap = await getDocs(query(collection(db, "comments"), where("postId", "==", postId)));
      all = snap.docs
        .map((d) => d.data())
        .sort((a, b) => (b.createdAt?.seconds || 0) - (a.createdAt?.seconds || 0));
      countEl.textContent = all.length ? `(${all.length})` : "";
      page = 0;
      renderPage();
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
      document.getElementById("c-name").value = "";
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
