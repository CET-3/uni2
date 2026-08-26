(() => {
    const form = document.querySelector("[data-solicitud-asociacion-form]");
    if (!form) return;

    const cursoContainer = form.querySelector('[data-solicitud-field="curso"]');
    const clasificacionContainer = form.querySelector('[data-solicitud-field="clasificacion"]');
    const curso = form.querySelector("#id_curso_actual");
    const clasificacion = form.querySelector("#id_clasificacion_adherente");
    const opciones = form.querySelectorAll('input[name="es_estudiante_cet3"]');

    const actualizar = () => {
        const elegida = form.querySelector('input[name="es_estudiante_cet3"]:checked');
        const esEstudiante = elegida?.value === "si";
        const esAdherente = elegida?.value === "no";

        cursoContainer.hidden = !esEstudiante;
        clasificacionContainer.hidden = !esAdherente;
        curso.disabled = !esEstudiante;
        clasificacion.disabled = !esAdherente;
    };

    opciones.forEach((opcion) => opcion.addEventListener("change", actualizar));
    actualizar();
})();
