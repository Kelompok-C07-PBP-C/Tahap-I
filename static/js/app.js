function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

const csrfToken = getCookie('csrftoken');

function toggleWishlist(button) {
  const venueId = button.dataset.venue;
  fetch(`/api/wishlist/${venueId}/toggle/`, {
    method: 'POST',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/json',
      ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
    },
    body: JSON.stringify({}),
  })
    .then((response) => response.json())
    .then((data) => {
      const svg = button.querySelector('svg');
      if (!svg) return;
      if (data.wishlisted) {
        svg.setAttribute('fill', 'currentColor');
      } else {
        svg.setAttribute('fill', 'none');
      }
    })
    .catch((error) => console.error('Wishlist toggle failed', error));
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
          card.className = 'group relative overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl shadow-slate-950/40 backdrop-blur-xl transition hover:-translate-y-1 hover:bg-white/10';
          card.innerHTML = `
            <div class="relative">
              <img src="${venue.image_url}" alt="${venue.name}" class="h-48 w-full rounded-2xl object-cover" />
              <button data-venue="${venue.id}" class="wishlist-button absolute right-3 top-3 rounded-full border border-white/30 bg-white/10 p-2 text-white transition hover:bg-white/20" aria-label="Toggle wishlist">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-6 w-6">
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
              <a href="${venue.url}" class="rounded-2xl bg-white/10 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/20">View product</a>
            </div>
          `;
          grid.appendChild(card);
        });
      })
      .catch((error) => console.error('Filter failed', error));
  });
}
