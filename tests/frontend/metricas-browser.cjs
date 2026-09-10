const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

async function main() {
    const [port, origin, output] = process.argv.slice(2);
    const tabs = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
    const socket = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl);
    await new Promise(resolve => socket.addEventListener('open', resolve, {once: true}));
    let id = 0;
    const pending = new Map();
    const errors = [];
    socket.addEventListener('message', event => {
        const r = JSON.parse(event.data);
        if (r.method === 'Runtime.exceptionThrown') errors.push(r.params.exceptionDetails.text);
        if (pending.has(r.id)) {pending.get(r.id)(r); pending.delete(r.id);}
    });
    const send = (method, params = {}) => new Promise(resolve => {pending.set(++id, resolve); socket.send(JSON.stringify({id, method, params}));});
    const evaluate = async expression => {
        const r = await send('Runtime.evaluate', {expression, returnByValue: true});
        assert(!r.result.exceptionDetails, JSON.stringify(r.result.exceptionDetails));
        return r.result.result.value;
    };
    const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
    async function loaded() {
        for (let i = 0; i < 100; i++) {
            await pause(50);
            if (await evaluate('document.readyState === "complete" && !!document.querySelector("#datos-metricas") && !!window.Chart')) return;
        }
        throw Error('No cargó Métricas');
    }
    await send('Page.enable');
    await send('Runtime.enable');
    await send('Emulation.setEmulatedMedia', {features: [{name: 'prefers-reduced-motion', value: 'reduce'}]});
    await send('Network.setCookie', {name: 'sessionid', value: process.env.UNI2_TEST_SESSION, url: origin});
    for (const width of [1280, 768, 390]) {
        await send('Emulation.setDeviceMetricsOverride', {width, height: 1000, deviceScaleFactor: 1, mobile: width < 500});
        await send('Page.navigate', {url: origin + '/'});
        for (let i = 0; i < 100; i++) {
            await pause(50);
            if (await evaluate('document.readyState === "complete" && !!document.querySelector("[aria-labelledby=otros-accesos-title] .uni2-service-card")')) break;
        }
        assert(await evaluate(`(() => {
            const cards = Array.from(document.querySelectorAll('[aria-labelledby=otros-accesos-title] .uni2-service-card'));
            return cards.length > 0 && cards.every(card => {
                const bottomGap = card.getBoundingClientRect().bottom - card.lastElementChild.getBoundingClientRect().bottom;
                return bottomGap <= parseFloat(getComputedStyle(card).paddingBottom) + 1 && !card.querySelector('.link');
            });
        })()`), 'Accesos de home sin espacio reservado debajo del contenido ni enlace redundante');
        await send('Page.navigate', {url: origin + '/gestion/metricas/'});
        await loaded();
        for (const theme of ['light', 'dark']) {
            await evaluate(`if(window.__uni2Theme!=='${theme}') window.__uni2ToggleTheme()`);
            await pause(650);
            assert.equal(await evaluate('document.querySelectorAll(".uni2-metric-card").length'), 4);
            assert.equal(await evaluate('document.querySelectorAll(".uni2-metric-proportion").length'), 2);
            assert.equal(await evaluate('document.querySelectorAll(".uni2-metric-proportion a").length'), 0);
            assert.deepEqual(await evaluate(`Array.from(document.querySelectorAll('.uni2-metric-card')).map(el => getComputedStyle(el).borderTopColor)`), ['rgb(63, 81, 181)', 'rgb(76, 203, 74)', 'rgb(255, 203, 48)', 'rgb(255, 43, 43)']);
            assert(await evaluate(`(() => {
                const cards = Array.from(document.querySelectorAll('.uni2-metrics-overview .uni2-metric-card')).map(el => el.getBoundingClientRect());
                return innerWidth < 576 ? cards.every((r, i) => !i || r.top >= cards[i-1].bottom) : cards[0].top === cards[1].top;
            })()`), 'Una card por fila en móvil; pares en pantallas más anchas');
            assert.deepEqual(await evaluate('Array.from(document.querySelectorAll(".uni2-metric-progress")).map(el => el.value)'), [100, 100]);
            assert(await evaluate(`(() => {
                const cards = Array.from(document.querySelectorAll('.uni2-metric-proportion')).map(el => el.getBoundingClientRect());
                return innerWidth < 768 ? cards[1].top >= cards[0].bottom : cards[0].top === cards[1].top;
            })()`), 'Proporciones en dos columnas desde tablet; una en móvil');
            assert(await evaluate('document.documentElement.scrollWidth <= innerWidth'), JSON.stringify(await evaluate(`({width: innerWidth, overflow: Array.from(document.querySelectorAll('body *')).filter(el => el.getBoundingClientRect().right > innerWidth + 1 && el.getBoundingClientRect().width > 0).slice(0,12).map(el => ({tag: el.tagName, clase: el.className, text: el.textContent.slice(0,70), right: el.getBoundingClientRect().right}))})`)));
            assert(await evaluate('Array.from(document.querySelectorAll(".uni2-metric-value")).every(el => el.scrollWidth <= el.clientWidth)'), 'Importe grande cortado');
            assert.equal(await evaluate('Object.keys(Chart.instances).length'), 2);
            assert(await evaluate(`Array.from(document.querySelectorAll('.uni2-metrics-page table tr')).every(row => Array.from(row.children).slice(1).every(cell => getComputedStyle(cell).textAlign === 'right'))`), 'Columnas numéricas alineadas a la derecha');
            assert.equal(await evaluate('Chart.getChart("grafico-cuotas").data.datasets[0].data.at(-1)'), 26100000);
            await evaluate('document.querySelector("#mostrar-movimientos").click()');
            assert.equal(await evaluate('Chart.getChart("grafico-padron").config.type'), 'bar');
            await evaluate('document.querySelector("#mostrar-activos").click()');
            await evaluate(`document.querySelector('a[href="#adherentes"]').click()`);
            assert(await evaluate('document.querySelector("#adherentes").open'));
            const r = await send('Page.captureScreenshot', {format: 'png', captureBeyondViewport: true});
            fs.writeFileSync(path.join(output, `metricas-${width}-${theme}.png`), Buffer.from(r.result.data, 'base64'));
        }
    }
    assert.deepEqual(errors, []);
    socket.close();
    console.log('OK: 4 cards, 2 proporciones, colores, gráficos, importes grandes, temas y mobile.');
}
main().catch(error => {console.error(error); process.exit(1);});
