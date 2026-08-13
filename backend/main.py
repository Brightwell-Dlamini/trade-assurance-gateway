"""
Trade Assurance Gateway - MVP Backend
AfCFTA Digital Innovation Challenge 2nd Edition

This is a functional prototype demonstrating core modules:
- Trade transaction creation
- Automated document generation (Commercial Invoice + Certificate of Origin template)
- Simulated escrow / settlement flow (PAPSS-ready structure)
- Basic compliance checklist

Note: Real PAPSS, bank, and customs integrations require official credentials
and production agreements. This MVP uses simulation for demonstration.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timezone
from enum import Enum
import uuid
import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Trade Assurance Gateway",
    description="MVP for African MSME cross-border trade facilitation under AfCFTA",
    version="0.1.0"
)

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "frontend"
DOCS_DIR = BASE_DIR / "docs"
GENERATED_DIR = BASE_DIR / "generated_docs"

GENERATED_DIR.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# In-memory store for MVP (replace with PostgreSQL in production)
trades_db: Dict[str, dict] = {}
users_db: Dict[str, dict] = {}

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class TradeStatus(str, Enum):
    DRAFT = "draft"
    AWAITING_PAYMENT = "awaiting_payment"
    FUNDED = "funded"
    SHIPPED = "shipped"
    CUSTOMS_CLEARED = "customs_cleared"
    DELIVERED = "delivered"
    SETTLED = "settled"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"

class Party(BaseModel):
    name: str
    country: str
    email: Optional[str] = None
    phone: Optional[str] = None
    business_id: Optional[str] = None

class ProductItem(BaseModel):
    description: str
    hs_code: Optional[str] = None
    quantity: float
    unit: str = "pcs"
    unit_price: float
    currency: str = "USD"

class TradeCreate(BaseModel):
    seller: Party
    buyer: Party
    items: List[ProductItem]
    origin_country: str
    destination_country: str
    incoterms: str = "FOB"
    payment_terms: str = "Escrow - release on customs clearance"
    notes: Optional[str] = None

class EscrowAction(BaseModel):
    action: str  # deposit | release | dispute
    amount: Optional[float] = None
    evidence_url: Optional[str] = None
    notes: Optional[str] = None

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def calculate_total(items: List[ProductItem]) -> float:
    return sum(item.quantity * item.unit_price for item in items)

def generate_invoice_pdf(trade: dict) -> str:
    """Generate a simple Commercial Invoice PDF."""
    trade_id = trade["id"]
    filename = f"invoice_{trade_id}.pdf"
    filepath = GENERATED_DIR / filename

    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        fontSize=16,
        spaceAfter=12
    )
    normal = styles["Normal"]
    heading = styles["Heading2"]

    story = []
    story.append(Paragraph("COMMERCIAL INVOICE", title_style))
    story.append(Paragraph("Trade Assurance Gateway – AfCFTA MSME Prototype", 
                           ParagraphStyle("Sub", parent=normal, alignment=TA_CENTER, fontSize=9)))
    story.append(Spacer(1, 8*mm))

    # Parties
    story.append(Paragraph("<b>Seller</b>", heading))
    story.append(Paragraph(f"{trade['seller']['name']}<br/>{trade['seller']['country']}", normal))
    if trade['seller'].get('email'):
        story.append(Paragraph(trade['seller']['email'], normal))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph("<b>Buyer</b>", heading))
    story.append(Paragraph(f"{trade['buyer']['name']}<br/>{trade['buyer']['country']}", normal))
    story.append(Spacer(1, 6*mm))

    # Trade meta
    meta_data = [
        ["Invoice No:", trade_id],
        ["Date:", trade["created_at"][:10]],
        ["Origin:", trade["origin_country"]],
        ["Destination:", trade["destination_country"]],
        ["Incoterms:", trade["incoterms"]],
        ["Payment Terms:", trade["payment_terms"]],
    ]
    meta_table = Table(meta_data, colWidths=[40*mm, 120*mm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8*mm))

    # Items table
    story.append(Paragraph("<b>Goods</b>", heading))
    item_data = [["Description", "HS Code", "Qty", "Unit", "Unit Price", "Amount"]]
    for item in trade["items"]:
        amount = item["quantity"] * item["unit_price"]
        item_data.append([
            item["description"][:40],
            item.get("hs_code") or "—",
            str(item["quantity"]),
            item["unit"],
            f"{item['unit_price']:.2f}",
            f"{amount:.2f}"
        ])
    item_data.append(["", "", "", "", "TOTAL", f"{trade['total_amount']:.2f} {trade['currency']}"])

    items_table = Table(item_data, colWidths=[55*mm, 25*mm, 18*mm, 15*mm, 25*mm, 30*mm])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -2), 0.5, colors.grey),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 10*mm))

    story.append(Paragraph(
        "<i>This document was auto-generated by Trade Assurance Gateway for demonstration purposes "
        "under the AfCFTA Digital Innovation Challenge. It is not a legally binding customs document.</i>",
        ParagraphStyle("Footer", parent=normal, fontSize=7, textColor=colors.grey)
    ))

    doc.build(story)
    return str(filepath)

def generate_compliance_checklist(origin: str, destination: str, items: list) -> list:
    """Return a basic compliance checklist (simulated)."""
    checklist = [
        {"item": "Commercial Invoice", "required": True, "status": "generated"},
        {"item": "Packing List", "required": True, "status": "pending"},
        {"item": "Certificate of Origin (AfCFTA preferential)", "required": True, "status": "template_ready"},
        {"item": "Bill of Lading / Air Waybill", "required": True, "status": "pending"},
        {"item": "Phytosanitary / Health Certificate (if agri)", "required": False, "status": "check_product"},
        {"item": "Export Permit (if controlled goods)", "required": False, "status": "check_hs"},
        {"item": "Import Declaration / Entry", "required": True, "status": "buyer_side"},
        {"item": "Proof of Payment / Escrow confirmation", "required": True, "status": "system"},
    ]
    return checklist

# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    html_path = TEMPLATES_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "Trade Assurance Gateway",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "MVP / Simulation"
    }

@app.post("/api/trades")
async def create_trade(trade_in: TradeCreate):
    trade_id = str(uuid.uuid4())[:8].upper()
    total = calculate_total(trade_in.items)
    currency = trade_in.items[0].currency if trade_in.items else "USD"

    trade = {
        "id": trade_id,
        "seller": trade_in.seller.model_dump(),
        "buyer": trade_in.buyer.model_dump(),
        "items": [i.model_dump() for i in trade_in.items],
        "origin_country": trade_in.origin_country,
        "destination_country": trade_in.destination_country,
        "incoterms": trade_in.incoterms,
        "payment_terms": trade_in.payment_terms,
        "notes": trade_in.notes,
        "total_amount": total,
        "currency": currency,
        "status": TradeStatus.DRAFT.value,
        "escrow_balance": 0.0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "history": [
            {"event": "created", "timestamp": datetime.now(timezone.utc).isoformat(), "by": "system"}
        ]
    }

    # Generate documents
    invoice_path = generate_invoice_pdf(trade)
    trade["documents"] = {
        "commercial_invoice": f"/api/trades/{trade_id}/documents/invoice"
    }
    trade["compliance_checklist"] = generate_compliance_checklist(
        trade_in.origin_country, trade_in.destination_country, trade["items"]
    )

    trades_db[trade_id] = trade
    return trade

@app.get("/api/trades")
async def list_trades():
    return list(trades_db.values())

@app.get("/api/trades/{trade_id}")
async def get_trade(trade_id: str):
    trade = trades_db.get(trade_id.upper())
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade

@app.get("/api/trades/{trade_id}/documents/invoice")
async def download_invoice(trade_id: str):
    trade = trades_db.get(trade_id.upper())
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    filepath = GENERATED_DIR / f"invoice_{trade_id.upper()}.pdf"
    if not filepath.exists():
        generate_invoice_pdf(trade)
    return FileResponse(
        path=str(filepath),
        filename=f"Commercial_Invoice_{trade_id.upper()}.pdf",
        media_type="application/pdf"
    )

@app.post("/api/trades/{trade_id}/escrow")
async def escrow_action(trade_id: str, action: EscrowAction):
    trade = trades_db.get(trade_id.upper())
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    now = datetime.now(timezone.utc).isoformat()
    tid = trade_id.upper()

    if action.action == "deposit":
        if trade["status"] not in [TradeStatus.DRAFT.value, TradeStatus.AWAITING_PAYMENT.value]:
            raise HTTPException(status_code=400, detail="Cannot deposit in current status")
        amount = action.amount or trade["total_amount"]
        trade["escrow_balance"] = amount
        trade["status"] = TradeStatus.FUNDED.value
        trade["history"].append({
            "event": "escrow_funded",
            "amount": amount,
            "timestamp": now,
            "notes": action.notes or "Simulated PAPSS local-currency deposit"
        })

    elif action.action == "ship":
        if trade["status"] != TradeStatus.FUNDED.value:
            raise HTTPException(status_code=400, detail="Trade must be funded before shipping")
        trade["status"] = TradeStatus.SHIPPED.value
        trade["history"].append({
            "event": "shipped",
            "timestamp": now,
            "notes": action.notes or "Shipment confirmed"
        })

    elif action.action == "customs_clear":
        if trade["status"] not in [TradeStatus.SHIPPED.value, TradeStatus.FUNDED.value]:
            raise HTTPException(status_code=400, detail="Invalid status for customs clearance")
        trade["status"] = TradeStatus.CUSTOMS_CLEARED.value
        trade["history"].append({
            "event": "customs_cleared",
            "timestamp": now,
            "notes": action.notes or "Customs clearance confirmed (simulated)"
        })

    elif action.action == "release":
        if trade["status"] not in [TradeStatus.CUSTOMS_CLEARED.value, TradeStatus.DELIVERED.value]:
            raise HTTPException(status_code=400, detail="Release only after customs clearance or delivery")
        trade["status"] = TradeStatus.SETTLED.value
        released = trade["escrow_balance"]
        trade["escrow_balance"] = 0.0
        trade["history"].append({
            "event": "escrow_released",
            "amount": released,
            "timestamp": now,
            "notes": action.notes or "Funds released to seller via simulated PAPSS settlement"
        })

    elif action.action == "dispute":
        trade["status"] = TradeStatus.DISPUTED.value
        trade["history"].append({
            "event": "dispute_raised",
            "timestamp": now,
            "notes": action.notes or "Dispute opened"
        })

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action.action}")

    trade["updated_at"] = now
    trades_db[tid] = trade
    return trade

@app.get("/api/demo/sample")
async def create_sample_trade():
    """Create a ready-to-use sample trade for demonstration."""
    sample = TradeCreate(
        seller=Party(
            name="Kente Weavers Cooperative",
            country="Ghana",
            email="export@kenteweavers.gh",
            phone="+233241234567"
        ),
        buyer=Party(
            name="Nairobi Fashion Hub Ltd",
            country="Kenya",
            email="procurement@nairobifashion.co.ke",
            phone="+254712345678"
        ),
        items=[
            ProductItem(
                description="Handwoven Kente cloth (traditional design)",
                hs_code="5805.00",
                quantity=200,
                unit="metres",
                unit_price=18.50,
                currency="USD"
            ),
            ProductItem(
                description="Matching accessory sets",
                hs_code="6217.10",
                quantity=50,
                unit="sets",
                unit_price=12.00,
                currency="USD"
            )
        ],
        origin_country="Ghana",
        destination_country="Kenya",
        incoterms="CIF",
        payment_terms="Escrow – release on customs clearance",
        notes="Sample intra-African trade under AfCFTA preferential rules"
    )
    return await create_trade(sample)

# ---------------------------------------------------------------------------
# Startup message
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup():
    print("=" * 60)
    print("Trade Assurance Gateway MVP started")
    print("AfCFTA Digital Innovation Challenge – Prototype")
    print("API docs: http://127.0.0.1:8000/docs")
    print("=" * 60)
