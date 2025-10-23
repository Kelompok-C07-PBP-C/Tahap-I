function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

const getCsrfToken = () => {
  const cookieToken = getCookie('csrftoken');
  if (cookieToken) {
    return cookieToken;
  }
  const metaToken = document.querySelector('meta[name="csrf-token"]');
  if (metaToken) {
    return metaToken.getAttribute('content');
  }
  return '';
};

const updateWishlistButton = (button, wishlisted) => {
  if (!button) return;
  const svg = button.querySelector('svg');
  const path = svg ? svg.querySelector('path') : null;
  if (svg) {
    svg.setAttribute('fill', wishlisted ? '#ef4444' : 'none');
    svg.setAttribute('stroke', wishlisted ? '#ef4444' : 'currentColor');
  }
  if (path) {
    path.setAttribute('fill', wishlisted ? '#ef4444' : 'none');
    path.setAttribute('stroke', wishlisted ? '#ef4444' : 'currentColor');
  }
  button.classList.toggle('wishlist-button--active', Boolean(wishlisted));
  button.setAttribute('aria-pressed', wishlisted ? 'true' : 'false');
  button.dataset.wishlisted = wishlisted ? 'true' : 'false';
};

function toggleWishlist(button) {
  const venueId = button.dataset.venue;
  if (!venueId || button.dataset.loading === 'true') {
    return;
  }

  const previousState = button.getAttribute('aria-pressed') === 'true';
  const desiredState = !previousState;
  const csrfToken = getCsrfToken();

  button.dataset.loading = 'true';
  updateWishlistButton(button, desiredState);

  fetch(`/api/wishlist/${venueId}/toggle/`, {
    method: 'POST',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
    },
    credentials: 'same-origin',
    body: JSON.stringify({}),
  })
    .then((response) => response.json())
    .then((data) => {
      const svg = button.querySelector('svg');
      if (!svg) return;
      if (data.wishlisted) {
        svg.setAttribute('fill', '#ef4444');
        svg.setAttribute('stroke', '#ef4444');
      } else {
        svg.setAttribute('fill', 'none');
        svg.setAttribute('stroke', 'currentColor');
      }
      button.setAttribute('aria-pressed', data.wishlisted ? 'true' : 'false');
    })
    .then((data) => {
      updateWishlistButton(button, Boolean(data.wishlisted));
    })
    .catch((error) => {
      updateWishlistButton(button, previousState);
      console.error('Wishlist toggle failed', error);
    })
    .finally(() => {
      delete button.dataset.loading;
    });
}

