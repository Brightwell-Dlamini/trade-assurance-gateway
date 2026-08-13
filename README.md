# Trade Assurance Gateway

**Fully working MVP for the AfCFTA Digital Innovation Challenge (2nd Edition)**  
**Version 1.0.0**

**Theme:** Realizing the AfCFTA for MSMEs through Digital Solutions

## Live Demo Flow (2 minutes)

1. Open http://127.0.0.1:8000
2. Click **Load Full Sample (2 items)**
3. Download **Commercial Invoice** and **Packing List** PDFs
4. Click **Simulate Escrow Deposit (PAPSS)**
5. Mark as **Shipped** → **Simulate Customs Clearance** → **Release Funds**
6. View full audit trail and compliance checklist

## What it solves

African MSMEs face high cross-border payment risk, complex documentation, and information asymmetry. This platform provides:

- Automated trade documents (Invoice + Packing List)
- Conditional payment assurance (escrow) designed for PAPSS local-currency settlement
- Corridor-aware compliance checklist
- Full transaction history for trust and audit

## Features

| Feature | Status |
|---------|--------|
| Multi-item trade creation | Working |
| Commercial Invoice PDF | Working |
| Packing List PDF | Working |
| Simulated PAPSS-ready escrow | Working |
| Compliance checklist | Working |
| SQLite persistence | Working |
| Trade listing dashboard | Working |
| Responsive mobile-first UI | Working |

## Quick Start

```bash
git clone https://github.com/Brightwell-Dlamini/trade-assurance-gateway.git
cd trade-assurance-gateway
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Open: http://127.0.0.1:8000  
API docs: http://127.0.0.1:8000/docs

## Project Structure

```
trade-assurance-gateway/
├── backend/main.py          # FastAPI application
├── templates/index.html     # Frontend
├── docs/
│   ├── ARCHITECTURE.md
│   └── PITCH_NOTES.md
├── data/                    # SQLite (runtime)
├── generated_docs/          # PDFs (runtime)
├── requirements.txt
└── README.md
```

## Architecture

See `docs/ARCHITECTURE.md`.

## Pitch & Impact Notes

See `docs/PITCH_NOTES.md`.

## Important Disclaimer

This is a demonstration prototype. Escrow, customs and payment steps are simulated. Production deployment requires PAPSS onboarding, bank partnerships, data-protection compliance and formal agreements with national authorities.

## Challenge Details

- Deadline: 4 September 2026
- Official site: https://au-afcfta.org
- Enquiries: DT@au-afcfta.org

Built for the AfCFTA Digital Innovation Challenge 2nd Edition.
