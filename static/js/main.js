/**
 * ============================================================
 * StoreHub — Premium JS Interactions
 * ============================================================
 * Pure Vanilla JS. No external libraries.
 * All animations respect prefers-reduced-motion.
 */

'use strict';

/* ── Reduced Motion Helper ─────────────────────────────────────────── */
const prefersReducedMotion = () =>
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ── CSRF Token Helper ─────────────────────────────────────────────── */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    for (const cookie of document.cookie.split(';')) {
      const c = cookie.trim();
      if (c.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(c.slice(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie('csrftoken');

/* ── DOMContentLoaded — Main Init ──────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initNavbarScroll();
  initHamburgerMenu();
  initScrollReveal();
  initButtonRipple();
  initTypewriter();
  initToastDismiss();
  initCartAjax();
  initScrollToTop();
  initImageFallbacks();
  initSkeletonImages();
  initFooterAccordion();
  initFilterToggle();
});

/* ── 1. Navbar Scroll-Aware Shadow ─────────────────────────────────── */
function initNavbarScroll() {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;

  const update = () =>
    navbar.classList.toggle('scrolled', window.scrollY > 50);

  window.addEventListener('scroll', update, { passive: true });
  update(); // run on load
}

/* ── 2. Hamburger Menu Toggle (Mobile) ─────────────────────────────── */
function initHamburgerMenu() {
  const hamburger = document.getElementById('hamburger-toggle');
  const navLinks  = document.getElementById('nav-links');
  if (!hamburger || !navLinks) return;

  hamburger.addEventListener('click', () => {
    const isOpen = navLinks.classList.toggle('active');
    hamburger.classList.toggle('active', isOpen);
    hamburger.setAttribute('aria-expanded', String(isOpen));
    // Prevent body scroll when menu is open
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });

  // Close on nav link click
  navLinks.querySelectorAll('a, button').forEach(el => {
    el.addEventListener('click', () => {
      navLinks.classList.remove('active');
      hamburger.classList.remove('active');
      hamburger.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    });
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
      navLinks.classList.remove('active');
      hamburger.classList.remove('active');
      hamburger.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }
  });
}

/* ── 3. Scroll Reveal (IntersectionObserver) ────────────────────────── */
function initScrollReveal() {
  const targets = document.querySelectorAll('.product-card, .fade-in');

  if (prefersReducedMotion()) {
    targets.forEach(el => el.classList.add('visible'));
    return;
  }

  if (!('IntersectionObserver' in window)) {
    targets.forEach(el => el.classList.add('visible'));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.classList.add('visible');
        }, index * 80);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

  targets.forEach(el => observer.observe(el));
}

/* ── 4. Button Ripple Effect ───────────────────────────────────────── */
function initButtonRipple() {
  if (prefersReducedMotion()) return;

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn');
    if (!btn) return;

    const ripple = document.createElement('span');
    ripple.classList.add('ripple');

    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    ripple.style.cssText = `
      width: ${size}px;
      height: ${size}px;
      left: ${e.clientX - rect.left - size / 2}px;
      top: ${e.clientY - rect.top - size / 2}px;
    `;

    btn.appendChild(ripple);
    ripple.addEventListener('animationend', () => ripple.remove());
  });
}

/* ── 5. Typewriter with Rotating Phrases ───────────────────────────── */
function initTypewriter() {
  const el     = document.getElementById('typewriter-text');
  const cursor = document.getElementById('typewriter-cursor');
  if (!el) return;

  const phrases = [
    el.dataset.text || el.textContent.trim(),
    'Shop smarter today.',
    'Unbeatable prices, always.',
    'Delivered to your doorstep.',
  ].filter(Boolean);

  el.textContent = '';
  if (cursor) cursor.style.display = 'inline';

  if (prefersReducedMotion()) {
    el.textContent = phrases[0];
    return;
  }

  let phraseIndex = 0;
  let charIndex   = 0;
  let deleting    = false;

  function tick() {
    const current = phrases[phraseIndex];

    if (!deleting) {
      el.textContent = current.slice(0, charIndex + 1);
      charIndex++;

      if (charIndex === current.length) {
        // Pause then start deleting
        setTimeout(() => { deleting = true; tick(); }, 2200);
        return;
      }
      setTimeout(tick, 60);
    } else {
      el.textContent = current.slice(0, charIndex - 1);
      charIndex--;

      if (charIndex === 0) {
        deleting    = false;
        phraseIndex = (phraseIndex + 1) % phrases.length;
        setTimeout(tick, 400);
        return;
      }
      setTimeout(tick, 30);
    }
  }

  setTimeout(tick, 600);
}

/* ── 6. Toast Notifications — Auto Dismiss ─────────────────────────── */
function initToastDismiss() {
  document.querySelectorAll('.toast').forEach((toast, index) => {
    if (!prefersReducedMotion()) {
      toast.style.animationDelay = `${index * 120}ms`;
    }

    const dismiss = () => {
      toast.classList.add('hide');
      toast.addEventListener('animationend', () => toast.remove(), { once: true });
    };

    setTimeout(dismiss, 4000 + index * 120);

    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) closeBtn.addEventListener('click', dismiss);
  });
}

