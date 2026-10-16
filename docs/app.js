/**
 * docs/app.js - debim-standards Interactive Catalog Explorer & 2D Visualizer
 */

let webData = {
  human_scale: [],
  regulations: [],
  materials: []
};

let currentMainTab = 'all';
let currentSubTab = 'all';

// Theme Management
function initTheme() {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light') {
    document.body.classList.add('light-theme');
    updateThemeIcon('light');
  } else {
    document.body.classList.remove('light-theme');
    updateThemeIcon('dark');
  }
}

function toggleTheme() {
  document.body.classList.toggle('light-theme');
  const isLight = document.body.classList.contains('light-theme');
  localStorage.setItem('theme', isLight ? 'light' : 'dark');
  updateThemeIcon(isLight ? 'light' : 'dark');
}

function updateThemeIcon(mode) {
  const btn = document.getElementById('themeToggleBtn');
  if (!btn) return;
  if (mode === 'light') {
    btn.innerHTML = `☀️ Light Mode`;
  } else {
    btn.innerHTML = `🌙 Dark Mode`;
  }
}

// Data Fetching
async function loadData() {
  try {
    const res = await fetch('./data.json');
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    webData = await res.json();
    updateStats();
    renderCatalog();
  } catch (err) {
    console.error('Error loading data.json:', err);
    document.getElementById('catalogGrid').innerHTML = `
      <div class="empty-state">
        <h3>⚠️ Unable to load catalog data</h3>
        <p>Please ensure <code>docs/data.json</code> was built using <code>python tools/build_web_data.py</code>.</p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem; color: var(--text-muted);">${err.message}</p>
      </div>
    `;
  }
}

function updateStats() {
  const furnitureCount = webData.human_scale ? webData.human_scale.length : 0;
  let clauseCount = 0;
  if (webData.regulations) {
    webData.regulations.forEach(r => clauseCount += (r.clauses ? r.clauses.length : 0));
  }
  const materialCount = webData.materials ? webData.materials.length : 0;

  const fElem = document.getElementById('statFurniture');
  const cElem = document.getElementById('statClauses');
  const mElem = document.getElementById('statMaterials');

  if (fElem) fElem.textContent = furnitureCount;
  if (cElem) cElem.textContent = clauseCount;
  if (mElem) mElem.textContent = materialCount;
}

