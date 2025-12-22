// Tab switching
function showTab(tabName) {
  // Hide all tabs
  document.querySelectorAll('.tab-content').forEach(tab => {
    tab.classList.remove('active');
  });
  
  // Remove active from all buttons
  document.querySelectorAll('.tab-button').forEach(btn => {
    btn.classList.remove('active');
  });
  
  // Show target tab
  const targetTab = document.getElementById('tab-' + tabName);
  if (targetTab) {
    targetTab.classList.add('active');
  }
  
  // Activate correct button
  const buttons = document.querySelectorAll('.tab-button');
  buttons.forEach(btn => {
    if ((tabName === 'input' && (btn.textContent.includes('Data Jalan') || btn.textContent.includes('Data Jurnal'))) ||
        (tabName === 'parameters' && btn.textContent.includes('Parameter')) ||
        (tabName === 'results' && btn.textContent.includes('Hasil'))) {
      btn.classList.add('active');
    }
  });
}

// Auto-switch to results tab if exists
document.addEventListener('DOMContentLoaded', () => {
  const resultsTab = document.getElementById('tab-results');
  if (resultsTab) {
    setTimeout(() => {
      document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
      });
      
      document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
      });
      
      resultsTab.classList.add('active');
      
      const tabButtons = document.querySelectorAll('.tab-button');
      tabButtons.forEach(btn => {
        if (btn.textContent.includes('Hasil')) {
          btn.classList.add('active');
        }
      });
      
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 200);
  }
});
