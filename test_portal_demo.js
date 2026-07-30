const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('portal-demo.js', 'utf8');
function render(page) {
  const root = { innerHTML: '', listeners: {}, addEventListener(type, fn) { this.listeners[type] = fn; } };
  const document = {
    readyState: 'complete', body: { dataset: { page }, innerHTML: '' },
    getElementById(id) { return id === 'demo-root' ? root : null; },
    addEventListener() {}, querySelector(selector) { return selector === '[data-page]' ? this.body : null; }
  };
  const context = { document, location: { pathname: `/${page}.html` }, localStorage: { getItem() { return null; }, setItem() {} }, console, window: { addEventListener() {} } };
  vm.runInNewContext(source, context);
  return document.body.innerHTML;
}

test('all customer modules render a navigable production-style demo shell', () => {
  for (const page of ['dashboard','journey','awards','customers','league','recommendations','profile','partners','knowledge']) {
    const html = render(page);
    assert.match(html, /Erfolgssoftware/);
    assert.match(html, /class="portal"/);
  }
});

test('dashboard brings the customer process together', () => {
  const html = render('dashboard');
  for (const marker of ['Leuchtfeuer-Score','Strategietermin','Nächste empfohlene Aktion','Aktuelle To-dos','Aktuelle Awards','KPI-Übersicht']) assert.match(html, new RegExp(marker));
});

test('journey, awards, customers and referrals expose the required flows', () => {
  assert.match(render('journey'), /Termin dokumentieren/);
  assert.match(render('journey'), /KI-Automatisierung/);
  assert.match(render('awards'), /Stufenplanung öffnen/);
  assert.match(render('customers'), /Kunde hinzufügen/);
  assert.match(render('league'), /Impact League/);
  assert.match(render('recommendations'), /Empfehlung eintragen/);
  assert.match(render('recommendations'), /Eigene Empfehlungen aufbauen/);
});

test('internal view is a distinct control cockpit', () => {
  const html = render('admin');
  for (const marker of ['Internes Board','Programm veröffentlichen','Kunden-Radar','TL;DV','Audit-Log']) assert.match(html, new RegExp(marker));
});
