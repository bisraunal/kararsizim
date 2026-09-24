/**
 * Dynamic Poll Option Management (Min: 2, Max: 5)
 */
document.addEventListener('DOMContentLoaded', function () {
  const container = document.getElementById('options-container');
  const addBtn = document.getElementById('add-option-btn');
  const optionCountDisplay = document.getElementById('option-count-display');

  if (!container || !addBtn) return;

  const MIN_OPTIONS = 2;
  const MAX_OPTIONS = 5;

  function updateOptionState() {
    const items = container.querySelectorAll('.option-input-group');
    const count = items.length;

    if (optionCountDisplay) {
      optionCountDisplay.textContent = `${count} / ${MAX_OPTIONS} seçenek`;
    }

    // Toggle Add button
    addBtn.disabled = count >= MAX_OPTIONS;
    if (count >= MAX_OPTIONS) {
      addBtn.classList.add('disabled');
    } else {
      addBtn.classList.remove('disabled');
    }

    // Update numbers & remove buttons
    items.forEach((item, index) => {
      const badge = item.querySelector('.option-number-badge');
      if (badge) badge.textContent = index + 1;

      const removeBtn = item.querySelector('.btn-remove-option');
      if (removeBtn) {
        removeBtn.disabled = count <= MIN_OPTIONS;
      }
    });
  }

  // Add Option handler
  addBtn.addEventListener('click', function () {
    const currentCount = container.querySelectorAll('.option-input-group').length;
    if (currentCount >= MAX_OPTIONS) return;

    const newIndex = currentCount + 1;
    const group = document.createElement('div');
    group.className = 'option-input-group';
    group.innerHTML = `
      <span class="option-number-badge">${newIndex}</span>
      <input type="text" name="options[]" class="form-input" placeholder="Seçenek ${newIndex} metnini yazın" required maxlength="200" autocomplete="off">
      <button type="button" class="btn-remove-option" title="Seçeneği Sil">&times;</button>
    `;

    container.appendChild(group);

    const input = group.querySelector('input');
    if (input) input.focus();

    updateOptionState();
  });

  // Remove Option handler (Event Delegation)
  container.addEventListener('click', function (e) {
    if (e.target.closest('.btn-remove-option')) {
      const items = container.querySelectorAll('.option-input-group');
      if (items.length > MIN_OPTIONS) {
        const group = e.target.closest('.option-input-group');
        group.remove();
        updateOptionState();
      }
    }
  });

  // Initial state check
  updateOptionState();
});
