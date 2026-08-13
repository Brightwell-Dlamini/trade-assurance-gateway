# Trade Assurance Gateway – Technical Architecture

**AfCFTA Digital Innovation Challenge – 2nd Edition**  
Version 0.2.0

## 1. Purpose

Provide African MSMEs with a practical, mobile-first digital layer that reduces friction in cross-border trade by combining:

- Automated trade documentation
- Conditional payment assurance (escrow) structured for PAPSS
- Basic regulatory compliance guidance

The solution is designed to complement (not replace) existing continental infrastructure such as PAPSS and national single windows.

## 2. Core Modules

### 2.1 Trade Document Engine
- Generates Commercial Invoice and Packing List as PDFs
- Accepts multi-item trades
- Produces audit-ready documents suitable for demonstration and further integration with customs systems

### 2.2 Escrow & Settlement Layer
- Milestone-based fund release logic:
  1. Deposit (buyer funds held)
  2. Shipment confirmed
  3. Customs clearance confirmed
  4. Release to seller
- Structured so that real PAPSS (or mobile-money) rails can replace the current simulation
- Full event history retained for each trade

### 2.3 Compliance Co-Pilot
- Generates a corridor-aware checklist of required documents
- Currently rule-based; designed for later AI-assisted HS-code and regulation mapping

### 2.4 Persistence
- SQLite for the MVP (data/trades.db)
- Ready to migrate to PostgreSQL for production multi-user deployments

## 3. Technology Stack (MVP)

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Backend | FastAPI (Python) | Fast, async, automatic OpenAPI docs |
| Database | SQLite (aiosqlite) | Zero-config persistence for prototype |
| PDF Generation | ReportLab | Reliable, pure-Python |
| Frontend | Vanilla HTML/CSS/JS | Lightweight, mobile-responsive, no build step |
| Future mobile channel | USSD / WhatsApp | Critical for last-mile MSME access |

## 4. Data Flow (Happy Path)

1. User creates trade (seller, buyer, items, corridor)
2. System generates Invoice + Packing List PDFs
3. Buyer deposits funds → status = funded
4. Seller marks shipped → status = shipped
5. Customs clearance confirmed → status = customs_cleared
6. Funds released to seller → status = settled
7. Full audit trail available at every step

## 5. Integration Roadmap

| Integration | Priority | Notes |
|-------------|----------|-------|
| PAPSS | High | Replace simulated deposit/release |
| National single windows / customs status APIs | High | Real clearance confirmation |
| Mobile money (M-Pesa, MTN MoMo, etc.) | High | Last-mile payment access |
| Digital identity (AU / national) | Medium | Stronger KYC |
| Logistics tracking providers | Medium | Automated shipment evidence |
| AI regulatory translation | Medium | Scale compliance support across languages and countries |

## 6. Security & Compliance Considerations (Future)

- Role-based access (seller / buyer / admin)
- Encryption at rest and in transit
- Data minimisation and retention policy
- Alignment with AfCFTA Digital Trade Protocol principles
- Formal agreements required before any live funds movement

## 7. Alignment with AfCFTA Goals

- Directly addresses payments, documentation and trust barriers for MSMEs
- Designed for interoperability with continental digital public infrastructure
- Supports inclusive access (mobile-first, low-bandwidth friendly)
- Provides a clear path from prototype to operational service

---

*This document will be expanded as the prototype matures toward the 4 September 2026 application deadline.*
