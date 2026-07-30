const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');

const js = fs.readFileSync('portal-enhancements.js', 'utf8');
const css = fs.readFileSync('portal-enhancements.css', 'utf8');
const landing = fs.readFileSync('index.html', 'utf8');
const customerLeague = fs.readFileSync('kunden-bestenliste.html', 'utf8');
const internal = fs.readFileSync('interne-uebersicht.html', 'utf8');
const journey = fs.readFileSync('kunden-etappen.html', 'utf8');
const journeyGoal = fs.readFileSync('journey-goal.js', 'utf8');

test('landing page makes the leuchtfeuer journey, ranking and gallery visible', () => {
  assert.match(landing, /Wir machen dich zum Vertrauensführer deiner Branche\./);
  assert.match(landing, /Dein Weg zum Leuchtfeuer/);
  assert.match(landing, /Unsere Leuchtfeuer, echte Erfolgsgeschichten\./);
  assert.match(landing, /zielbild-leuchtfeuer-1-1\.webp/);
  assert.match(landing, /roadmap-fullbleed/);
  assert.match(landing, /SPEEDSCALING/);
  assert.match(landing, /1\.205 Punkte/);
});

test('customer journey shows the 16:9 goal image and keeps the stage action below its copy', () => {
  assert.match(journey, /journey-goal\.js/);
  assert.match(journeyGoal, /zielbild-leuchtfeuer-16-9\.webp/);
  assert.match(journeyGoal, /stage-card/);
  assert.match(journeyGoal, /stage-action/);
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

test('Impact League has dedicated public and internal entry points and is linked from the public landing page', () => {
  const publicLeague = fs.readFileSync('impact-league.html', 'utf8');
  const internalLeague = fs.readFileSync('interne-impact-league.html', 'utf8');
  assert.match(landing, /href="impact-league\.html"/);
  assert.match(publicLeague, /Unsere sichtbaren Erfolgspartner/);
  assert.match(publicLeague, /SPEEDSCALING/);
  assert.match(internal, /href="interne-impact-league\.html"/);
  assert.match(internalLeague, /Interne Impact League/);
});

test('customer league presents live competition mechanics and a visible next milestone', () => {
  assert.match(customerLeague, /league-gamification/);
  assert.match(js, /Dein nächstes Etappenziel/);
  assert.match(js, /Rang verändert sich live/);
  assert.match(js, /league-progress/);
  assert.match(css, /league-gamification/);
});
