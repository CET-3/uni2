(function () {
  'use strict';

  function initialize(form) {
    const typeField = form.querySelector('[name="tipo"]');
    const courseGroup = form.querySelector('[data-asociado-field="curso"]');
    const classificationGroup = form.querySelector('[data-asociado-field="clasificacion"]');
    if (!typeField || !courseGroup || !classificationGroup) return;

    const courseField = courseGroup.querySelector('select');
    const classificationField = classificationGroup.querySelector('select');

    function update() {
      const isAdherent = typeField.value === 'adherente';
      courseGroup.hidden = isAdherent;
      classificationGroup.hidden = !isAdherent;
      if (courseField) courseField.disabled = isAdherent;
      if (classificationField) classificationField.disabled = !isAdherent;
    }

    typeField.addEventListener('change', update);
    update();
  }

  document.querySelectorAll('[data-asociado-tipo-form]').forEach(initialize);
})();
