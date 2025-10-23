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

const escapeHtml = (value) => {
  if (value === undefined || value === null) {
    return '';
  }
  return String(value).replace(/[&<>'"]/g, (char) => {
    switch (char) {
      case '&':
        return '&amp;';
      case '<':
        return '&lt;';
      case '>':
        return '&gt;';
      case '"':
        return '&quot;';
      case "'":
        return '&#39;';
      default:
        return char;
    }
  });
};

const formatCurrency = (value) => {
  if (value === undefined || value === null || value === '') {
    return '';
  }
  const number = Number(value);
  if (Number.isNaN(number)) {
    return String(value);
  }
  return number.toLocaleString('id-ID');
};

const escapeSelector = (value) => {
  const stringValue = String(value ?? '');
  if (typeof window !== 'undefined' && window.CSS && typeof window.CSS.escape === 'function') {
    return window.CSS.escape(stringValue);
  }
  return stringValue.replace(/([\0-\x1f\x7f-\x9f!"#$%&'()*+,./:;<=>?@[\\\]^`{|}~])/g, '\\$1');
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

const extractVenueData = (button) => {
  if (!button) return null;
  const {
    venue: id,
    venueName: name,
    venueCity: city,
    venueCategory: category,
    venuePrice: price,
    venueUrl: url,
    venueImage: image,
    venueDescription: description,
  } = button.dataset;
  if (!id) {
    return null;
  }
  return {
    id,
    name: name || '',
    city: city || '',
    category: category || '',
    price: price || '',
    url: url || '',
    image: image || '',
    description: description || '',
  };
};

const createWishlistCard = (venueData) => {
  const card = document.createElement('article');
  card.className =
    'card-tilt group relative overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl shadow-slate-950/40 backdrop-blur-xl';
  card.setAttribute('data-animate', '');
  card.dataset.wishlistItem = String(venueData.id || '');

  const image = document.createElement('img');
  image.src = venueData.image || '';
  image.alt = venueData.name || '';
  image.className = 'h-48 w-full rounded-2xl object-cover';
  card.appendChild(image);

  const header = document.createElement('div');
  header.className = 'mt-4 flex items-start justify-between';
  card.appendChild(header);

  const meta = document.createElement('div');
  header.appendChild(meta);

  const category = document.createElement('p');
  category.className = 'text-xs uppercase tracking-[0.4em] text-white/50';
  category.textContent = venueData.category || '';
  meta.appendChild(category);

  const title = document.createElement('h3');
  title.className = 'text-xl font-semibold text-white';
  title.textContent = venueData.name || '';
  meta.appendChild(title);

  const city = document.createElement('p');
  city.className = 'text-sm text-white/60';
  city.textContent = venueData.city || '';
  meta.appendChild(city);

  const button = document.createElement('button');
  button.className =
    'wishlist-button wishlist-button--active rounded-full border border-white/20 bg-white/10 p-2 text-white transition hover:bg-white/20';
  button.setAttribute('aria-label', 'Unlove');
  button.setAttribute('aria-pressed', 'true');
  button.dataset.venue = String(venueData.id || '');
  button.dataset.wishlisted = 'true';
  button.dataset.venueName = venueData.name || '';
  button.dataset.venueCity = venueData.city || '';
  button.dataset.venueCategory = venueData.category || '';
  button.dataset.venuePrice = venueData.price || '';
  button.dataset.venueUrl = venueData.url || '';
  button.dataset.venueImage = venueData.image || '';
  button.dataset.venueDescription = venueData.description || '';
  header.appendChild(button);

  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('stroke-width', '1.5');
  svg.setAttribute('class', 'h-6 w-6');
  button.appendChild(svg);

  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  path.setAttribute('stroke-linecap', 'round');
  path.setAttribute('stroke-linejoin', 'round');
  path.setAttribute(
    'd',
    'M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z'
  );
  svg.appendChild(path);
  updateWishlistButton(button, true);

  const description = document.createElement('p');
  description.className = 'mt-2 text-sm text-white/70';
  description.textContent = venueData.description || '';
  card.appendChild(description);

  const footer = document.createElement('div');
  footer.className = 'mt-4 flex items-center justify-between';
  card.appendChild(footer);

  const priceTag = document.createElement('span');
  priceTag.className =
    'rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs uppercase tracking-widest text-white/70';
  const priceText = formatCurrency(venueData.price);
  const fallbackPrice = venueData.price ? String(venueData.price) : '';
  const combinedPrice = priceText || fallbackPrice;
  priceTag.textContent = combinedPrice ? `Rp ${combinedPrice}` : 'Rp';
  footer.appendChild(priceTag);

  const link = document.createElement('a');
  link.href = venueData.url || '#';
  link.className =
    'interactive-glow rounded-2xl bg-white/10 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/20';
  link.textContent = 'View product';
  link.setAttribute('data-ripple', '');
  footer.appendChild(link);

  return card;
};

const updateWishlistEmptyState = (grid, emptyState) => {
  if (!emptyState) {
    return;
  }
  const hasItems = Boolean(grid && grid.querySelector('[data-wishlist-item]'));
  if (hasItems) {
    emptyState.classList.add('hidden');
  } else {
    emptyState.classList.remove('hidden');
  }
};

const syncWishlistGrid = ({ venueId, wishlisted, venueData }) => {
  if (!venueId) {
    return;
  }
  const grid = document.querySelector('[data-wishlist-grid]');
  if (!grid) {
    return;
  }
  const emptyState = document.querySelector('[data-wishlist-empty]');
  const selector = `[data-wishlist-item="${escapeSelector(venueId)}"]`;
  const existingCard = grid.querySelector(selector);
  if (!wishlisted) {
    if (existingCard) {
      existingCard.remove();
    }
    updateWishlistEmptyState(grid, emptyState);
    return;
  }
  if (existingCard) {
    updateWishlistEmptyState(grid, emptyState);
    return;
  }
  if (!venueData) {
    updateWishlistEmptyState(grid, emptyState);
    return;
  }
  const card = createWishlistCard(venueData);
  grid.prepend(card);
  if (window.RagaSpace && typeof window.RagaSpace.refreshInteractive === 'function') {
    window.RagaSpace.refreshInteractive(grid);
  }
  updateWishlistEmptyState(grid, emptyState);
};

document.addEventListener('wishlist:changed', (event) => {
  if (!event.detail) {
    return;
  }
  syncWishlistGrid(event.detail);
});

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
    .then((response) => {
      if (response.redirected) {
        window.location.href = response.url;
        throw new Error('Authentication required');
      }
      if (!response.ok) {
        throw new Error(`Wishlist toggle failed with status ${response.status}`);
      }
      const contentType = response.headers.get('content-type') || '';
      if (!contentType.includes('application/json')) {
        throw new Error('Unexpected response format');
      }
      return response.json();
    })
    .then((data) => {
      const wishlisted = Boolean(data.wishlisted);
      updateWishlistButton(button, wishlisted);
      const venueData = extractVenueData(button);
      document.dispatchEvent(
        new CustomEvent('wishlist:changed', {
          detail: { venueId, wishlisted, venueData },
        })
      );
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
          const wishlistedClass = venue.wishlisted ? 'wishlist-button--active' : '';
          const heartFill = venue.wishlisted ? '#ef4444' : 'none';
          const heartStroke = venue.wishlisted ? '#ef4444' : 'currentColor';
          const wishlistedState = venue.wishlisted ? 'true' : 'false';
          const priceDisplay = formatCurrency(venue.price);
          card.innerHTML = `
            <div class="relative">
              <img src="${escapeHtml(venue.image_url)}" alt="${escapeHtml(venue.name)}" class="h-48 w-full rounded-2xl object-cover" />
              <button data-venue="${escapeHtml(venue.id)}" data-wishlisted="${wishlistedState}" data-venue-name="${escapeHtml(venue.name)}" data-venue-city="${escapeHtml(venue.city)}" data-venue-category="${escapeHtml(venue.category)}" data-venue-price="${escapeHtml(venue.price)}" data-venue-url="${escapeHtml(venue.url)}" data-venue-image="${escapeHtml(venue.image_url)}" data-venue-description="${escapeHtml(venue.description || '')}" class="wishlist-button ${wishlistedClass} absolute right-3 top-3 rounded-full border border-white/30 bg-white/10 p-2 text-white transition hover:bg-white/20" aria-label="Toggle wishlist" aria-pressed="${wishlistedState}">
                <svg xmlns="http://www.w3.org/2000/svg" fill="${heartFill}" viewBox="0 0 24 24" stroke-width="1.5" stroke="${heartStroke}" class="h-6 w-6">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
                </svg>
              </button>
            </div>
            <div class="mt-4 flex flex-col gap-2">
              <p class="text-xs uppercase tracking-[0.4em] text-white/50">${escapeHtml(venue.category)}</p>
              <h3 class="text-xl font-semibold text-white">${escapeHtml(venue.name)}</h3>
              <p class="text-sm text-white/60">${escapeHtml(venue.city)}</p>
            </div>
            <div class="mt-4 flex items-center justify-between">
              <span class="rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs uppercase tracking-widest text-white/70">Rp ${escapeHtml(priceDisplay)}</span>
              <a href="${escapeHtml(venue.url)}" class="interactive-glow rounded-2xl bg-white/10 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/20" data-ripple>View product</a>
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
