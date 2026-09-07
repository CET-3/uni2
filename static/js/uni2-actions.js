/* Acciones compartidas: un submit nativo o una operación asíncrona por vez. */
(function () {
  'use strict';
  if (window.Uni2Actions) return;

  const active = new Map();
  const resumed = new WeakSet();
  let status;

  function announce(text) {
    if (!status) {
      status = document.createElement('span');
      status.className = 'visually-hidden';
      status.setAttribute('role', 'status');
      document.body.append(status);
    }
    status.textContent = text;
  }

  function restoreAttribute(element, name, value) {
    if (value === null) element.removeAttribute(name);
    else element.setAttribute(name, value);
  }

  function paint(button, text, success) {
    if (!button) return;
    if (button instanceof HTMLInputElement) {
      button.value = (success ? '✓ ' : '') + text;
      return;
    }
    const icon = document.createElement('span');
    icon.className = success ? 'bi bi-check-lg' : 'spinner-border spinner-border-sm uni2-action-spinner';
    icon.setAttribute('aria-hidden', 'true');
    button.replaceChildren(icon, document.createTextNode(' ' + text));
  }

  function prepare(button) {
    if (!button || button.dataset.actionPrepared || !button.getClientRects().length) return;
    // Reservar espacio para los textos antes de interactuar evita saltos de ancho.
    const clone = button.cloneNode(true);
    clone.removeAttribute('id');
    clone.removeAttribute('name');
    // Las utilidades Bootstrap (w-100) llevan !important. Medimos texto
    // intrínseco, no el ancho del viewport ni el de una tarjeta fluida.
    clone.style.cssText = 'position:fixed;visibility:hidden;width:max-content!important;min-width:0!important;max-width:none!important;pointer-events:none';
    document.body.append(clone);
    let width = clone.getBoundingClientRect().width;
    for (const success of [false, true]) {
      paint(clone, success ? (button.dataset.successText || 'Guardado') : (button.dataset.loadingText || 'Procesando…'), success);
      width = Math.max(width, clone.getBoundingClientRect().width);
    }
    clone.remove();
    button.style.minWidth = 'min(100%, ' + Math.ceil(width) + 'px)';
    button.dataset.actionPrepared = 'true';
  }

  function begin(owner, button) {
    if (active.has(owner)) return false;
    prepare(button);
    const controls = owner instanceof HTMLFormElement
      ? Array.from(owner.elements).filter(el => ['submit', 'image'].includes(el.type))
      : [owner];
    const state = {
      button, controls: controls.map(el => [el, el.disabled, el.getAttribute('aria-disabled')]),
      busy: owner.getAttribute('aria-busy'), submitting: owner.getAttribute('data-submitting'),
      children: button ? Array.from(button.childNodes) : [], value: button && button.value,
      width: button?.style.width,
    };
    if (button) {
      // Las fuentes de iconos pueden terminar de cargar después de preparar
      // los mínimos. Conservar también el ancho real durante esta operación.
      button.style.width = 'min(100%, ' + button.getBoundingClientRect().width + 'px)';
    }
    active.set(owner, state);
    owner.dataset.submitting = 'true';
    owner.setAttribute('aria-busy', 'true');
    controls.forEach(el => { el.disabled = true; el.setAttribute('aria-disabled', 'true'); });
    const text = button?.dataset.loadingText || 'Procesando…';
    paint(button, text, false);
    announce(text);
    return true;
  }

  function reset(owner) {
    resumed.delete(owner);
    const state = active.get(owner);
    if (!state) return;
    clearTimeout(state.timer);
    state.mirror?.remove();
    state.controls.forEach(([el, disabled, aria]) => {
      el.disabled = disabled;
      restoreAttribute(el, 'aria-disabled', aria);
    });
    if (state.button instanceof HTMLInputElement) state.button.value = state.value;
    else if (state.button) state.button.replaceChildren(...state.children);
    if (state.button) state.button.style.width = state.width;
    restoreAttribute(owner, 'aria-busy', state.busy);
    restoreAttribute(owner, 'data-submitting', state.submitting);
    active.delete(owner);
  }

  async function run(button, operation) {
    if (!begin(button, button)) return;
    const state = active.get(button);
    try {
      const result = await operation();
      if (active.get(button) !== state) return result;
      const text = button.dataset.successText || 'Guardado';
      paint(button, text, true);
      button.setAttribute('aria-busy', 'false');
      announce(text);
      state.timer = setTimeout(() => reset(button), 1200);
      return result;
    } catch (error) {
      if (active.get(button) === state) reset(button);
      throw error; // El consumidor muestra el error con el mecanismo de su pantalla.
    }
  }

  document.addEventListener('submit', function (event) {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) return;
    if (resumed.has(form)) {
      resumed.delete(form);
      queueMicrotask(() => { if (event.defaultPrevented) reset(form); });
      return;
    }
    if (active.has(form)) {
      event.preventDefault();
      event.stopImmediatePropagation();
      return;
    }
    const submitter = event.submitter;
    const method = submitter?.getAttribute('formmethod') || form.method;
    if (method.toLowerCase() !== 'post' || event.defaultPrevented) return;

    // Un control disabled no se serializa. Copiar el submitter antes de
    // deshabilitarlo conserva acciones como name="action" value="confirmar".
    const name = submitter?.name, value = submitter?.value;
    if (!begin(form, submitter || Array.from(form.elements).find(el => el.type === 'submit' && !el.disabled))) return;
    if (name) {
      const mirror = document.createElement('input');
      mirror.type = 'hidden'; mirror.name = name; mirror.value = value;
      form.append(mirror);
      active.get(form).mirror = mirror;
    }

    const pending = [];
    form.dispatchEvent(new CustomEvent('uni2:before-submit', {
      bubbles: true, detail: { waitUntil: promise => pending.push(promise) },
    }));
    if (pending.length) {
      event.preventDefault();
      const state = active.get(form);
      Promise.all(pending).then(() => {
        if (active.get(form) !== state) return;
        resumed.add(form);
        form.requestSubmit(submitter || undefined);
        // Si la validación nativa impidió submit, no consumió la reanudación.
        if (resumed.has(form)) reset(form);
      }).catch(() => {
        if (active.get(form) === state) {
          reset(form);
          announce('No se pudo completar la acción. Volvé a intentarlo.');
        }
      });
    } else {
      // Permitir que validadores y la PWA cancelen el envío sin dejarlo ocupado.
      queueMicrotask(() => { if (event.defaultPrevented) reset(form); });
    }
  }, true);

  window.addEventListener('pageshow', event => {
    if (!event.persisted) return;
    for (const owner of active.keys()) reset(owner);
  });
  function prepareButtons() {
    document.querySelectorAll('form[method="post"] button[type="submit"], [data-loading-text]').forEach(prepare);
  }
  document.addEventListener('shown.bs.modal', prepareButtons);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', prepareButtons, {once: true});
  else prepareButtons();

  window.Uni2Actions = {run, reset};
})();
