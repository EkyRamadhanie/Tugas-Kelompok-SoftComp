// Tab switching
function showTab(tabName) {
  document.querySelectorAll('.tab-content').forEach(tab => {
    tab.classList.remove('active');
  });
  document.querySelectorAll('.tab-button').forEach(btn => {
    btn.classList.remove('active');
  });
  
  const targetTab = document.getElementById('tab-' + tabName);
  if (targetTab) {
    targetTab.classList.add('active');
  }
  
  if (event && event.target) {
    event.target.classList.add('active');
  }
}

// Switch between Form and CSV input modes
function showInputMode(mode) {
  const formMode = document.getElementById('input-form-mode');
  const csvMode = document.getElementById('input-csv-mode');
  const btnForm = document.getElementById('btn-form');
  const btnCsv = document.getElementById('btn-csv');
  
  if (mode === 'form') {
    formMode.style.display = 'block';
    csvMode.style.display = 'none';
    btnForm.classList.add('active');
    btnCsv.classList.remove('active');
  } else {
    formMode.style.display = 'none';
    csvMode.style.display = 'block';
    btnForm.classList.remove('active');
    btnCsv.classList.add('active');
  }
}

// Add new distress row
function addDistressRow() {
  const container = document.getElementById('distress-inputs');
  const rowCount = container.children.length + 1;
  const newRow = document.createElement('div');
  newRow.className = 'input-row';
  newRow.innerHTML = `
    <input type="text" placeholder="ID (D${rowCount})" class="d-id">
    <input type="number" placeholder="Lokasi (meter)" class="d-loc">
    <input type="number" placeholder="Deduction" class="d-ded">
    <input type="number" placeholder="Biaya Lokal" class="d-cost">
    <button type="button" onclick="removeRow(this)" class="btn-remove">✕</button>
  `;
  container.appendChild(newRow);
}

// Add new segment row
function addSegmentRow() {
  const container = document.getElementById('segment-inputs');
  const rowCount = container.children.length + 1;
  const newRow = document.createElement('div');
  newRow.className = 'input-row';
  newRow.innerHTML = `
    <input type="text" placeholder="ID (S${rowCount})" class="s-id">
    <input type="number" placeholder="Start (m)" class="s-start">
    <input type="number" placeholder="End (m)" class="s-end">
    <input type="number" placeholder="Biaya Resurfacing" class="s-cost">
    <button type="button" onclick="removeRow(this)" class="btn-remove">✕</button>
  `;
  container.appendChild(newRow);
}

// Remove a row
function removeRow(button) {
  button.parentElement.remove();
}

// Populate form from CSV (untuk restore data setelah submit)
function csvToForm(distressCSV, segmentCSV) {
  if (!distressCSV || !segmentCSV) return;
  
  // Parse distress CSV
  const distressLines = distressCSV.trim().split('\n');
  if (distressLines.length > 1) {
    const distressContainer = document.getElementById('distress-inputs');
    distressContainer.innerHTML = ''; // Clear existing rows
    
    for (let i = 1; i < distressLines.length; i++) {
      const parts = distressLines[i].split(',');
      if (parts.length === 4) {
        const newRow = document.createElement('div');
        newRow.className = 'input-row';
        newRow.innerHTML = `
          <input type="text" placeholder="ID (D${i})" class="d-id" value="${parts[0].trim()}">
          <input type="number" placeholder="Lokasi (meter)" class="d-loc" value="${parts[1].trim()}">
          <input type="number" placeholder="Deduction" class="d-ded" value="${parts[2].trim()}">
          <input type="number" placeholder="Biaya Lokal" class="d-cost" value="${parts[3].trim()}">
          <button type="button" onclick="removeRow(this)" class="btn-remove">✕</button>
        `;
        distressContainer.appendChild(newRow);
      }
    }
  }
  
  // Parse segment CSV
  const segmentLines = segmentCSV.trim().split('\n');
  if (segmentLines.length > 1) {
    const segmentContainer = document.getElementById('segment-inputs');
    segmentContainer.innerHTML = ''; // Clear existing rows
    
    for (let i = 1; i < segmentLines.length; i++) {
      const parts = segmentLines[i].split(',');
      if (parts.length === 4) {
        const newRow = document.createElement('div');
        newRow.className = 'input-row';
        newRow.innerHTML = `
          <input type="text" placeholder="ID (S${i})" class="s-id" value="${parts[0].trim()}">
          <input type="number" placeholder="Start (m)" class="s-start" value="${parts[1].trim()}">
          <input type="number" placeholder="End (m)" class="s-end" value="${parts[2].trim()}">
          <input type="number" placeholder="Biaya Resurfacing" class="s-cost" value="${parts[3].trim()}">
          <button type="button" onclick="removeRow(this)" class="btn-remove">✕</button>
        `;
        segmentContainer.appendChild(newRow);
      }
    }
  }
}