// 2D Clearance Visualizer SVG Generator
function generateHumanScaleSVG(item) {
  const dims = item.dimensions || { width: 1.0, depth: 1.0, height: 1.0 };
  const clr = item.clearance || { front: 0.0, back: 0.0, left: 0.0, right: 0.0 };

  const fw = dims.width;
  const fd = dims.depth;
  const cLeft = clr.left;
  const cRight = clr.right;
  const cFront = clr.front;
  const cBack = clr.back;

  const totalWidth = fw + cLeft + cRight;
  const totalDepth = fd + cFront + cBack;

  // SVG viewBox setup
  const svgW = 280;
  const svgH = 180;
  const padding = 20;

  const availW = svgW - padding * 2;
  const availH = svgH - padding * 2;

  const scale = Math.min(availW / totalWidth, availH / totalDepth, 70);

  const drawnTotalW = totalWidth * scale;
  const drawnTotalD = totalDepth * scale;

  const originX = (svgW - drawnTotalW) / 2;
  const originY = (svgH - drawnTotalD) / 2;

  // Furniture footprint offset
  const furnX = originX + (cLeft * scale);
  const furnY = originY + (cBack * scale);
  const furnW = fw * scale;
  const furnD = fd * scale;

  // Custom details based on item category / tags
  let detailGraphics = '';
  const itemKey = (item.item_key || '').toUpperCase();
  const cat = (item.category || '').toLowerCase();

  if (cat === 'bedroom' && itemKey.includes('BED')) {
    // Bed pillows and mattress top view
    const pillowW = Math.min(0.45 * scale, furnW * 0.4);
    const pillowH = Math.min(0.3 * scale, furnD * 0.25);
    detailGraphics = `
      <rect x="${furnX + furnW * 0.08}" y="${furnY + furnD * 0.05}" width="${pillowW}" height="${pillowH}" rx="2" fill="var(--svg-footprint-stroke)" opacity="0.6"/>
      ${furnW > 1.2 * scale ? `<rect x="${furnX + furnW - pillowW - furnW * 0.08}" y="${furnY + furnD * 0.05}" width="${pillowW}" height="${pillowH}" rx="2" fill="var(--svg-footprint-stroke)" opacity="0.6"/>` : ''}
      <line x1="${furnX + 5}" y1="${furnY + furnD * 0.35}" x2="${furnX + furnW - 5}" y2="${furnY + furnD * 0.35}" stroke="var(--svg-footprint-stroke)" stroke-dasharray="2,2" opacity="0.8"/>
    `;
  } else if (cat === 'living' && itemKey.includes('SOFA')) {
    // Sofa cushions
    detailGraphics = `
      <rect x="${furnX + 3}" y="${furnY + 3}" width="${furnW - 6}" height="${furnD * 0.3}" rx="2" fill="var(--svg-footprint-stroke)" opacity="0.5"/>
    `;
  } else if (cat === 'dining' && itemKey.includes('TABLE')) {
    // Dining chairs around table
    detailGraphics = `
      <rect x="${furnX + furnW * 0.2}" y="${furnY + furnD * 0.2}" width="${furnW * 0.6}" height="${furnD * 0.6}" fill="none" stroke="var(--svg-footprint-stroke)" stroke-dasharray="2,2"/>
    `;
  } else if (cat === 'sanitary' && itemKey.includes('WATER_CLOSET')) {
    // WC bowl and tank
    detailGraphics = `
      <rect x="${furnX + furnW * 0.1}" y="${furnY + 2}" width="${furnW * 0.8}" height="${furnD * 0.3}" rx="2" fill="var(--svg-footprint-stroke)" opacity="0.7"/>
      <ellipse cx="${furnX + furnW / 2}" cy="${furnY + furnD * 0.65}" rx="${furnW * 0.38}" ry="${furnD * 0.28}" fill="none" stroke="var(--svg-text)" stroke-width="1.5"/>
    `;
  } else if (cat === 'circulation') {
    // Direction arrows
    detailGraphics = `
      <line x1="${furnX + furnW / 2}" y1="${furnY + 10}" x2="${furnX + furnW / 2}" y2="${furnY + furnD - 10}" stroke="var(--primary)" stroke-width="2" marker-end="url(#arrow)"/>
    `;
  }

  const clearanceText = `Clr: F ${cFront.toFixed(2)}m | L ${cLeft.toFixed(2)}m | R ${cRight.toFixed(2)}m`;

  return `
    <svg viewBox="0 0 ${svgW} ${svgH}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
          <path d="M 20 0 L 0 0 0 20" fill="none" stroke="var(--card-border)" stroke-width="0.5" opacity="0.3"/>
        </pattern>
        <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--primary)" />
        </marker>
      </defs>

      <rect width="${svgW}" height="${svgH}" fill="url(#grid)" />

      <!-- Outer Clearance Envelope -->
      <rect x="${originX}" y="${originY}" width="${drawnTotalW}" height="${drawnTotalD}"
            fill="var(--svg-clearance-fill)" stroke="var(--svg-clearance-stroke)"
            stroke-width="1.5" stroke-dasharray="4,3" rx="4"/>

      <!-- Inner Furniture Footprint -->
      <rect x="${furnX}" y="${furnY}" width="${furnW}" height="${furnD}"
            fill="var(--svg-footprint-fill)" stroke="var(--svg-footprint-stroke)"
            stroke-width="2" rx="3"/>

      ${detailGraphics}

      <!-- Dimension Footprint Text -->
      <text x="${furnX + furnW / 2}" y="${furnY + furnD / 2 + 4}" fill="var(--svg-text)"
            font-size="10" font-weight="bold" text-anchor="middle" font-family="sans-serif">
        ${fw.toFixed(2)} × ${fd.toFixed(2)}m
      </text>

      <!-- Envelope Area Label -->
      <text x="${svgW / 2}" y="${svgH - 8}" fill="var(--primary)"
            font-size="9.5" text-anchor="middle" font-family="sans-serif" font-weight="500">
        Total Envelope: ${item.total_space_area ? item.total_space_area.toFixed(2) : (totalWidth * totalDepth).toFixed(2)} sq.m
      </text>
    </svg>
  `;
}

