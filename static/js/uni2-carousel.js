(function() {
  var sliders = document.querySelectorAll(".uni2-carousel.js-auto-slider, .js-home-benefits-slider");

  sliders.forEach(function(slider) {
    var paused = false;
    var resumeTimer = null;

    function getStep() {
      var first = slider.children[0];
      if (!first) return 280;
      var gap = parseFloat(getComputedStyle(slider).columnGap || 16);
      return first.getBoundingClientRect().width + gap;
    }

    function pauseTemporarily() {
      paused = true;
      window.clearTimeout(resumeTimer);
      resumeTimer = window.setTimeout(function() { paused = false; }, 2600);
    }

    function updateDots() {
      if (!slider.id) return;
      var dots = document.querySelectorAll('[data-slider-dots="' + slider.id + '"] [data-slide-index]');
      if (!dots.length) return;
      var step = getStep();
      var active = Math.min(dots.length - 1, Math.max(0, Math.round(slider.scrollLeft / step)));
      dots.forEach(function(dot, index) {
        dot.classList.toggle("btn-primary", index === active);
        dot.classList.toggle("btn-outline-primary", index !== active);
        dot.setAttribute("aria-current", index === active ? "true" : "false");
      });
    }

    function scrollToIndex(index) {
      slider.scrollTo({ left: getStep() * index, behavior: "smooth" });
      pauseTemporarily();
      window.setTimeout(updateDots, 350);
    }

    function advance() {
      if (paused || slider.scrollWidth <= slider.clientWidth + 4) return;
      var maxScroll = slider.scrollWidth - slider.clientWidth;
      if (slider.scrollLeft >= maxScroll - 10) {
        slider.scrollTo({ left: 0, behavior: "smooth" });
        window.setTimeout(updateDots, 350);
        return;
      }
      slider.scrollBy({ left: getStep(), behavior: "smooth" });
      window.setTimeout(updateDots, 350);
    }

    slider.addEventListener("pointerenter", function() { paused = true; });
    slider.addEventListener("pointerleave", function() { paused = false; });
    slider.addEventListener("touchstart", function() { paused = true; }, { passive: true });
    slider.addEventListener("touchend", function() {
      window.setTimeout(function() { paused = false; }, 1800);
    }, { passive: true });
    slider.addEventListener("scroll", function() { window.requestAnimationFrame(updateDots); }, { passive: true });

    if (slider.id) {
      document.querySelectorAll('[data-slider-prev="' + slider.id + '"]').forEach(function(button) {
        button.addEventListener("click", function() {
          var step = getStep();
          var current = Math.round(slider.scrollLeft / step);
          scrollToIndex(Math.max(0, current - 1));
        });
      });

      document.querySelectorAll('[data-slider-next="' + slider.id + '"]').forEach(function(button) {
        button.addEventListener("click", function() {
          var step = getStep();
          var current = Math.round(slider.scrollLeft / step);
          scrollToIndex(Math.min(slider.children.length - 1, current + 1));
        });
      });

      document.querySelectorAll('[data-slider-dots="' + slider.id + '"] [data-slide-index]').forEach(function(button) {
        button.addEventListener("click", function() { scrollToIndex(Number(button.dataset.slideIndex)); });
      });
    }

    updateDots();
    window.setInterval(advance, 3400);
  });
})();