/* ── 7. Utility: Show a Dynamic Toast ──────────────────────────────── */
function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('aside');
    container.className = 'toast-container';
    container.setAttribute('aria-live', 'polite');
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span>${message}</span>
    <button class="toast-close" aria-label="Close notification">&times;</button>
  `;
  container.appendChild(toast);

  const dismiss = () => {
    toast.classList.add('hide');
    toast.addEventListener('animationend', () => toast.remove(), { once: true });
  };

  setTimeout(dismiss, 4000);
  toast.querySelector('.toast-close').addEventListener('click', dismiss);
}

/* ── 8. Cart AJAX Quantity Updates ─────────────────────────────────── */
function initCartAjax() {
  const selects = document.querySelectorAll('.quantity-select');
  if (!selects.length) return;

  selects.forEach(select => {
    select.addEventListener('change', function () {
      const itemId      = this.dataset.itemId;
      const newQuantity = parseInt(this.value);
      const spinner     = document.getElementById(`spinner-${itemId}`);
      const row         = document.getElementById(`item-row-${itemId}`);

      if (spinner) spinner.style.display = 'inline';
      this.disabled = true;

      fetch(`/cart/update/${itemId}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
        body: JSON.stringify({ quantity: newQuantity }),
      })
        .then(r => r.json())
        .then(data => {
          if (spinner) spinner.style.display = 'none';
          this.disabled = false;

          if (data.success) {
            if (data.item_removed && row) {
              row.style.transition = 'opacity 0.3s ease';
              row.style.opacity = '0';
              setTimeout(() => row.remove(), 300);
            } else {
              const subtotalEl = document.getElementById(`subtotal-${itemId}`);
              if (subtotalEl) subtotalEl.textContent = data.item_subtotal;
            }

            const fields = {
              'cart-subtotal':   data.cart_subtotal,
              'cart-tax':        data.tax,
              'cart-shipping':   data.shipping,
              'cart-grand-total': data.grand_total,
            };
            for (const [id, value] of Object.entries(fields)) {
              const el = document.getElementById(id);
              if (el) el.textContent = value;
            }

            // Pulse cart badge
            const badge = document.getElementById('cart-badge');
            if (badge && data.cart_count !== undefined) {
              badge.textContent = data.cart_count;
              if (!prefersReducedMotion()) {
                badge.classList.add('badge-pulse');
                setTimeout(() => badge.classList.remove('badge-pulse'), 400);
              }
            }

            showToast('Cart updated!', 'success');
          } else {
            showToast(data.error || 'Failed to update.', 'error');
          }
        })
        .catch(() => {
          if (spinner) spinner.style.display = 'none';
          this.disabled = false;
          showToast('Network error. Please try again.', 'error');
        });
    });
  });
}

/* ── 9. Scroll-to-Top Button ───────────────────────────────────────── */
function initScrollToTop() {
  const btn = document.createElement('button');
  btn.id = 'scroll-to-top';
  btn.setAttribute('aria-label', 'Scroll to top');
  btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" stroke-width="2.5" stroke-linecap="round"
    stroke-linejoin="round" aria-hidden="true">
    <path d="M18 15l-6-6-6 6"/>
  </svg>`;
  document.body.appendChild(btn);

  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 300);
  }, { passive: true });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: prefersReducedMotion() ? 'instant' : 'smooth' });
  });
}

/* ── 10. Image Fallback (onerror) ──────────────────────────────────── */
function initImageFallbacks() {
  // This function is a safety net for any image without an inline onerror
  document.querySelectorAll('img[data-fallback]').forEach(img => {
    img.addEventListener('error', function () {
      if (this.src !== this.dataset.fallback) {
        this.src = this.dataset.fallback;
      }
    });
  });
}

/* ── 11. Skeleton → Real Image ─────────────────────────────────────── */
function initSkeletonImages() {
  document.querySelectorAll('.product-img-wrapper img').forEach(img => {
    const wrapper = img.closest('.product-img-wrapper');
    if (!wrapper) return;

    if (!img.complete || img.naturalWidth === 0) {
      wrapper.classList.add('skeleton');
      img.addEventListener('load', () => {
        wrapper.classList.remove('skeleton');
      }, { once: true });
      img.addEventListener('error', () => {
        wrapper.classList.remove('skeleton');
      }, { once: true });
    }
  });
}

/* ── 12. Footer Accordion (Mobile) ─────────────────────────────────── */
function initFooterAccordion() {
  const cols = document.querySelectorAll('.footer-col');

  cols.forEach(col => {
    const heading = col.querySelector('h4');
    const list    = col.querySelector('ul');
    if (!heading || !list) return;

    heading.addEventListener('click', () => {
      // Only activate on mobile
      if (window.innerWidth > 768) return;
      col.classList.toggle('open');
    });
  });
}

/* ── 13. Mobile Filter Sidebar Toggle ──────────────────────────────── */
function initFilterToggle() {
  const toggleBtn = document.getElementById('filter-toggle');
  const sidebar   = document.querySelector('.sidebar');
  if (!toggleBtn || !sidebar) return;

  toggleBtn.addEventListener('click', () => {
    const isOpen = sidebar.classList.toggle('open');
    toggleBtn.textContent = isOpen ? '✕ Close Filters' : '⚙ Filters';
    toggleBtn.setAttribute('aria-expanded', String(isOpen));
  });
}