function generateRegulationSVG(clause) {
  const cKey = (clause.clause_key || clause.clause_id || '').toUpperCase();

  let graphic = '';
  if (cKey.includes('CLAUSE_51') || cKey.includes('LIGHT') || cKey.includes('VENTILATION')) {
    graphic = `
      <rect x="50" y="30" width="180" height="110" fill="none" stroke="var(--accent-amber)" stroke-width="2" rx="4"/>
      <rect x="110" y="60" width="60" height="50" fill="var(--accent-amber-bg)" stroke="var(--accent-amber)" stroke-dasharray="3,3" rx="2"/>
      <text x="140" y="50" fill="var(--svg-text)" font-size="10" text-anchor="middle">Habitable Floor Area (100%)</text>
      <text x="140" y="88" fill="var(--accent-amber)" font-size="12" font-weight="bold" text-anchor="middle">≥ 10%</text>
      <text x="140" y="102" fill="var(--text-secondary)" font-size="9" text-anchor="middle">Light/Vent Window</text>
    `;
  } else if (cKey.includes('CLAUSE_22') || cKey.includes('STAIR')) {
    graphic = `
      <path d="M 50 130 L 90 130 L 90 105 L 130 105 L 130 80 L 170 80 L 170 55 L 210 55" fill="none" stroke="var(--primary)" stroke-width="3"/>
      <text x="110" y="122" fill="var(--accent-amber)" font-size="9">Tread ≥ 0.22m</text>
      <text x="135" y="95" fill="var(--accent-amber)" font-size="9">Riser ≤ 0.20m</text>
      <text x="130" y="40" fill="var(--svg-text)" font-size="10" text-anchor="middle">Clear Width ≥ 0.90m | Headroom ≥ 2.00m</text>
    `;
  } else if (cKey.includes('CLAUSE_33') || cKey.includes('CLEAR_HEIGHT')) {
    graphic = `
      <line x1="60" y1="40" x2="220" y2="40" stroke="var(--svg-text)" stroke-width="2"/>
      <line x1="60" y1="130" x2="220" y2="130" stroke="var(--svg-text)" stroke-width="2"/>
      <line x1="140" y1="45" x2="140" y2="125" stroke="var(--primary)" stroke-width="2" marker-end="url(#arrow)" marker-start="url(#arrow)"/>
      <text x="140" y="32" fill="var(--svg-text)" font-size="10" text-anchor="middle">Ceiling Level</text>
      <text x="180" y="90" fill="var(--primary)" font-size="11" font-weight="bold">≥ 2.60m</text>
      <text x="140" y="145" fill="var(--svg-text)" font-size="10" text-anchor="middle">Finished Floor Level</text>
    `;
  } else if (cKey.includes('CLAUSE_40') || cKey.includes('WET_AREA')) {
    graphic = `
      <path d="M 40 70 L 130 70 L 130 110 L 240 110" fill="none" stroke="var(--primary)" stroke-width="3"/>
      <text x="85" y="60" fill="var(--svg-text)" font-size="10" text-anchor="middle">Main Floor</text>
      <text x="185" y="100" fill="var(--svg-text)" font-size="10" text-anchor="middle">Wet Area Drop</text>
      <text x="135" y="132" fill="var(--accent-amber)" font-size="10" font-weight="bold" text-anchor="middle">Step Drop ≥ 0.10m</text>
    `;
  } else if (cKey.includes('SETBACK')) {
    graphic = `
      <line x1="50" y1="30" x2="50" y2="150" stroke="var(--accent-amber)" stroke-width="2" stroke-dasharray="4,4"/>
      <rect x="110" y="40" width="120" height="100" fill="var(--svg-footprint-fill)" stroke="var(--svg-footprint-stroke)" stroke-width="2"/>
      <line x1="50" y1="90" x2="110" y2="90" stroke="var(--primary)" stroke-width="2"/>
      <text x="50" y="20" fill="var(--accent-amber)" font-size="9" text-anchor="middle">Boundary Line</text>
      <text x="80" y="82" fill="var(--primary)" font-size="10" font-weight="bold" text-anchor="middle">Setback</text>
      <text x="80" y="105" fill="var(--svg-text)" font-size="9" text-anchor="middle">0.50m - 2.00m</text>
    `;
  } else {
    graphic = `
      <rect x="40" y="30" width="200" height="110" fill="none" stroke="var(--primary)" stroke-width="2" rx="4"/>
      <text x="140" y="90" fill="var(--primary)" font-size="12" font-weight="bold" text-anchor="middle">Regulation Standard</text>
    `;
  }

  return `
    <svg viewBox="0 0 280 180" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
      <rect width="280" height="180" fill="var(--svg-bg)"/>
      ${graphic}
    </svg>
  `;
}