document.addEventListener('click', (event) => {
  const button = event.target.closest('.wishlist-button');
  if (button) {
    event.preventDefault();
    toggleWishlist(button);
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const navToggle = document.querySelector('[data-nav-toggle]');
  const navMenu = document.querySelector('#primary-nav-menu');
  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      const expanded = navToggle.getAttribute('aria-expanded') === 'true';
      navToggle.setAttribute('aria-expanded', (!expanded).toString());
      navMenu.classList.toggle('hidden');
    });
  }

  const modalStack = [];

  const openModal = (modal) => {
    if (!modal) return;
    modal.classList.remove('hidden');
    modal.setAttribute('aria-hidden', 'false');
    if (!modalStack.includes(modal)) {
      modalStack.push(modal);
    }
    document.body.classList.add('overflow-hidden');
    const focusTargetId = modal.dataset.modalInitialFocus;
    let focusTarget = focusTargetId ? modal.querySelector(`#${focusTargetId}`) : null;
    if (!focusTarget) {
      focusTarget = modal.querySelector('[data-autofocus], input, select, textarea, button, a[href]');
    }
    if (focusTarget && typeof focusTarget.focus === 'function') {
      focusTarget.focus();
    }
  };

  const closeModal = (modal) => {
    if (!modal) return;
    modal.classList.add('hidden');
    modal.setAttribute('aria-hidden', 'true');
    const index = modalStack.indexOf(modal);
    if (index >= 0) {
      modalStack.splice(index, 1);
    }
    if (modalStack.length === 0) {
      document.body.classList.remove('overflow-hidden');
    }
  };

  document.addEventListener('click', (event) => {
    const trigger = event.target.closest('[data-modal-target]');
    if (trigger) {
      const modalId = trigger.getAttribute('data-modal-target');
      const modal = document.getElementById(modalId);
      if (modal) {
        event.preventDefault();
        openModal(modal);
        return;
      }
    }

    const dismiss = event.target.closest('[data-modal-close]');
    if (dismiss) {
      event.preventDefault();
      const modal = dismiss.closest('[data-modal]');
      closeModal(modal);
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && modalStack.length > 0) {
      event.preventDefault();
      const modal = modalStack[modalStack.length - 1];
      closeModal(modal);
    }
  });

  document.querySelectorAll('[data-modal]').forEach((modal) => {
    if (!modal.hasAttribute('aria-hidden')) {
      modal.setAttribute('aria-hidden', modal.classList.contains('hidden') ? 'true' : 'false');
    }
    const defaultOpen = modal.getAttribute('data-modal-default-open');
    if (defaultOpen && defaultOpen !== 'false') {
      openModal(modal);
    }
  });

  const animatedElements = document.querySelectorAll('[data-animate]');
  const animatedObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          animatedObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.2 }
  );

  const observeAnimated = (element) => {
    if (!element || element.dataset.animateObserved === 'true') {
      return;
    }
    animatedObserver.observe(element);
    element.dataset.animateObserved = 'true';
  };

  animatedElements.forEach((element) => observeAnimated(element));

  const attachRipple = (element) => {
    if (!element || element.dataset.rippleBound === 'true') {
      return;
    }
    element.dataset.rippleBound = 'true';
    if (!element.classList.contains('relative')) {
      element.classList.add('relative');
    }
    element.addEventListener('click', (event) => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey) {
        return;
      }
      if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
      }
      const rect = element.getBoundingClientRect();
      const ripple = document.createElement('span');
      ripple.className = 'ripple';
      ripple.style.left = `${event.clientX - rect.left}px`;
      ripple.style.top = `${event.clientY - rect.top}px`;
      element.appendChild(ripple);
      window.setTimeout(() => {
        ripple.remove();
      }, 750);
    });
  };

  document.querySelectorAll('.interactive-glow, [data-ripple]').forEach((element) => attachRipple(element));

  const transitionOverlay = document.getElementById('page-transition');

  const hideTransition = () => {
    if (!transitionOverlay) return;
    transitionOverlay.classList.remove('opacity-100', 'pointer-events-auto');
    transitionOverlay.classList.add('opacity-0', 'pointer-events-none');
    window.setTimeout(() => {
      transitionOverlay.classList.add('invisible');
    }, 400);
  };

  const showTransition = () => {
    if (!transitionOverlay) return;
    transitionOverlay.classList.remove('pointer-events-none', 'opacity-0', 'invisible');
    transitionOverlay.classList.add('opacity-100', 'pointer-events-auto');
  };

  hideTransition();
  window.addEventListener('pageshow', () => hideTransition());

  document.addEventListener('click', (event) => {
    if (event.defaultPrevented) {
      return;
    }
    const anchor = event.target.closest('a[href]');
    if (!anchor) {
      return;
    }
    if (anchor.dataset.modalTarget || anchor.hasAttribute('data-modal-target')) {
      return;
    }
    const href = anchor.getAttribute('href');
    if (!href || href.startsWith('#')) {
      return;
    }
    if (anchor.target && anchor.target !== '_self') {
      return;
    }
    if (anchor.host && anchor.host !== window.location.host) {
      return;
    }
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
      return;
    }
    showTransition();
    event.preventDefault();
    window.setTimeout(() => {
      window.location.href = anchor.href;
    }, 220);
  });

  const refreshInteractive = (root = document) => {
    const scope = root instanceof Element ? root : document;
    scope.querySelectorAll('[data-animate]').forEach((element) => observeAnimated(element));
    scope.querySelectorAll('.interactive-glow, [data-ripple]').forEach((element) => attachRipple(element));
  };

  window.RagaSpace = window.RagaSpace || {};
  window.RagaSpace.refreshInteractive = refreshInteractive;
});

const filterForm = document.querySelector('#catalog-filter-form');
if (filterForm) {
  filterForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const params = new URLSearchParams(new FormData(filterForm));
    fetch(`/api/catalog/filter/?${params.toString()}`, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
    })
      .then((response) => response.json())
      .then((data) => {
        const grid = document.querySelector('#catalog-grid');
        if (!grid) return;
        grid.innerHTML = '';
        if (data.venues.length === 0) {
          grid.innerHTML = '<p class="text-white/70">No venues match your filters yet.</p>';
          return;
        }
        data.venues.forEach((venue) => {
          const card = document.createElement('article');
          card.className = 'card-tilt group relative overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl shadow-slate-950/40 backdrop-blur-xl transition hover:bg-white/10';
          card.setAttribute('data-animate', '');
          card.innerHTML = `
            <div class="relative">
              <img src="${venue.image_url}" alt="${venue.name}" class="h-48 w-full rounded-2xl object-cover" />
              <button data-venue="${venue.id}" class="wishlist-button interactive-glow absolute right-3 top-3 rounded-full border border-white/30 bg-white/10 p-2 text-white transition hover:bg-white/20" data-ripple aria-label="Toggle wishlist" aria-pressed="${venue.wishlisted ? 'true' : 'false'}">
                <svg xmlns="http://www.w3.org/2000/svg" fill="${venue.wishlisted ? '#ef4444' : 'none'}" viewBox="0 0 24 24" stroke-width="1.5" stroke="${venue.wishlisted ? '#ef4444' : 'currentColor'}" class="h-6 w-6">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
                </svg>
              </button>
            </div>
            <div class="mt-4 flex flex-col gap-2">
              <p class="text-xs uppercase tracking-[0.4em] text-white/50">${venue.category}</p>
              <h3 class="text-xl font-semibold text-white">${venue.name}</h3>
              <p class="text-sm text-white/60">${venue.city}</p>
            </div>
            <div class="mt-4 flex items-center justify-between">
              <span class="rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs uppercase tracking-widest text-white/70">Rp ${venue.price}</span>
              <a href="${venue.url}" class="interactive-glow rounded-2xl bg-white/10 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/20" data-ripple>View product</a>
            </div>
          `;
          grid.appendChild(card);
        });
        if (window.RagaSpace && typeof window.RagaSpace.refreshInteractive === 'function') {
          window.RagaSpace.refreshInteractive(grid);
        }
      })
      .catch((error) => console.error('Filter failed', error));
  });
}
