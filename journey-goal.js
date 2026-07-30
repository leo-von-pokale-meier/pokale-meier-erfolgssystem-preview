(() => {
  const page = document.body.dataset.page;

  if (page === 'dashboard') {
    const stageCard = [...document.querySelectorAll('.grid.cols-3 > .card')]
      .find((card) => card.textContent.includes('Aktuelle Stufe'));

    if (stageCard) {
      stageCard.classList.add('stage-card');
      const action = stageCard.querySelector('.btn')?.closest('p');
      if (action) action.classList.add('stage-action');
    }
  }

  if (page === 'journey' && !document.querySelector('.journey-goal')) {
    const footerNote = document.querySelector('.footer-note');
    if (!footerNote) return;

    footerNote.insertAdjacentHTML(
      'beforebegin',
      `<section class="section journey-goal" aria-labelledby="journey-goal-title">
        <span class="eyebrow">Dein Zielbild</span>
        <h2 id="journey-goal-title">Dein Weg zum Leuchtfeuer</h2>
        <figure>
          <img src="assets/zielbild-leuchtfeuer-16-9.webp" alt="Zielbild: Dein Weg zum Leuchtfeuer von Bronze über Silber bis Leuchtfeuer">
        </figure>
      </section>`,
    );
  }
})();
