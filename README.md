# Trade Assurance Gateway

**MVP Prototype for the AfCFTA Digital Innovation Challenge (2nd Edition)**  
**Version 0.2.0**

Theme: *Realizing the AfCFTA for MSMEs through Digital Solutions*

## What this is

A functional demonstration of a digital platform that helps African Micro, Small and Medium Enterprises (MSMEs) complete cross-border trade more safely and efficiently.

It adapts proven approaches from developed markets (national single windows, B2B escrow/trade assurance, regulatory intelligence) to the African context, with particular attention to:

- Local-currency settlement readiness (PAPSS structure)
- Mobile-first / low-bandwidth usability
- Automated trade document generation
- Conditional release of funds against trade milestones
- Persistent storage

## Current MVP Features (v0.2.0)

| Feature | Status | Notes |
|---------|--------|-------|
| Create trade transaction | Working | Multi-item support |
| Auto-generate Commercial Invoice (PDF) | Working | ReportLab |
| Auto-generate Packing List (PDF) | Working | Includes weight & package estimates |
| Basic compliance checklist | Working | Corridor-aware template |
| Simulated escrow flow | Working | Deposit → Ship → Customs Clear → Release |
| Transaction history / audit trail | Working | Full event log |
| Responsive web interface | Working | Suitable for mobile demonstration |
| SQLite persistence | Working | Data survives server restarts |
| Real PAPSS integration | Planned | Requires official API credentials |
| National single-window connectors | Planned | Country-by-country |
| AI HS-code & rule suggestion | Planned | |
| USSD / WhatsApp channel | Planned | Critical for last-mile MSMEs |

## Quick Start

```bash
git clone https://github.com/Brightwell-Dlamini/trade-assurance-gateway.git
cd trade-assurance-gateway
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Then open: http://127.0.0.1:8000

API documentation (Swagger): http://127.0.0.1:8000/docs

## Typical Demo Flow

1. Open the web interface.
2. Click **Load Full Sample** (or create your own trade).
3. Download the generated **Commercial Invoice** PDF.
4. Download the generated **Packing List** PDF.
5. Click **Simulate Escrow Deposit (PAPSS)**.
6. Mark as **Shipped**.
7. Simulate **Customs Clearance**.
8. **Release Funds to Seller**.

You will see the full audit trail and status changes at each step. Data is stored in SQLite.

## Project Structure

```
trade-assurance-gateway/
├── backend/
│   └── main.py              # FastAPI application (v0.2.0)
├── templates/
│   └── index.html           # Frontend interface
├── data/                    # SQLite database (created at runtime)
├── generated_docs/          # Auto-generated PDFs (created at runtime)
├── requirements.txt
└── README.md
```

## Architecture Alignment

This MVP implements the first three modules described in the technical architecture:

1. **Trade Document Engine** – Commercial Invoice + Packing List generation
2. **Escrow & Settlement Layer** – Milestone-based release logic (ready for PAPSS)
3. **Compliance Co-Pilot** – Initial checklist generation

Identity, full logistics visibility, and marketplace matching are designed but not yet implemented.

## Important Disclaimers

- This is a **prototype for demonstration and further development**.
- Escrow, customs, and payment steps are **simulated**.
- No real money is moved and no real customs declarations are filed.
- Production use requires proper licensing, bank partnerships, PAPSS onboarding, data protection compliance, and formal agreements with national authorities.

## Next Development Priorities

1. Basic user accounts and role separation (seller / buyer).
2. Integrate a real or sandbox payment rail (starting with mobile money simulation).
3. Build a lightweight USSD/WhatsApp interface.
4. AI-assisted HS code suggestion and regulatory translation.
5. Prepare a short pitch deck and impact metrics dashboard for the AfCFTA Challenge submission.

## Contact / Challenge Context

- Challenge deadline: **4 September 2026**
- Official site: https://au-afcfta.org
- Enquiries: DT@au-afcfta.org

Built as a practical starting point for an AfCFTA Digital Innovation Challenge application.