function generateMaterialSVG(item) {
  const cat = (item.category || '').toLowerCase();
  let icon = '📦';
  if (cat === 'structural') icon = '🏗️';
  else if (cat === 'masonry') icon = '🧱';
  else if (cat === 'finish') icon = '🪵';
  else if (cat === 'opening') icon = '🚪';
  else if (cat === 'roofing') icon = '🏠';

  return `
    <svg viewBox="0 0 280 180" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
      <rect width="280" height="180" fill="var(--svg-bg)"/>
      <circle cx="140" cy="75" r="36" fill="var(--primary-bg)" stroke="var(--primary)" stroke-width="1.5"/>
      <text x="140" y="86" font-size="32" text-anchor="middle">${icon}</text>
      <text x="140" y="135" fill="var(--svg-text)" font-size="12" font-weight="bold" text-anchor="middle">${item.unit ? `Unit: ${item.unit}` : 'Material Spec'}</text>
      <text x="140" y="152" fill="var(--primary)" font-size="10" text-anchor="middle">${item.catalogs ? item.catalogs.join(' • ') : ''}</text>
    </svg>
  `;
}

// Render Grid Cards
function renderCatalog() {
  const grid = document.getElementById('catalogGrid');
  const query = (document.getElementById('searchInput').value || '').toLowerCase().trim();

  let itemsToRender = [];

  // Filter Human Scale
  if (currentMainTab === 'all' || currentMainTab === 'human_scale') {
    (webData.human_scale || []).forEach(item => {
      const subMatch = currentSubTab === 'all' || (item.category || '').toLowerCase() === currentSubTab;
      if (subMatch) {
        itemsToRender.push({ type: 'human_scale', data: item });
      }
    });
  }

  // Filter Regulations
  if ((currentMainTab === 'all' || currentMainTab === 'regulations') && currentSubTab === 'all') {
    (webData.regulations || []).forEach(ruleset => {
      (ruleset.clauses || []).forEach(clause => {
        itemsToRender.push({ type: 'regulation', data: clause });
      });
    });
  }

  // Filter Materials
  if ((currentMainTab === 'all' || currentMainTab === 'materials') && currentSubTab === 'all') {
    (webData.materials || []).forEach(mat => {
      itemsToRender.push({ type: 'material', data: mat });
    });
  }

  // Query Filter
  if (query) {
    itemsToRender = itemsToRender.filter(entry => {
      const d = entry.data;
      const matchText = [
        d.name || '',
        d.name_en || '',
        d.title || '',
        d.title_en || '',
        d.id || '',
        d.clause_id || '',
        d.category || '',
        d.specification || '',
        d.description || '',
        d.reference || '',
        ...(d.tags || [])
      ].join(' ').toLowerCase();

      return matchText.includes(query);
    });
  }

  if (itemsToRender.length === 0) {
    grid.innerHTML = `
      <div class="empty-state">
        <p style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">🔍 ไม่พบรายการข้อมูลที่ตรงกับเงื่อนไข</p>
        <p>ลองเปลี่ยนคำค้นหา หรือเลือกหมวดหมู่อื่นในแถบเมนูข้างต้น</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = itemsToRender.map(entry => {
    if (entry.type === 'human_scale') {
      const d = entry.data;
      const dims = d.dimensions || {};
      const clr = d.clearance || {};
      return `
        <div class="card">
          <div class="card-header">
            <div class="card-titles">
              <div class="card-title">${d.name}</div>
              <div class="card-subtitle">${d.name_en}</div>
              <div class="card-id-badge">${d.id}</div>
            </div>
            <span class="category-tag">${d.category}</span>
          </div>

          <div class="diagram-box">
            ${generateHumanScaleSVG(d)}
          </div>

          <table class="metrics-table">
            <tr><td>มิติชิ้นงาน (W×D×H):</td><td class="metric-val">${dims.width} × ${dims.depth} × ${dims.height} ม.</td></tr>
            <tr><td>ระยะ Clearance หน้า/หลัง:</td><td class="metric-val">${clr.front} / ${clr.back} ม.</td></tr>
            <tr><td>ระยะ Clearance ซ้าย/ขวา:</td><td class="metric-val">${clr.left} / ${clr.right} ม.</td></tr>
            <tr><td>พื้นที่ Footprint สุทธิ:</td><td class="metric-val">${d.footprint_area} ตร.ม.</td></tr>
            <tr><td>พื้นที่ซองการใช้งานรวม:</td><td class="metric-val">${d.total_space_area} ตร.ม.</td></tr>
          </table>

          <div style="margin-top: 0.75rem; font-size: 0.75rem; color: var(--text-muted);">
            <strong>อ้างอิง:</strong> ${d.reference || 'Neufert & Panero'}
          </div>

          ${d.tags ? `<div class="tags-row">${d.tags.map(t => `<span class="tag-item">#${t}</span>`).join('')}</div>` : ''}
        </div>
      `;
    } else if (entry.type === 'regulation') {
      const c = entry.data;
      const metrics = c.metrics || [];
      return `
        <div class="card">
          <div class="card-header">
            <div class="card-titles">
              <div class="card-title">${c.title}</div>
              <div class="card-subtitle">${c.title_en}</div>
              <div class="card-id-badge">${c.clause_id} • ${c.regulation_id}</div>
            </div>
            <span class="category-tag regulation">MR 55 Code</span>
          </div>

          <div class="diagram-box">
            ${generateRegulationSVG(c)}
          </div>

          <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.75rem;">
            ${c.description}
          </p>

          <table class="metrics-table">
            ${metrics.map(m => `
              <tr>
                <td>${m.name} (${m.parameter}):</td>
                <td class="metric-val">${m.operator} ${m.threshold} ${m.unit}</td>
              </tr>
            `).join('')}
          </table>

          ${metrics.some(m => m.remediation) ? `
            <div class="remediation-box">
              <div class="remediation-title">🛠️ ข้อแนะนำการแก้ไข (Remediation)</div>
              ${metrics.map(m => m.remediation ? `<div class="remediation-text">• ${m.remediation.message_th}</div>` : '').join('')}
            </div>
          ` : ''}

          <div style="margin-top: 0.75rem; font-size: 0.75rem; color: var(--text-muted);">
            <strong>อ้างอิงกฎหมาย:</strong> ${c.reference}
          </div>
        </div>
      `;
    } else if (entry.type === 'material') {
      const m = entry.data;
      const cost = m.cost;
      const carbon = m.carbon;
      return `
        <div class="card">
          <div class="card-header">
            <div class="card-titles">
              <div class="card-title">${m.name}</div>
              <div class="card-subtitle">${m.name_en}</div>
              <div class="card-id-badge">${m.id}</div>
            </div>
            <span class="category-tag material">${m.category}</span>
          </div>

          <div class="diagram-box">
            ${generateMaterialSVG(m)}
          </div>

          <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
            ${m.specification || 'ไม่มีข้อกำหนดสเปกเพิ่มเติม'}
          </p>

          ${cost ? `
            <div class="cost-breakdown">
              <div class="cost-box">
                <div class="cost-label">ค่าวัสดุ</div>
                <div class="cost-amount">฿${cost.material_price.toLocaleString()}</div>
              </div>
              <div class="cost-box">
                <div class="cost-label">ค่าแรง</div>
                <div class="cost-amount">฿${cost.labor_price.toLocaleString()}</div>
              </div>
              <div class="cost-box" style="border-color: var(--primary);">
                <div class="cost-label">ราคารวม/หน่วย</div>
                <div class="cost-amount" style="color: var(--primary);">฿${cost.total_price.toLocaleString()}</div>
              </div>
            </div>
          ` : ''}

          ${carbon ? `
            <div class="carbon-badge">
              <span>🌱 Embodied Carbon:</span>
              <span>${carbon.embodied_carbon} kgCO₂e / ${carbon.unit}</span>
            </div>
          ` : ''}

          ${m.tags ? `<div class="tags-row">${m.tags.map(t => `<span class="tag-item">#${t}</span>`).join('')}</div>` : ''}
        </div>
      `;
    }
  }).join('');
}

// Event Listeners & Tab Controls
function switchMainTab(category) {
  currentMainTab = category;
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === category);
  });

  const subNav = document.getElementById('subTabsNav');
  if (category === 'human_scale' || category === 'all') {
    subNav.style.display = 'flex';
  } else {
    subNav.style.display = 'none';
  }

  renderCatalog();
}

function switchSubTab(subCategory) {
  currentSubTab = subCategory;
  document.querySelectorAll('.sub-tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.subtab === subCategory);
  });
  renderCatalog();
}

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  loadData();

  document.getElementById('themeToggleBtn').addEventListener('click', toggleTheme);

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => switchMainTab(btn.dataset.tab));
  });

  document.querySelectorAll('.sub-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => switchSubTab(btn.dataset.subtab));
  });

  document.getElementById('searchInput').addEventListener('input', renderCatalog);
});