// Convert form inputs to CSV
function formToCSV() {
  // Convert distress form to CSV
  const distressRows = document.querySelectorAll('#distress-inputs .input-row');
  let distressCSV = 'id,location_m,deduction,cost_local\n';
  let distressCount = 0;
  
  distressRows.forEach(row => {
    const id = row.querySelector('.d-id').value.trim();
    const loc = row.querySelector('.d-loc').value.trim();
    const ded = row.querySelector('.d-ded').value.trim();
    const cost = row.querySelector('.d-cost').value.trim();
    
    if (id && loc && ded && cost) {
      distressCSV += `${id},${loc},${ded},${cost}\n`;
      distressCount += 1;
    }
  });
  
  // Convert segment form to CSV
  const segmentRows = document.querySelectorAll('#segment-inputs .input-row');
  let segmentCSV = 'id,start_m,end_m,cost_resurfacing\n';
  let segmentCount = 0;
  
  segmentRows.forEach(row => {
    const id = row.querySelector('.s-id').value.trim();
    const start = row.querySelector('.s-start').value.trim();
    const end = row.querySelector('.s-end').value.trim();
    const cost = row.querySelector('.s-cost').value.trim();
    
    if (id && start && end && cost) {
      segmentCSV += `${id},${start},${end},${cost}\n`;
      segmentCount += 1;
    }
  });
  
  return { distressCSV, segmentCSV, distressCount, segmentCount };
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  // Form submission handler
  const form = document.getElementById('ga-form');
  if (!form) {
    return;
  }
  
  form.addEventListener('submit', function(e) {
    const btnForm = document.getElementById('btn-form');
    const isFormMode = btnForm && btnForm.classList.contains('active');
    
    if (isFormMode) {
      // Form mode: convert to CSV
      const { distressCSV, segmentCSV, distressCount, segmentCount } = formToCSV();

      // Client-side validation: need at least 1 distress and 1 segment
      const errorBox = document.getElementById('client-error');
      if (errorBox) {
        errorBox.style.display = 'none';
      }
      if (distressCount === 0 || segmentCount === 0) {
        if (errorBox) {
          errorBox.style.display = 'block';
          errorBox.querySelector('.msg').textContent = 'Isi minimal 1 baris kerusakan dan 1 baris segmen sebelum menjalankan analisis.';
        }
        e.preventDefault();
        return;
      }
      
      const distressInput = document.querySelector('input[name="distress_csv"]');
      const segmentInput = document.querySelector('input[name="segment_csv"]');
      
      if (distressInput && segmentInput) {
        distressInput.value = distressCSV;
        segmentInput.value = segmentCSV;
      }
    } else {
      // CSV mode: use textarea values
      const distressTextarea = document.querySelector('textarea[name="distress_csv_text"]');
      const segmentTextarea = document.querySelector('textarea[name="segment_csv_text"]');
      
      if (distressTextarea && segmentTextarea) {
        const distressInput = document.querySelector('input[name="distress_csv"]');
        const segmentInput = document.querySelector('input[name="segment_csv"]');
        
        if (distressInput && segmentInput) {
          distressInput.value = distressTextarea.value;
          segmentInput.value = segmentTextarea.value;
        }
      }
    }
    
    // Show loading indicator
    const loading = document.getElementById('loading');
    if (loading) {
      loading.classList.add('active');
    }
  });
  
  // Auto-switch to results tab if results exist
  const resultsTab = document.getElementById('tab-results');
  if (resultsTab) {
    // Results exist, switch to results tab automatically
    setTimeout(() => {
      // Hide all tabs
      document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
      });
      
      // Remove active from all buttons
      document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
      });
      
      // Show results tab
      resultsTab.classList.add('active');
      
      // Activate results button
      const tabButtons = document.querySelectorAll('.tab-button');
      tabButtons.forEach(btn => {
        if (btn.textContent.includes('Hasil')) {
          btn.classList.add('active');
        }
      });
      
      // Scroll to top smoothly
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 200);
  }
  
  // Restore form data from CSV if exists
  const distressTextarea = document.querySelector('textarea[name="distress_csv_text"]');
  const segmentTextarea = document.querySelector('textarea[name="segment_csv_text"]');
  if (distressTextarea && segmentTextarea) {
    const distressCSV = distressTextarea.value;
    const segmentCSV = segmentTextarea.value;
    if (distressCSV && segmentCSV) {
      csvToForm(distressCSV, segmentCSV);
    }
  }
});
