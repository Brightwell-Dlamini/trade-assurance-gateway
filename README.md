# Trade Assurance Gateway

**Institutional-grade digital trade facilitation platform**  
Version 1.1.0 · AfCFTA Digital Innovation Challenge

## Overview

Trade Assurance Gateway is a production-oriented prototype that enables African MSMEs to execute cross-border trade with institutional-grade documentation, conditional payment assurance, and full auditability.

It combines:
- Automated generation of Commercial Invoices and Packing Lists
- Milestone-based escrow designed for PAPSS local-currency settlement
- Corridor-aware compliance guidance
- Complete transaction history

## Live Demonstration (2–3 minutes)

```bash
git clone https://github.com/Brightwell-Dlamini/trade-assurance-gateway.git
cd trade-assurance-gateway
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Open http://127.0.0.1:8000

1. Click **Load Institutional Sample**
2. Download Commercial Invoice and Packing List
3. Execute: Place Funds in Escrow → Confirm Shipment → Confirm Customs Clearance → Release Funds
4. Review the audit trail and compliance checklist

## Architecture

See `docs/ARCHITECTURE.md` and `docs/PITCH_NOTES.md`.

## Stack

- FastAPI + Pydantic + aiosqlite + ReportLab
- Clean state-machine design for trade lifecycle
- Responsive institutional UI

## Disclaimer

This is a high-fidelity demonstration system. Escrow and customs events are simulated. Live production use requires PAPSS onboarding, banking partnerships, and national single-window connectivity.

## Challenge Context

- AfCFTA Digital Innovation Challenge – 2nd Edition
- Deadline: 4 September 2026
- Official portal: https://au-afcfta.org
