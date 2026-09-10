/* Django entrega los cálculos; este archivo sólo dibuja y navega. */
(() => {
    const source = document.getElementById('datos-metricas');
    if (!source || !window.Chart) return;
    const datos = JSON.parse(source.textContent);
    const moneda = new Intl.NumberFormat('es-AR', {style: 'currency', currency: 'ARS'});
    const numero = new Intl.NumberFormat('es-AR', {maximumFractionDigits: 1});
    let movimientos = false;
    let padron;
    let cuotas;

    function dibujar() {
        padron?.destroy();
        cuotas?.destroy();
        const styles = getComputedStyle(document.documentElement);
        const color = token => styles.getPropertyValue(token).trim();
        const azul = color('--color-action-on-surface');
        const verde = color('--color-success-text');
        const rojo = color('--color-danger-text');
        const texto = color('--color-text-secondary');
        const base = {
            locale: 'es-AR',
            responsive: true, maintainAspectRatio: false,
            animation: !matchMedia('(prefers-reduced-motion: reduce)').matches,
            plugins: {legend: {labels: {color: texto}}},
            scales: {x: {ticks: {color: texto}, grid: {display: false}}, y: {beginAtZero: true, ticks: {color: texto, precision: 0}, grid: {color: color('--color-border-subtle')}}},
        };
        padron = new Chart(document.getElementById('grafico-padron'), {
            type: movimientos ? 'bar' : 'line',
            data: {labels: datos.padron.map(f => f.etiqueta), datasets: movimientos ? [
                {label: 'Altas', data: datos.padron.map(f => f.altas), backgroundColor: verde},
                {label: 'Bajas', data: datos.padron.map(f => f.bajas), backgroundColor: rojo},
            ] : [{label: 'Activos al cierre', data: datos.padron.map(f => f.activos), borderColor: azul, backgroundColor: azul, tension: 0.15}]},
            options: {...base, onClick(event, elementos) {
                if (!movimientos || !elementos.length) return;
                const punto = elementos[0];
                const url = datos.padron[punto.index][punto.datasetIndex ? 'url_bajas' : 'url_altas'];
                if (url) window.location.assign(url);
            }},
        });
        cuotas = new Chart(document.getElementById('grafico-cuotas'), {
            type: 'bar',
            data: {labels: datos.cuotas.map(f => f.etiqueta), datasets: [
                {label: 'Generado', data: datos.cuotas.map(f => Number(f.generado)), backgroundColor: azul},
                {label: 'Cobrado', data: datos.cuotas.map(f => f.cobrado === null ? null : Number(f.cobrado)), backgroundColor: verde},
            ]},
            options: {...base, plugins: {...base.plugins, tooltip: {callbacks: {
                label: context => `${context.dataset.label}: ${moneda.format(context.parsed.y)}`,
                afterBody: items => {
                    if (!items.length) return [];
                    const fila = datos.cuotas[items[0].dataIndex];
                    return [`Cumplimiento: ${fila.cumplimiento === null ? '—' : numero.format(fila.cumplimiento) + ' %'}`, `Pendiente: ${moneda.format(fila.pendiente)}`];
                },
            }}}},
        });
    }
    for (const [id, modo] of [['mostrar-activos', false], ['mostrar-movimientos', true]]) {
        document.getElementById(id).addEventListener('click', () => {
            movimientos = modo;
            for (const button of document.querySelectorAll('#mostrar-activos, #mostrar-movimientos')) {
                const activo = button.id === id;
                button.classList.toggle('active', activo);
                button.setAttribute('aria-pressed', String(activo));
            }
            dibujar();
        });
    }
    document.querySelectorAll('[data-open-details]').forEach(link => link.addEventListener('click', () => {
        document.querySelector(link.getAttribute('href')).open = true;
    }));
    new MutationObserver(dibujar).observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});
    dibujar();
})();
