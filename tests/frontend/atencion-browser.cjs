// Runner CDP sin dependencias: prueba datos y comportamiento, no HTML de prueba.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

async function main() {
    const [port, origin, output] = process.argv.slice(2);
    const tabs = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
    const socket = new WebSocket(tabs.find(tab => tab.type === 'page').webSocketDebuggerUrl);
    await new Promise(resolve => socket.addEventListener('open', resolve, {once: true}));
    let id = 0;
    const pending = new Map();
    const errors = [];
    socket.addEventListener('message', event => {
        const response = JSON.parse(event.data);
        if (response.method === 'Runtime.exceptionThrown') errors.push(response.params.exceptionDetails.text);
        if (pending.has(response.id)) {
            pending.get(response.id)(response);
            pending.delete(response.id);
        }
    });
    const send = (method, params = {}) => new Promise(resolve => {
        pending.set(++id, resolve);
        socket.send(JSON.stringify({id, method, params}));
    });
    const evaluate = async expression => {
        const result = await send('Runtime.evaluate', {expression, returnByValue: true});
        assert(!result.result.exceptionDetails, JSON.stringify(result.result.exceptionDetails));
        return result.result.result.value;
    };
    async function loaded() {
        for (let attempt = 0; attempt < 100; attempt++) {
            await new Promise(resolve => setTimeout(resolve, 50));
            if (await evaluate('document.readyState === "complete" && !!document.querySelector("h1")')) return;
        }
        throw new Error('La página no terminó de cargar');
    }
    await send('Page.enable');
    await send('Runtime.enable');
    await send('Network.setCookie', {name: 'sessionid', value: process.env.UNI2_TEST_SESSION, url: origin});
    for (const width of [1280, 390]) {
        await send('Emulation.setDeviceMetricsOverride', {width, height: 900, deviceScaleFactor: 1, mobile: width < 500});
        await send('Page.navigate', {url: origin + '/gestion/atencion-diaria/'});
        await loaded();
        assert.equal(await evaluate('document.querySelector("h1").textContent'), 'Atención diaria');
        assert.equal(await evaluate('document.querySelector(".uni2-metric-value").textContent'), '$ 30.000,75');
        assert(await evaluate('!!document.querySelector(".uni2-navbar")'));
        for (const theme of ['light', 'dark']) {
            await evaluate(`if (window.__uni2Theme !== '${theme}') document.querySelector('#theme-toggle').click()`);
            // Esperar las transiciones del design system antes de inspeccionar/capturar.
            await new Promise(resolve => setTimeout(resolve, 600));
            assert.equal(await evaluate('document.documentElement.dataset.theme'), theme);
            assert.deepEqual(await evaluate(`Array.from(document.querySelectorAll('.uni2-metric-card')).map(el => getComputedStyle(el).borderTopColor)`),
                ['rgb(63, 81, 181)', 'rgb(76, 203, 74)', 'rgb(255, 203, 48)'], 'Acentos de total, efectivo y billetera');
            assert.equal(await evaluate(`document.querySelectorAll('.uni2-metric-heading .bi[aria-hidden="true"]').length`), 3, 'Un icono decorativo por indicador');
            assert(await evaluate(`Array.from(document.querySelectorAll('.uni2-metric-label')).every(el => getComputedStyle(el).textTransform === 'none')`), 'Títulos en mayúscula inicial');
            const sideLinks = await evaluate(`Array.from(document.querySelectorAll('aside a')).map(el => {
                const style = getComputedStyle(el);
                return {color: style.color, decoration: style.textDecorationLine, height: el.getBoundingClientRect().height};
            })`);
            assert(sideLinks.length === 4 && sideLinks.every(link =>
                link.color === (theme === 'light' ? 'rgb(26, 26, 46)' : 'rgb(237, 242, 255)')
                && link.decoration === 'none' && link.height >= 44), JSON.stringify(sideLinks));
            assert(await evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Desborde horizontal');
            assert(await evaluate('Array.from(document.querySelectorAll(".uni2-metric-value")).every(el => el.scrollWidth <= el.clientWidth)'), 'Importe fuera de su tarjeta');
            const screenshot = await send('Page.captureScreenshot', {format: 'png', captureBeyondViewport: true});
            fs.writeFileSync(path.join(output, `atencion-${width}-${theme}.png`), Buffer.from(screenshot.result.data, 'base64'));
        }
        await evaluate('document.querySelector(".uni2-row-link").click()');
        await loaded();
        assert(await evaluate('document.querySelector("h1").textContent.includes("Detalle del pago")'));
        assert(await evaluate('document.body.textContent.includes("Sin fecha de carga auditada")'));
        await send('Page.navigate', {url: origin + '/gestion/atencion-diaria/'});
        await loaded();
        await evaluate('document.querySelector("#id_periodo").value="ayer";document.querySelector("form[method=get]").requestSubmit()');
        await loaded();
        assert.equal(await evaluate('document.querySelector(".uni2-metric-value").textContent'), '$ 0,00');
        assert(await evaluate('document.body.textContent.includes("No hay pagos para estos filtros.")'));
    }
    assert.deepEqual(errors, []);
    socket.close();
    console.log('OK: importes, filtros, detalle, layout de Uni2 y temas en desktop/mobile.');
}
main().catch(error => { console.error(error); process.exit(1); });
