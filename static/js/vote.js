/**
 * AJAX Voting System for Kararsızım
 */

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

document.addEventListener('DOMContentLoaded', function () {
  document.addEventListener('click', async function (e) {
    const btn = e.target.closest('.option-btn');
    if (!btn || btn.disabled) return;

    const pollCard = btn.closest('[data-poll-id]');
    if (!pollCard) return;

    const pollId = pollCard.getAttribute('data-poll-id');
    const optionId = btn.getAttribute('data-option-id');
    const csrfToken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    // Temporarily disable buttons in this card while loading
    const allButtons = pollCard.querySelectorAll('.option-btn');
    allButtons.forEach(b => b.disabled = true);

    try {
      const response = await fetch(`/poll/${pollId}/vote/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: new URLSearchParams({ option_id: optionId })
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        alert(data.message || 'Oy kullanılırken bir hata oluştu.');
        // Re-enable if failed
        allButtons.forEach(b => b.disabled = false);
        return;
      }

      // Update UI with response data
      data.options.forEach(opt => {
        const optionElement = pollCard.querySelector(`[data-option-id="${opt.id}"]`);
        if (optionElement) {
          // Update progress bar width
          let progressBar = optionElement.querySelector('.option-progress-bar');
          if (!progressBar) {
            progressBar = document.createElement('div');
            progressBar.className = 'option-progress-bar';
            optionElement.prepend(progressBar);
          }
          progressBar.style.width = `${opt.percentage}%`;

          // Update percentage and vote stats
          let statsElement = optionElement.querySelector('.option-stats');
          if (!statsElement) {
            statsElement = document.createElement('div');
            statsElement.className = 'option-stats';
            optionElement.appendChild(statsElement);
          }

          let chosenBadge = '';
          if (opt.is_chosen) {
            optionElement.classList.add('chosen');
            chosenBadge = '<span class="chosen-mark">Oyunuz</span>';
          }

          statsElement.innerHTML = `${chosenBadge} <span>%${opt.percentage}</span>`;
          optionElement.disabled = true;
        }
      });

      // Update total votes in footer
      const totalVotesElem = pollCard.querySelector('.poll-total-votes');
      if (totalVotesElem) {
        totalVotesElem.textContent = `${data.total_votes} oy`;
      }

      // Add voted status indicator if present in card
      const footerStatus = pollCard.querySelector('.poll-card-status');
      if (footerStatus && !footerStatus.querySelector('.voted-badge')) {
        footerStatus.innerHTML = '<span class="voted-badge">Oy Verildi</span>';
      }

    } catch (err) {
      console.error('Oylama hatası:', err);
      alert('Bağlantı hatası oluştu. Lütfen tekrar deneyin.');
      allButtons.forEach(b => b.disabled = false);
    }
  });
});
