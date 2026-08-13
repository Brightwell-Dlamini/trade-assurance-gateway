# Trade Assurance Gateway

**MVP Prototype for the AfCFTA Digital Innovation Challenge (2nd Edition)**

Theme: *Realizing the AfCFTA for MSMEs through Digital Solutions*

## What this is

A functional demonstration of a digital platform that helps African Micro, Small and Medium Enterprises (MSMEs) complete cross-border trade more safely and efficiently.

It adapts proven approaches from developed markets (national single windows, B2B escrow/trade assurance, regulatory intelligence) to the African context, with particular attention to:

- Local-currency settlement readiness (PAPSS structure)
- Mobile-first / low-bandwidth usability
- Automated trade document generation
- Conditional release of funds against trade milestones

## Current MVP Features

| Feature | Status | Notes |
|---------|--------|-------|
| Create trade transaction | Working | Seller, buyer, product, corridor |
| Auto-generate Commercial Invoice (PDF) | Working | ReportLab |
| Basic compliance checklist | Working | Corridor-aware template |
| Simulated escrow flow | Working | Deposit → Ship → Customs Clear → Release |
| Transaction history / audit trail | Working | In-memory |
| Responsive web interface | Working | Suitable for mobile demonstration |
| Real PAPSS integration | Planned | Requires official API credentials |
| National single-window connectors | Planned | Country-by-country |
| AI HS-code & rule suggestion | Planned | |
| USSD / WhatsApp channel | Planned | Critical for last-mile MSMEs |
| Persistent database | Planned | Currently in-memory (restarts clear data) |

## Quick Start

```bash
cd trade-assurance-gateway
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Then open: http://127.0.0.1:8000

API documentation (Swagger): http://127.0.0.1:8000/docs

## Typical Demo Flow

1. Open the web interface.
2. Click **Load Full Sample** (or create your own trade).
3. Download the generated Commercial Invoice PDF.
4. Click **Simulate Escrow Deposit (PAPSS)**.
5. Mark as **Shipped**.
6. Simulate **Customs Clearance**.
7. **Release Funds to Seller**.

You will see the full audit trail and status changes at each step.

## Project Structure

```
trade-assurance-gateway/
├── backend/
│   └── main.py              # FastAPI application
├── templates/
│   └── index.html           # Frontend interface
├── generated_docs/          # Auto-generated PDFs (created at runtime)
├── docs/                    # Additional documentation
├── requirements.txt
└── README.md
```

## Architecture Alignment

This MVP implements the first three modules described in the technical architecture:

1. **Trade Document Engine** – Commercial Invoice generation
2. **Escrow & Settlement Layer** – Milestone-based release logic (ready for PAPSS)
3. **Compliance Co-Pilot** – Initial checklist generation

Identity, full logistics visibility, and marketplace matching are designed but not yet implemented.

## Important Disclaimers

- This is a **prototype for demonstration and further development**.
- Escrow, customs, and payment steps are **simulated**.
- No real money is moved and no real customs declarations are filed.
- Production use requires proper licensing, bank partnerships, PAPSS onboarding, data protection compliance, and formal agreements with national authorities.

## Next Development Priorities

1. Replace in-memory store with PostgreSQL.
2. Add multi-item support and packing list generation.
3. Integrate a real or sandbox payment rail (starting with mobile money simulation).
4. Build a lightweight USSD/WhatsApp interface.
5. Add basic user accounts and role separation (seller / buyer).
6. Prepare a short pitch deck and impact metrics dashboard for the AfCFTA Challenge submission.

## Contact / Challenge Context

- Challenge deadline: **4 September 2026**
- Official site: https://au-afcfta.org
- Enquiries: DT@au-afcfta.org

Built as a practical starting point for an AfCFTA Digital Innovation Challenge application.
