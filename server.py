#!/usr/bin/env python3
"""
Spark 8 Label Generator — Web Server (V3 — Clean Compliance)
"""

import http.server
import json
import os
import urllib.parse
from generate_label import generate_label

PORT = int(os.environ.get("PORT", 8090))
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_DIR, "generated_labels")
os.makedirs(OUTPUT_DIR, exist_ok=True)

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Spark 8 — Label Generator</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #080808;
    color: #ccc;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    padding: 32px 16px;
  }

  .container { width: 100%; max-width: 500px; }

  .header {
    text-align: center;
    margin-bottom: 24px;
  }
  .header h1 {
    font-size: 22px;
    font-weight: 700;
    color: #CC0000;
    letter-spacing: 3px;
  }
  .header p {
    color: #444;
    font-size: 12px;
    margin-top: 2px;
    letter-spacing: 1px;
  }

  .card {
    background: #111;
    border: 1px solid #1e1e1e;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 12px;
  }

  .card-title {
    font-size: 10px;
    font-weight: 600;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 14px;
  }

  .field { margin-bottom: 12px; }
  .field:last-child { margin-bottom: 0; }

  label {
    display: block;
    font-size: 11px;
    font-weight: 600;
    color: #666;
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  input, select {
    width: 100%;
    padding: 9px 10px;
    background: #0a0a0a;
    border: 1px solid #252525;
    border-radius: 5px;
    color: #eee;
    font-size: 14px;
    font-family: inherit;
    transition: border-color 0.2s;
    -webkit-appearance: none;
    appearance: none;
  }
  input:focus, select:focus {
    outline: none;
    border-color: #CC0000;
  }
  input::placeholder { color: #333; }

  select {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath d='M2 4l4 4 4-4' fill='none' stroke='%23666' stroke-width='1.5'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 10px center;
    padding-right: 28px;
    cursor: pointer;
  }
  select option { background: #111; color: #eee; }

  .row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  .row-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 6px;
  }

  .btn {
    width: 100%;
    padding: 12px;
    background: #CC0000;
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-top: 4px;
  }
  .btn:hover { background: #ee2222; }
  .btn:active { transform: scale(0.98); }
  .btn:disabled { background: #333; color: #555; cursor: not-allowed; }

  .status {
    text-align: center;
    margin-top: 10px;
    font-size: 11px;
    min-height: 16px;
    letter-spacing: 0.5px;
  }
  .status.success { color: #CC0000; }
  .status.error { color: #AA4444; }
  .status.loading { color: #666; }

  /* Product type buttons */
  .type-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 5px;
  }
  .type-btn {
    padding: 7px 2px;
    background: #0a0a0a;
    border: 1px solid #252525;
    border-radius: 5px;
    color: #666;
    font-size: 9px;
    font-weight: 600;
    cursor: pointer;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    transition: all 0.15s;
  }
  .type-btn:hover { border-color: #444; color: #999; }
  .type-btn.active {
    border-color: #CC0000;
    color: #CC0000;
    background: #1a0808;
  }

  /* Size buttons */
  .size-btn {
    padding: 8px 4px;
    background: #0a0a0a;
    border: 1px solid #252525;
    border-radius: 5px;
    color: #666;
    font-size: 10px;
    font-weight: 600;
    cursor: pointer;
    text-align: center;
    transition: all 0.15s;
  }
  .size-btn:hover { border-color: #444; color: #999; }
  .size-btn.active {
    border-color: #CC0000;
    color: #CC0000;
    background: #1a0808;
  }
  .size-desc {
    font-size: 8px;
    font-weight: 400;
    color: #444;
    display: block;
    margin-top: 2px;
  }

  /* History */
  .history-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 10px;
    background: #0a0a0a;
    border: 1px solid #1a1a1a;
    border-radius: 5px;
    margin-bottom: 5px;
    font-size: 12px;
  }
  .history-item .strain { color: #CC0000; font-weight: 600; }
  .history-item .meta { color: #444; font-size: 10px; margin-top: 1px; }
  .history-item a {
    color: #888;
    text-decoration: none;
    font-weight: 600;
    font-size: 10px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    border: 1px solid #333;
    padding: 3px 8px;
    border-radius: 3px;
    transition: all 0.2s;
  }
  .history-item a:hover { color: #CC0000; border-color: #CC0000; }

  .empty-state {
    color: #2a2a2a;
    font-size: 12px;
    text-align: center;
    padding: 16px;
  }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <img src="/logo" alt="Spark 8" style="height:60px; margin-bottom:8px;">
    <h1>SPARK 8</h1>
    <p>THCa Product Label Generator</p>
  </div>

  <form id="labelForm">

    <!-- Label Size -->
    <div class="card">
      <div class="card-title">Label Size</div>
      <div class="row-3" id="sizeGrid">
        <button type="button" class="size-btn" data-size="small">
          Small<span class="size-desc">2 × 1 in</span>
        </button>
        <button type="button" class="size-btn active" data-size="medium">
          Medium<span class="size-desc">3 × 2 in</span>
        </button>
        <button type="button" class="size-btn" data-size="large">
          Large<span class="size-desc">4 × 3 in</span>
        </button>
      </div>
    </div>

    <!-- Product Type -->
    <div class="card">
      <div class="card-title">Product Type</div>
      <div class="type-grid" id="typeGrid">
        <button type="button" class="type-btn active" data-type="cartridge">Cartridge</button>
        <button type="button" class="type-btn" data-type="disposable">Disposable</button>
        <button type="button" class="type-btn" data-type="gummies">Gummies</button>
        <button type="button" class="type-btn" data-type="preroll">Pre-Roll</button>
        <button type="button" class="type-btn" data-type="flower">Flower</button>
        <button type="button" class="type-btn" data-type="concentrate">Concentrate</button>
        <button type="button" class="type-btn" data-type="tincture">Tincture</button>
        <button type="button" class="type-btn" data-type="edible">Edible</button>
      </div>
    </div>

    <!-- Product Details -->
    <div class="card">
      <div class="card-title">Product Details</div>

      <div class="field">
        <label for="strain">Strain Name</label>
        <input type="text" id="strain" name="strain" placeholder="e.g. Blue Dream" required>
      </div>

      <div class="row">
        <div class="field">
          <label for="thc_mg">THCa Amount</label>
          <select id="thc_mg">
            <option value="5">5 mg</option>
            <option value="10">10 mg</option>
            <option value="15">15 mg</option>
            <option value="20">20 mg</option>
            <option value="25" selected>25 mg</option>
            <option value="30">30 mg</option>
            <option value="35">35 mg</option>
            <option value="40">40 mg</option>
            <option value="50">50 mg</option>
            <option value="75">75 mg</option>
            <option value="100">100 mg</option>
            <option value="150">150 mg</option>
            <option value="200">200 mg</option>
            <option value="250">250 mg</option>
            <option value="500">500 mg</option>
            <option value="1000">1000 mg</option>
          </select>
        </div>
        <div class="field">
          <label for="serving_size">Serving Size</label>
          <select id="serving_size"></select>
        </div>
      </div>

      <div class="row">
        <div class="field">
          <label for="batch">Batch Number</label>
          <input type="text" id="batch" placeholder="e.g. BT-2026-001" required>
        </div>
        <div class="field">
          <label for="exp_date">Expiration</label>
          <select id="exp_date"></select>
        </div>
      </div>

      <button type="submit" class="btn" id="submitBtn">Generate Label</button>
      <div class="status" id="status"></div>
    </div>
  </form>

  <div class="card">
    <div class="card-title">Generated Labels</div>
    <div id="history"><div class="empty-state">No labels yet</div></div>
  </div>
</div>

<script>
const servingSizes = {
  cartridge: ['1 cartridge (0.5g)', '1 cartridge (1g)', '1 cartridge (2g)'],
  disposable: ['1 device (0.5g)', '1 device (1g)', '1 device (2g)', '1 device (3g)'],
  gummies: ['1 gummy', '2 gummies', '1 piece (10mg)', '1 piece (25mg)', '1 piece (50mg)'],
  preroll: ['1 pre-roll (0.5g)', '1 pre-roll (1g)', '1 pre-roll (1.5g)', '1 pre-roll (2g)'],
  flower: ['1g', '3.5g (1/8 oz)', '7g (1/4 oz)', '14g (1/2 oz)', '28g (1 oz)'],
  concentrate: ['1 dab (0.05g)', '0.5g container', '1g container', '2g container'],
  tincture: ['1 mL (1 dropper)', '0.5 mL (1/2 dropper)', '2 mL (2 droppers)'],
  edible: ['1 piece', '2 pieces', '1 serving (10mg)', '1 serving (25mg)', '1 serving (50mg)'],
};

let selectedType = 'cartridge';
let selectedSize = 'medium';
let labels = [];

const form = document.getElementById('labelForm');
const status = document.getElementById('status');
const history = document.getElementById('history');
const submitBtn = document.getElementById('submitBtn');
const servingSelect = document.getElementById('serving_size');
const expSelect = document.getElementById('exp_date');

function updateServings(type) {
  const opts = servingSizes[type] || servingSizes.cartridge;
  servingSelect.innerHTML = opts.map((s, i) =>
    `<option value="${s}" ${i === 0 ? 'selected' : ''}>${s}</option>`
  ).join('');
}

function populateExpDates() {
  const now = new Date();
  const months = ['01','02','03','04','05','06','07','08','09','10','11','12'];
  const names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  let html = '';
  for (let i = 6; i <= 30; i++) {
    const d = new Date(now.getFullYear(), now.getMonth() + i, 1);
    html += `<option value="${months[d.getMonth()]}/${d.getFullYear()}">${names[d.getMonth()]} ${d.getFullYear()}</option>`;
  }
  expSelect.innerHTML = html;
}

// Product type buttons
document.getElementById('typeGrid').addEventListener('click', (e) => {
  const btn = e.target.closest('.type-btn');
  if (!btn) return;
  document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  selectedType = btn.dataset.type;
  updateServings(selectedType);
});

// Size buttons
document.getElementById('sizeGrid').addEventListener('click', (e) => {
  const btn = e.target.closest('.size-btn');
  if (!btn) return;
  document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  selectedSize = btn.dataset.size;
});

updateServings('cartridge');
populateExpDates();

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  status.className = 'status loading';
  status.textContent = 'Generating...';
  submitBtn.disabled = true;

  const data = {
    strain: document.getElementById('strain').value.trim(),
    thc_mg: document.getElementById('thc_mg').value,
    serving_size: servingSelect.value,
    batch: document.getElementById('batch').value.trim(),
    exp_date: expSelect.value,
    product_type: selectedType,
    label_size: selectedSize,
  };

  try {
    const res = await fetch('/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    const result = await res.json();
    if (result.success) {
      status.className = 'status success';
      status.textContent = 'Label ready!';
      labels.unshift({ ...data, filename: result.filename });
      renderHistory();
      window.open('/download/' + encodeURIComponent(result.filename), '_blank');
    } else {
      status.className = 'status error';
      status.textContent = result.error;
    }
  } catch (err) {
    status.className = 'status error';
    status.textContent = 'Connection error';
  }
  submitBtn.disabled = false;
});

function renderHistory() {
  if (!labels.length) return;
  history.innerHTML = labels.map(l => `
    <div class="history-item">
      <div>
        <div class="strain">${l.strain}</div>
        <div class="meta">${l.thc_mg}mg · ${l.product_type} · ${l.label_size} · ${l.batch}</div>
      </div>
      <a href="/download/${encodeURIComponent(l.filename)}" target="_blank">PDF</a>
    </div>
  `).join('');
}
</script>
</body>
</html>
"""


class LabelHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
        elif self.path == '/logo':
            logo_path = os.path.join(PROJECT_DIR, 'spark8-logo.png')
            if os.path.exists(logo_path):
                self.send_response(200)
                self.send_header('Content-Type', 'image/png')
                self.end_headers()
                with open(logo_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404)
        elif self.path.startswith('/download/'):
            filename = urllib.parse.unquote(self.path[10:])
            filepath = os.path.join(OUTPUT_DIR, filename)
            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header('Content-Type', 'application/pdf')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.end_headers()
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/generate':
            length = int(self.headers['Content-Length'])
            body = json.loads(self.rfile.read(length))
            try:
                strain = body.get('strain', 'Unknown')
                safe_strain = strain.replace(' ', '_').replace('/', '-')
                batch = body.get('batch', 'BATCH')
                label_size = body.get('label_size', 'medium')
                filename = f"label_{safe_strain}_{batch}_{label_size}.pdf"
                out_path = os.path.join(OUTPUT_DIR, filename)

                generate_label(
                    strain=strain,
                    thc_mg=body.get('thc_mg', '25'),
                    serving_size=body.get('serving_size', ''),
                    batch=batch,
                    exp_date=body.get('exp_date', ''),
                    product_type=body.get('product_type', 'cartridge'),
                    label_size=label_size,
                    output_file=out_path,
                )

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'filename': filename}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        print(f"  [{self.log_date_time_string()}] {args[0]}")


if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', PORT), LabelHandler)
    print(f"\n  SPARK 8 Label Generator")
    print(f"  Open: http://localhost:{PORT}")
    print(f"  Labels: {OUTPUT_DIR}/\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
