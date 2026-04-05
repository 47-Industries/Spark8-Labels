<div align="center">

# Spark8-Labels

**THCa compliance label generator for Spark 8 products**

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)
![ReportLab](https://img.shields.io/badge/ReportLab-PDF-red?style=flat-square)
![Railway](https://img.shields.io/badge/Railway-deployed-0B0D0E?style=flat-square&logo=railway&logoColor=white)

Single-page web app &bull; PDF generation &bull; QR codes &bull; Batch tracking &bull; Florida hemp compliance

</div>

---

Web-based label generator built for **Spark 8** (smoke shop and lounge, Tampa Bay FL). Generates print-ready THCa product compliance labels as PDFs with batch tracking, QR codes, strain information, and full Florida hemp regulation text. Dark-themed UI designed for fast in-store label production.

| | |
|---|---|
| **Status** | Production |
| **Client** | Spark 8 |
| **Developer** | 47 Industries LLC |
| **Platform** | Web |
| **Tech** | Python, ReportLab, qrcode, HTTP server |
| **Deployment** | Railway |

## Repository Structure

```
Spark8-Labels/
├── server.py              # HTTP server + embedded web UI
├── generate_label.py      # PDF label generation engine
├── spark8-logo.png        # Brand logo asset
├── requirements.txt       # Python dependencies
├── Procfile               # Railway deployment config
└── generated_labels/      # Output directory (gitignored)
```

## Features

### Label Generation
- Three label sizes: Small (2x1 in), Medium (3x2 in), Large (4x3 in)
- Eight product types: Cartridge, Disposable, Gummies, Pre-Roll, Flower, Concentrate, Tincture, Edible
- Strain name, type (Sativa/Indica/Hybrid), and weight
- THCa amount per serving with configurable serving sizes
- Batch number and expiration date tracking
- QR code linking to shopspark8.com
- THCa compliance warning triangle symbol

### Compliance
- Florida Rule 5K-4.034 compliant label text
- 2018 Farm Bill / <0.3% Delta-9 THC disclosure
- Age restriction warnings (21+)
- FDA disclaimer
- Keep out of reach warnings

### Web Interface
- Dark-themed single-page UI with Spark 8 branding
- Product type and label size selection via button grids
- Dynamic serving size options based on product type
- Auto-populated expiration date dropdown (6-60 months out)
- Label generation history with direct PDF download links
- Mobile-responsive layout

### Security
- Rate limiting (20 requests/minute per IP)
- Input sanitization on all fields
- Path traversal protection on file downloads
- Payload size limits (4KB max)
- Security headers (CSP, X-Frame-Options, XSS protection)

## Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
git clone <repo-url>
cd Spark8-Labels
pip install -r requirements.txt
```

### Run Locally

```bash
python3 server.py
```

Open `http://localhost:8090` in your browser.

### CLI Usage

Generate labels directly from the command line:

```bash
python3 generate_label.py \
  --strain "Blue Dream" \
  --thca 25 \
  --serving "1 cartridge (0.5g)" \
  --batch "BT-2026-001" \
  --exp "08/2027" \
  --type cartridge \
  --size medium \
  --strain-type Hybrid \
  --weight 3.5g
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8090` | Server port |

## Deployment

Deployed to **Railway** via Procfile:

```
web: python3 server.py
```

## License

Proprietary -- 47 Industries LLC. All rights reserved.

## Contact

**47 Industries LLC**
[47industries.com](https://47industries.com) | hello@47industries.com
