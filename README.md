# Trade Assurance Gateway

**Institutional-grade digital trade facilitation for the African Continental Free Trade Area**  
Version 1.2.0 · AfCFTA Digital Innovation Challenge

## Overview

Trade Assurance Gateway enables African MSMEs to execute cross-border trade with institutional documentation, conditional payment assurance, and full auditability. It is designed for interoperability with:

- **PAPSS** – Pan-African Payment and Settlement System
- **ADAPT** – Africa Digital Access and Public Infrastructure for Trade
- The continental **e-Certificate of Origin** programme
- National single windows and the AfCFTA Digital Trade Protocol

## Demonstration (2–3 minutes)

```bash
git clone https://github.com/Brightwell-Dlamini/trade-assurance-gateway.git
cd trade-assurance-gateway
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Open http://127.0.0.1:8000

1. Click **Load Institutional Sample**
2. Download Commercial Invoice, Packing List and **Certificate of Origin (AfCFTA)**
3. Execute: Place Funds in Escrow → Confirm Shipment → Confirm Customs Clearance → Release Funds
4. Review Corridor Insights, Compliance Checklist, Interoperability tags and the full Audit Trail

## Key Capabilities

| Capability | Status |
|------------|--------|
| Multi-item trade creation | Working |
| Commercial Invoice PDF | Working |
| Packing List PDF | Working |
| AfCFTA Certificate of Origin template | Working |
| PAPSS-oriented milestone escrow | Working |
| Corridor insights | Working |
| Compliance checklist | Working |
| Verifiable audit trail (ADAPT-oriented) | Working |
| Inclusivity framing (women-led / youth-led MSMEs) | Working |
| SQLite persistence | Working |

## Architecture Alignment

- **Trade & Investment Facilitation** – document generation, compliance, procedures
- **Digital Financial Services** – conditional escrow structured for PAPSS
- **ADAPT readiness** – audit trail and document set designed for trust frameworks
- **e-CO readiness** – Certificate of Origin template aligned with continental programme

## Disclaimer

Demonstration system. Escrow and customs events are simulated. Production use requires PAPSS onboarding, banking partnerships, national single-window connectivity and formal certification arrangements.

## Challenge Context

- Theme: Realising the AfCFTA for MSMEs through Digital Solutions
- Deadline: 4 September 2026
- Official portal: https://au-afcfta.org
- Enquiries: DT@au-afcfta.org
