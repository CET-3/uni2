(function() {
  var sliders = document.querySelectorAll('.uni2-carousel.js-auto-slider');
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  sliders.forEach(function(slider) {
    var interactionRoot = slider.closest('section') || slider.parentElement;
    var userPaused = reducedMotion.matches;
    var manuallyToggled = false;
    var pointerPaused = false;
    var focusPaused = false;
    var touchPaused = false;
    var resumeTimer = null;
    var dots = slider.id
      ? document.querySelectorAll('[data-slider-dots="' + slider.id + '"] [data-slide-index]')
      : [];
    var previousButtons = slider.id
      ? document.querySelectorAll('[data-slider-prev="' + slider.id + '"]')
      : [];
    var nextButtons = slider.id
      ? document.querySelectorAll('[data-slider-next="' + slider.id + '"]')
      : [];
    var toggleButtons = slider.id
      ? document.querySelectorAll('[data-slider-toggle="' + slider.id + '"]')
      : [];

    slider.setAttribute('role', 'region');
    slider.setAttribute('aria-roledescription', 'carrusel');
    slider.setAttribute('aria-live', 'off');

    Array.prototype.forEach.call(slider.children, function(slide, index) {
      slide.setAttribute('role', 'group');
      slide.setAttribute('aria-roledescription', 'diapositiva');
      slide.setAttribute('aria-label', (index + 1) + ' de ' + slider.children.length);
    });

    function getStep() {
      var first = slider.children[0];
      if (!first) return 280;
      var gap = parseFloat(window.getComputedStyle(slider).columnGap || 16);
      return first.getBoundingClientRect().width + gap;
    }

    function activeIndex() {
      var step = getStep();
      return Math.min(
        slider.children.length - 1,
        Math.max(0, Math.round(slider.scrollLeft / step))
      );
    }

    function isPaused() {
      return userPaused || pointerPaused || focusPaused || touchPaused || document.hidden;
    }

    function scrollBehavior() {
      return reducedMotion.matches ? 'auto' : 'smooth';
    }

    function updateToggleButtons() {
      toggleButtons.forEach(function(button) {
        button.setAttribute('aria-pressed', String(userPaused));
        button.setAttribute('aria-label', userPaused ? 'Reanudar carrusel' : 'Pausar carrusel');
        var icon = button.querySelector('i');
        if (icon) icon.className = userPaused ? 'bi bi-play-fill' : 'bi bi-pause-fill';
      });
    }

    function updateControls() {
      if (!slider.children.length) return;
      var active = activeIndex();

      dots.forEach(function(dot, index) {
        if (index === active) {
          dot.setAttribute('aria-current', 'true');
        } else {
          dot.removeAttribute('aria-current');
        }
      });
      previousButtons.forEach(function(button) { button.disabled = active === 0; });
      nextButtons.forEach(function(button) { button.disabled = active === slider.children.length - 1; });
    }

    function scrollToIndex(index) {
      if (!slider.children.length) return;
      var target = Math.min(slider.children.length - 1, Math.max(0, index));
      slider.scrollTo({ left: getStep() * target, behavior: scrollBehavior() });
      window.setTimeout(updateControls, reducedMotion.matches ? 0 : 350);
    }

    function pauseTouchTemporarily() {
      touchPaused = true;
      window.clearTimeout(resumeTimer);
      resumeTimer = window.setTimeout(function() { touchPaused = false; }, 1800);
    }

    function advance() {
      if (isPaused() || slider.scrollWidth <= slider.clientWidth + 4) return;
      var maxScroll = slider.scrollWidth - slider.clientWidth;
      if (slider.scrollLeft >= maxScroll - 10) {
        slider.scrollTo({ left: 0, behavior: scrollBehavior() });
      } else {
        slider.scrollBy({ left: getStep(), behavior: scrollBehavior() });
      }
      window.setTimeout(updateControls, reducedMotion.matches ? 0 : 350);
    }

    interactionRoot.addEventListener('pointerenter', function() { pointerPaused = true; });
    interactionRoot.addEventListener('pointerleave', function() { pointerPaused = false; });
    interactionRoot.addEventListener('focusin', function() { focusPaused = true; });
    interactionRoot.addEventListener('focusout', function(event) {
      if (!interactionRoot.contains(event.relatedTarget)) focusPaused = false;
    });
    slider.addEventListener('touchstart', pauseTouchTemporarily, { passive: true });
    slider.addEventListener('touchend', pauseTouchTemporarily, { passive: true });
    slider.addEventListener('scroll', function() {
      window.requestAnimationFrame(updateControls);
    }, { passive: true });
    slider.addEventListener('keydown', function(event) {
      if (event.target !== slider) return;
      if (event.key === 'ArrowLeft') {
        event.preventDefault();
        scrollToIndex(activeIndex() - 1);
      }
      if (event.key === 'ArrowRight') {
        event.preventDefault();
        scrollToIndex(activeIndex() + 1);
      }
    });

    previousButtons.forEach(function(button) {
      button.addEventListener('click', function() { scrollToIndex(activeIndex() - 1); });
    });
    nextButtons.forEach(function(button) {
      button.addEventListener('click', function() { scrollToIndex(activeIndex() + 1); });
    });
    dots.forEach(function(button) {
      button.addEventListener('click', function() {
        scrollToIndex(Number(button.dataset.slideIndex));
      });
    });
    toggleButtons.forEach(function(button) {
      button.addEventListener('click', function() {
        manuallyToggled = true;
        userPaused = !userPaused;
        updateToggleButtons();
      });
    });

    function followMotionPreference(event) {
      if (!manuallyToggled) {
        userPaused = event.matches;
        updateToggleButtons();
      }
    }

    if (reducedMotion.addEventListener) {
      reducedMotion.addEventListener('change', followMotionPreference);
    } else {
      reducedMotion.addListener(followMotionPreference);
    }

    updateToggleButtons();
    updateControls();
    window.setInterval(advance, 3400);
  });
})();
