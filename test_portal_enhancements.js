const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');

const js = fs.readFileSync('portal-enhancements.js', 'utf8');
const css = fs.readFileSync('portal-enhancements.css', 'utf8');
const landing = fs.readFileSync('index.html', 'utf8');

test('landing page makes the leuchtfeuer journey, ranking and gallery visible', () => {
  assert.match(landing, /Wir machen dich zum Vertrauensführer deiner Branche\./);
  assert.match(landing, /Dein Weg zum Leuchtfeuer/);
  assert.match(landing, /Unsere Leuchtfeuer, echte Erfolgsgeschichten\./);
  assert.match(landing, /weg-zum-leuchtfeuer\.png/);
  assert.match(landing, /SPEEDSCALING/);
  assert.match(landing, /1\.205 Punkte/);
});

test('partner profiles, validated league score and self-managed website data are available', () => {
  for (const name of ['SPEEDSCALING', 'Scaling Champions', 'Skillisch Marketing']) assert.match(js, new RegExp(name));
  assert.match(js, /Website-URL/);
  assert.match(js, /Haupt-USP/);
  assert.match(js, /Gezählt werden nur strukturierte, datierte Erfolgsakten/);
  assert.match(js, /showModal\(\)/);
  assert.match(js, /localStorage\.setItem/);
  assert.match(css, /partner-grid/);
});
