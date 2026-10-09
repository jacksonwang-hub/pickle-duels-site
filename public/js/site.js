/* Pickle Duels — progressive enhancement.
   Everything here is additive: the site is fully usable with JS disabled. */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Run each feature in isolation. A thrown error in one block must never
     stop a later one -- the reveal code in particular, because failing to
     run it would leave .reveal sections invisible at opacity 0. */
  var guard = function (name, fn) {
    try {
      fn();
    } catch (error) {
      if (window.console && console.error) console.error('[pickle-duels] ' + name, error);
    }
  };

  /* Failsafe: whatever else happens, never leave content hidden. */
  window.setTimeout(function () {
    var hidden = document.querySelectorAll('.reveal:not(.is-visible)');
    Array.prototype.forEach.call(hidden, function (el) { el.classList.add('is-visible'); });
  }, 2500);

  /* --- Mobile navigation -------------------------------------------------- */
  guard('nav', function () {
  var toggle = document.querySelector('.nav-toggle');
  var panel = document.getElementById('mobile-nav');

  if (toggle && panel) {
    var setOpen = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      panel.hidden = !open;
      document.body.style.overflow = open ? 'hidden' : '';

      if (open) {
        var first = panel.querySelector('a, button');
        if (first) first.focus();
      } else if (toggle.offsetParent !== null) {
        // Return focus to the control that opened the menu, as the disclosure
        // pattern requires -- but not when a resize to desktop closed it,
        // because the toggle is display:none there.
        toggle.focus();
      }
    };

    toggle.addEventListener('click', function () {
      setOpen(toggle.getAttribute('aria-expanded') !== 'true');
    });

    document.addEventListener('keydown', function (event) {
      if (panel.hidden) return;

      if (event.key === 'Escape') {
        setOpen(false);
        return;
      }

      // Keep tab focus inside the open panel.
      if (event.key !== 'Tab') return;
      var focusables = panel.querySelectorAll('a[href], button:not([disabled])');
      if (!focusables.length) return;
      var first = focusables[0];
      var last = focusables[focusables.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });

    // A resize past the desktop breakpoint leaves the panel orphaned otherwise.
    window.addEventListener('resize', function () {
      if (window.innerWidth >= 960 && !panel.hidden) setOpen(false);
    });
  }
  });

  /* --- Scroll reveal ------------------------------------------------------ */
  guard('reveal', function () {
  var targets = document.querySelectorAll('.reveal');

  if (reduced || !('IntersectionObserver' in window)) {
    Array.prototype.forEach.call(targets, function (el) { el.classList.add('is-visible'); });
  } else {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

    Array.prototype.forEach.call(targets, function (el) { observer.observe(el); });
  }
  });

  /* --- Demo request form -------------------------------------------------- */
  guard('form', function () {
  var form = document.querySelector('form[data-enhanced]');
  if (!form) return;

  var success = document.getElementById('form-success');
  var submit = form.querySelector('button[type="submit"]');

  // Suppress native validation bubbles so our own inline, screen-reader
  // announced messages run instead. Set from JS, not markup, so a visitor
  // without JS still gets the browser's built-in required-field checks.
  form.setAttribute('novalidate', 'novalidate');

  var messageFor = function (field) {
    if (field.validity.valueMissing) {
      return field.tagName === 'SELECT' ? 'Please choose an option.' : 'This field is required.';
    }
    if (field.validity.typeMismatch && field.type === 'email') {
      return 'Please enter a valid email address.';
    }
    return field.validationMessage;
  };

  var showError = function (field, message) {
    var slot = document.getElementById(field.id + '-error');
    if (slot) slot.textContent = message || '';
    if (message) {
      field.setAttribute('aria-invalid', 'true');
    } else {
      field.removeAttribute('aria-invalid');
    }
  };

  // Validate on blur once touched, so errors never appear mid-typing.
  Array.prototype.forEach.call(form.querySelectorAll('input, select, textarea'), function (field) {
    if (field.type === 'hidden') return;
    field.addEventListener('blur', function () {
      showError(field, field.checkValidity() ? '' : messageFor(field));
    });
    field.addEventListener('input', function () {
      if (field.getAttribute('aria-invalid') === 'true' && field.checkValidity()) showError(field, '');
    });
  });

  form.addEventListener('submit', function (event) {
    var invalid = null;
    Array.prototype.forEach.call(form.querySelectorAll('input, select, textarea'), function (field) {
      if (field.type === 'hidden') return;
      var ok = field.checkValidity();
      showError(field, ok ? '' : messageFor(field));
      if (!ok && !invalid) invalid = field;
    });

    if (invalid) {
      event.preventDefault();
      invalid.focus();
      return;
    }

    // Submit in the background so we can show an inline success state.
    // Without fetch, the form posts normally and Netlify serves /organize/thanks/.
    if (!window.fetch) return;
    event.preventDefault();

    if (submit) {
      submit.disabled = true;
      submit.textContent = 'Sending...';
    }

    fetch('/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams(new FormData(form)).toString()
    })
      .then(function (response) {
        if (!response.ok) throw new Error('Request failed: ' + response.status);
        form.hidden = true;
        if (success) {
          success.hidden = false;
          success.setAttribute('tabindex', '-1');
          success.focus();
          success.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'center' });
        }
      })
      .catch(function () {
        // Fall back to a normal page POST rather than stranding the visitor.
        if (submit) {
          submit.disabled = false;
          submit.textContent = 'Request a demo';
        }
        form.removeAttribute('data-enhanced');
        form.submit();
      });
  });
  });
})();
