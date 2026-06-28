document.addEventListener('DOMContentLoaded', () => {
    // ========== MOBILE MENU ==========
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('nav-links');
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('open');
        });
    }

    // ========== NAV SHADOW ON SCROLL ==========
    const nav = document.getElementById('nav');
    if (nav) {
        window.addEventListener('scroll', () => {
            nav.style.boxShadow = window.scrollY > 10
                ? '0 2px 16px rgba(0,0,0,0.12)'
                : '0 1px 8px rgba(0,0,0,0.08)';
        });
    }

    // ========== CONTACT FORM (mailto) ==========
    const form = document.getElementById('contact-form');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const name = document.getElementById('contact-name').value.trim();
            const email = document.getElementById('contact-email').value.trim();
            const subject = document.getElementById('contact-subject').value;
            const message = document.getElementById('contact-message').value.trim();
            const msgEl = document.getElementById('contact-form-message');

            if (!name || !email || !message) {
                msgEl.className = 'form-message error';
                msgEl.textContent = '필수 항목을 모두 입력해주세요.';
                return;
            }
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                msgEl.className = 'form-message error';
                msgEl.textContent = '올바른 이메일 주소를 입력해주세요.';
                return;
            }

            const body = `이름: ${name}\n이메일: ${email}\n\n${message}`;
            const mailto = `mailto:jang1red@naver.com?subject=${encodeURIComponent('[블로그 문의] ' + subject)}&body=${encodeURIComponent(body)}`;
            window.location.href = mailto;

            msgEl.className = 'form-message success';
            msgEl.textContent = '메일 앱이 열립니다. 열리지 않으면 jang1red@naver.com 으로 보내주세요.';
        });
    }
});
