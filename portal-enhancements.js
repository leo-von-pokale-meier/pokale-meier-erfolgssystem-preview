(() => {
  const page = document.body.dataset.page;
  const content = document.querySelector('.portal > div');
  if (!content || !['league', 'partners', 'profile'].includes(page)) return;

  const defaults = { company: 'Wirkungspartner GmbH', website: 'https://www.wirkungspartner.de', usp: 'Wir machen komplexe Veränderung für Mittelständler in klare, messbare Umsetzung.', offer: 'Strategieberatung und Umsetzung für nachhaltiges Wachstum.', audience: 'Geschäftsführende mittelständischer Unternehmen', onboarding: 'Zielbild geschärft · erste Erfolgskunde und Award-Moment für Q3 vereinbart.', score: 84 };
  const key = 'erfolgsportal-company-profile';
  const profile = { ...defaults, ...JSON.parse(localStorage.getItem(key) || '{}') };
  const escape = value => String(value).replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  const score = new Intl.NumberFormat('de-DE').format(profile.score);
  const level = n => n >= 900 ? 'Leuchtfeuer' : n >= 250 ? 'Silber' : 'Bronze';
  const partnerData = [
    {name:'SPEEDSCALING', score:1205, status:'Leuchtfeuer', url:'https://www.speedscaling.de/', promise:'Wir helfen Unternehmern, aus Wachstum ein skalierbares System zu machen.', detail:'SPEEDSCALING verbindet klare Skalierungsstrategie mit Umsetzungstempo für ambitionierte Unternehmer.', solution:'Skalierung & Vertrieb'},
    {name:'Scaling Champions', score:917, status:'Leuchtfeuer', url:'https://www.scaling-champions.com/', promise:'Wir bauen Vertriebsorganisationen, die planbar und ohne Gründer-Abhängigkeit wachsen.', detail:'Scaling Champions entwickelt wiederholbare Vertriebsprozesse und befähigt Teams, Verantwortung zu übernehmen.', solution:'Vertrieb & Führung'},
    {name:'Skillisch Marketing', score:25, status:'Bronze', url:'https://skillisch.de/', promise:'Wir machen B2B-Marken sichtbar, die aus Kompetenz echte Nachfrage gewinnen wollen.', detail:'Skillisch Marketing verbindet strategische Positionierung, Content und Performance-Marketing für B2B-Unternehmen.', solution:'Marketing & Sichtbarkeit'}
  ];
  const points = `<section class="card points-card"><h3>So ist dein Leuchtfeuer-Score valide</h3><div class="points-grid"><p><b>+10 Punkte</b><span>Ein dokumentierter Kundenerfolg</span></p><p><b>+25 Punkte</b><span>Nachweis und Kundenfreigabe liegen vor</span></p><p><b>+50 Punkte</b><span>Erfolg als Award oder Fallstudie sichtbar gemacht</span></p><p><b>+100 Punkte</b><span>Nachweisbarer Empfehlungs- oder Neukundeneffekt</span></p></div><p class="validation">Gezählt werden nur strukturierte, datierte Erfolgsakten mit Nachweis und Freigabe. Punkte werden nach einer Änderung neu berechnet; keine Selbstauskunft fließt ungeprüft in die öffentliche Liste.</p></section>`;

  if (page === 'league') {
    const rankings = [...partnerData, {name:profile.company, score:Number(profile.score), status:level(Number(profile.score)), url:profile.website, promise:profile.usp}].sort((a,b) => b.score-a.score);
    content.innerHTML = `<div class="eyebrow">Impact League</div><h2>Die ewige Bestenliste</h2><p class="lead">Sie zeigt die Leuchtfeuer, die Kundenerfolge nachweisbar sichtbar machen – und die aktuelle Bewegung im Netzwerk.</p><div class="league-hero"><div><small>Dein aktueller Score</small><strong>${score}</strong><span>Punkte · ${level(Number(profile.score))}</span></div><p>Dein Wert wächst ausschließlich mit bestätigten Erfolgsakten. Jede Änderung bleibt nachvollziehbar.</p></div><section class="card"><h3>Ewige Bestenliste</h3><ol class="league-list">${rankings.map((item,index) => `<li><span class="rank">${String(index+1).padStart(2,'0')}</span><div><a href="${escape(item.url)}" target="_blank" rel="noopener">${escape(item.name)}</a><small>${escape(item.status)} · ${escape(item.promise)}</small></div><b>${new Intl.NumberFormat('de-DE').format(item.score)} <small>Punkte</small></b></li>`).join('')}</ol></section><section class="card"><h3>Aktuelle Kundenerfolge</h3><div class="current-wins"><p><b>Heute · Erfolgskunde angelegt</b><span>${escape(profile.company)} hat eine neue Erfolgsakte zur Prüfung eingereicht.</span></p><p><b>Diese Woche · Award übergeben</b><span>SPEEDSCALING hat einen 100.000-€-Monatsumsatz sichtbar gewürdigt.</span></p><p><b>Diese Woche · Empfehlung bestätigt</b><span>Scaling Champions dokumentiert einen gewonnenen Neukunden aus einer Kundenempfehlung.</span></p></div></section>${points}`;
  }

  if (page === 'partners') {
    const cards = partnerData.map((partner, i) => `<button class="partner-card" data-partner="${i}"><div><span class="chip ${partner.status === 'Leuchtfeuer' ? 'orange' : ''}">${partner.status}</span><strong>${new Intl.NumberFormat('de-DE').format(partner.score)} <small>Punkte</small></strong></div><h3>${partner.name}</h3><p>${partner.promise}</p><span class="open-profile">Unternehmensprofil öffnen →</span></button>`).join('');
    content.innerHTML = `<div class="eyebrow">Dein Netzwerk</div><h2>Partner & Leuchtfeuer</h2><p class="lead">Finde Unternehmen, deren Leistung deine Kunden weiterbringt. Die Filterfunktion für Lösungen folgt mit dem Live-Netzwerk; diese drei Profile zeigen das spätere Prinzip.</p><div class="partner-filter"><span>Filter nach Lösung <b>· demnächst</b></span><button disabled>Skalierung</button><button disabled>Marketing</button><button disabled>Vertrieb</button></div><div class="partner-grid">${cards}</div><dialog class="partner-dialog"><button class="dialog-close" aria-label="Profil schließen">×</button><div class="dialog-content"></div></dialog>`;
    const dialog = content.querySelector('dialog');
    const dialogContent = content.querySelector('.dialog-content');
    content.querySelectorAll('[data-partner]').forEach(card => card.addEventListener('click', () => {
      const p = partnerData[card.dataset.partner];
      dialogContent.innerHTML = `<span class="eyebrow">Erfolgspartner · ${p.status}</span><h2>${p.name}</h2><p class="dialog-score">${new Intl.NumberFormat('de-DE').format(p.score)} Punkte</p><h3>Unser Versprechen</h3><p>${p.promise}</p><h3>Was wir machen</h3><p>${p.detail}</p><h3>Passend für</h3><p>${p.solution}</p><a class="btn" href="${p.url}" target="_blank" rel="noopener">Website besuchen</a>`;
      dialog.showModal();
    }));
    content.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  }

  if (page === 'profile') {
    content.innerHTML = `<div class="eyebrow">Organisation & Zugang</div><h2>Dein Unternehmensprofil</h2><p class="lead">Diese Angaben bilden später dein sichtbares Leuchtfeuer-Profil: von dir gepflegt und im Onboarding gemeinsam geschärft.</p><form class="profile-form"><div class="grid cols-2"><label>Unternehmensname<input name="company" value="${escape(profile.company)}" required></label><label>Website-URL<input name="website" type="url" value="${escape(profile.website)}" required></label><label>Leistungsversprechen<input name="offer" value="${escape(profile.offer)}" required></label><label>Wunschkunden<input name="audience" value="${escape(profile.audience)}" required></label></div><label>Dein Haupt-USP <textarea name="usp" required>${escape(profile.usp)}</textarea><small>Wird im Onboarding formuliert und später im Partnerprofil angezeigt.</small></label><label>Ergebnis aus dem Onboarding <textarea name="onboarding" required>${escape(profile.onboarding)}</textarea></label><div class="profile-actions"><button class="btn" type="submit">Profil speichern</button><a class="btn alt" href="${escape(profile.website)}" target="_blank" rel="noopener">Website öffnen</a></div><p class="save-message" aria-live="polite"></p></form><section class="card score-preview"><small>Dein aktueller Leuchtfeuer-Score</small><b>${score}</b><p>Punkte · ${level(Number(profile.score))}. Der Score wird zentral anhand deiner bestätigten Erfolge berechnet.</p></section>`;
    content.querySelector('.profile-form').addEventListener('submit', event => {
      event.preventDefault();
      const saved = Object.fromEntries(new FormData(event.currentTarget));
      localStorage.setItem(key, JSON.stringify({...profile, ...saved}));
      content.querySelector('.save-message').textContent = 'Gespeichert – dein Profil ist in dieser Demo sofort aktualisiert.';
    });
  }
})();
