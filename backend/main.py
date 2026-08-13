"""
Trade Assurance Gateway
AfCFTA Digital Innovation Challenge – 2nd Edition
Fully working MVP for presentation

Features:
- Multi-item trade creation
- Commercial Invoice + Packing List PDF generation
- Simulated PAPSS-ready escrow (deposit → ship → customs → release)
- SQLite persistence
- Trade listing dashboard
- Compliance checklist
- Clean responsive UI
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum
import uuid
import json
import aiosqlite
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

app = FastAPI(
    title="Trade Assurance Gateway",
    description="Digital trade facilitation platform for African MSMEs under AfCFTA",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
GENERATED_DIR = BASE_DIR / "generated_docs"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "trades.db"

GENERATED_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class TradeStatus(str, Enum):
    DRAFT = "draft"
    FUNDED = "funded"
    SHIPPED = "shipped"
    CUSTOMS_CLEARED = "customs_cleared"
    SETTLED = "settled"
    DISPUTED = "disputed"

class Party(BaseModel):
    name: str
    country: str
    email: Optional[str] = None
    phone: Optional[str] = None

class ProductItem(BaseModel):
    description: str
    hs_code: Optional[str] = None
    quantity: float = Field(gt=0)
    unit: str = "pcs"
    unit_price: float = Field(gt=0)
    currency: str = "USD"
    weight_kg: Optional[float] = None
    package_count: Optional[int] = None

class TradeCreate(BaseModel):
    seller: Party
    buyer: Party
    items: List[ProductItem]
    origin_country: str
    destination_country: str
    incoterms: str = "CIF"
    payment_terms: str = "Escrow – release on customs clearance"
    notes: Optional[str] = None

class EscrowAction(BaseModel):
    action: str
    notes: Optional[str] = None

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        await db.commit()

async def save_trade(trade: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO trades (id, data, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (trade["id"], json.dumps(trade), trade["status"], trade["created_at"], trade["updated_at"])
        )
        await db.commit()

async def load_trade(trade_id: str) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT data FROM trades WHERE id = ?", (trade_id.upper(),)) as cur:
            row = await cur.fetchone()
            return json.loads(row[0]) if row else None

async def list_trades() -> List[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT data FROM trades ORDER BY created_at DESC") as cur:
            rows = await cur.fetchall()
            return [json.loads(r[0]) for r in rows]

# ---------------------------------------------------------------------------
# PDF Generation
# ---------------------------------------------------------------------------
def _styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("T", parent=styles["Heading1"], alignment=TA_CENTER, fontSize=16, spaceAfter=10),
        "sub": ParagraphStyle("S", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9, textColor=colors.HexColor("#4a5568")),
        "h": styles["Heading2"],
        "n": styles["Normal"],
        "f": ParagraphStyle("F", parent=styles["Normal"], fontSize=7, textColor=colors.grey),
    }

def generate_invoice(trade: dict) -> Path:
    path = GENERATED_DIR / f"invoice_{trade['id']}.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)
    s = _styles()
    story = []
    story.append(Paragraph("COMMERCIAL INVOICE", s["title"]))
    story.append(Paragraph("Trade Assurance Gateway • AfCFTA MSME Prototype", s["sub"]))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(f"<b>Seller:</b> {trade['seller']['name']} ({trade['seller']['country']})", s["n"]))
    story.append(Paragraph(f"<b>Buyer:</b> {trade['buyer']['name']} ({trade['buyer']['country']})", s["n"]))
    story.append(Spacer(1, 4*mm))
    meta = [
        ["Invoice No.", trade["id"]],
        ["Date", trade["created_at"][:10]],
        ["Origin", trade["origin_country"]],
        ["Destination", trade["destination_country"]],
        ["Incoterms", trade["incoterms"]],
        ["Payment", trade["payment_terms"]],
    ]
    t = Table(meta, colWidths=[35*mm, 130*mm])
    t.setStyle(TableStyle([("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 9), ("BOTTOMPADDING", (0,0), (-1,-1), 3)]))
    story.append(t)
    story.append(Spacer(1, 6*mm))
    rows = [["Description", "HS Code", "Qty", "Unit", "Unit Price", "Amount"]]
    for it in trade["items"]:
        amt = it["quantity"] * it["unit_price"]
        rows.append([it["description"][:42], it.get("hs_code") or "—", str(it["quantity"]), it["unit"], f"{it['unit_price']:.2f}", f"{amt:.2f}"])
    rows.append(["", "", "", "", "TOTAL", f"{trade['total_amount']:.2f} {trade['currency']}"])
    t2 = Table(rows, colWidths=[58*mm, 25*mm, 18*mm, 15*mm, 25*mm, 28*mm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a365d")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ALIGN", (2,0), (-1,-1), "RIGHT"),
        ("GRID", (0,0), (-1,-2), 0.4, colors.grey),
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
        ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#edf2f7")),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(t2)
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("Auto-generated by Trade Assurance Gateway for the AfCFTA Digital Innovation Challenge. Not a legally binding customs document.", s["f"]))
    doc.build(story)
    return path

def generate_packing_list(trade: dict) -> Path:
    path = GENERATED_DIR / f"packing_{trade['id']}.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)
    s = _styles()
    story = []
    story.append(Paragraph("PACKING LIST", s["title"]))
    story.append(Paragraph("Trade Assurance Gateway • AfCFTA MSME Prototype", s["sub"]))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(f"<b>Trade ID:</b> {trade['id']}", s["n"]))
    story.append(Paragraph(f"<b>Seller:</b> {trade['seller']['name']} ({trade['seller']['country']})", s["n"]))
    story.append(Paragraph(f"<b>Buyer:</b> {trade['buyer']['name']} ({trade['buyer']['country']})", s["n"]))
    story.append(Paragraph(f"<b>Route:</b> {trade['origin_country']} → {trade['destination_country']}", s["n"]))
    story.append(Spacer(1, 5*mm))
    rows = [["#", "Description", "HS Code", "Qty", "Unit", "Pkgs", "Weight (kg)"]]
    total_pkgs, total_w = 0, 0.0
    for i, it in enumerate(trade["items"], 1):
        pkgs = it.get("package_count") or max(1, int(it["quantity"] // 10) or 1)
        w = it.get("weight_kg") or round(it["quantity"] * 0.45, 2)
        total_pkgs += pkgs
        total_w += w
        rows.append([str(i), it["description"][:36], it.get("hs_code") or "—", str(it["quantity"]), it["unit"], str(pkgs), f"{w:.2f}"])
    rows.append(["", "TOTAL", "", "", "", str(total_pkgs), f"{total_w:.2f}"])
    t = Table(rows, colWidths=[12*mm, 55*mm, 25*mm, 18*mm, 15*mm, 18*mm, 25*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a365d")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ALIGN", (0,0), (0,-1), "CENTER"),
        ("ALIGN", (3,0), (-1,-1), "RIGHT"),
        ("GRID", (0,0), (-1,-2), 0.4, colors.grey),
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
        ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#edf2f7")),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("Weights and package counts are estimates when not supplied. Generated for AfCFTA Digital Innovation Challenge demonstration.", s["f"]))
    doc.build(story)
    return path

def compliance_checklist(origin: str, dest: str) -> list:
    return [
        {"item": "Commercial Invoice", "required": True, "status": "generated"},
        {"item": "Packing List", "required": True, "status": "generated"},
        {"item": "Certificate of Origin (AfCFTA)", "required": True, "status": "template_ready"},
        {"item": "Transport Document (B/L or AWB)", "required": True, "status": "pending"},
        {"item": "Import Declaration", "required": True, "status": "buyer_side"},
        {"item": "Proof of Payment / Escrow", "required": True, "status": "system"},
    ]

# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup():
    await init_db()
    print("=" * 60)
    print("Trade Assurance Gateway v1.0.0")
    print("AfCFTA Digital Innovation Challenge – Ready for presentation")
    print("http://127.0.0.1:8000")
    print("=" * 60)

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse((TEMPLATES_DIR / "index.html").read_text(encoding="utf-8"))

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "Trade Assurance Gateway",
        "version": "1.0.0",
        "persistence": "SQLite",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/api/trades")
async def create_trade(body: TradeCreate):
    tid = str(uuid.uuid4())[:8].upper()
    items = [i.model_dump() for i in body.items]
    total = sum(i["quantity"] * i["unit_price"] for i in items)
    currency = items[0]["currency"] if items else "USD"
    now = datetime.now(timezone.utc).isoformat()
    trade = {
        "id": tid,
        "seller": body.seller.model_dump(),
        "buyer": body.buyer.model_dump(),
        "items": items,
        "origin_country": body.origin_country,
        "destination_country": body.destination_country,
        "incoterms": body.incoterms,
        "payment_terms": body.payment_terms,
        "notes": body.notes,
        "total_amount": total,
        "currency": currency,
        "status": TradeStatus.DRAFT.value,
        "escrow_balance": 0.0,
        "created_at": now,
        "updated_at": now,
        "history": [{"event": "created", "timestamp": now, "notes": "Trade created"}],
        "compliance_checklist": compliance_checklist(body.origin_country, body.destination_country),
        "documents": {
            "invoice": f"/api/trades/{tid}/documents/invoice",
            "packing_list": f"/api/trades/{tid}/documents/packing-list"
        }
    }
    generate_invoice(trade)
    generate_packing_list(trade)
    await save_trade(trade)
    return trade

@app.get("/api/trades")
async def get_trades():
    return await list_trades()

@app.get("/api/trades/{trade_id}")
async def get_trade(trade_id: str):
    trade = await load_trade(trade_id)
    if not trade:
        raise HTTPException(404, "Trade not found")
    return trade

@app.get("/api/trades/{trade_id}/documents/invoice")
async def get_invoice(trade_id: str):
    trade = await load_trade(trade_id)
    if not trade:
        raise HTTPException(404, "Trade not found")
    path = GENERATED_DIR / f"invoice_{trade_id.upper()}.pdf"
    if not path.exists():
        generate_invoice(trade)
    return FileResponse(path, filename=f"Invoice_{trade_id.upper()}.pdf", media_type="application/pdf")

@app.get("/api/trades/{trade_id}/documents/packing-list")
async def get_packing(trade_id: str):
    trade = await load_trade(trade_id)
    if not trade:
        raise HTTPException(404, "Trade not found")
    path = GENERATED_DIR / f"packing_{trade_id.upper()}.pdf"
    if not path.exists():
        generate_packing_list(trade)
    return FileResponse(path, filename=f"PackingList_{trade_id.upper()}.pdf", media_type="application/pdf")

@app.post("/api/trades/{trade_id}/escrow")
async def escrow(trade_id: str, action: EscrowAction):
    trade = await load_trade(trade_id)
    if not trade:
        raise HTTPException(404, "Trade not found")
    now = datetime.now(timezone.utc).isoformat()
    a = action.action.lower()

    if a == "deposit":
        if trade["status"] != "draft":
            raise HTTPException(400, "Can only deposit on draft trades")
        trade["escrow_balance"] = trade["total_amount"]
        trade["status"] = "funded"
        trade["history"].append({"event": "escrow_funded", "amount": trade["total_amount"], "timestamp": now, "notes": action.notes or "Simulated PAPSS local-currency deposit"})
    elif a == "ship":
        if trade["status"] != "funded":
            raise HTTPException(400, "Must be funded first")
        trade["status"] = "shipped"
        trade["history"].append({"event": "shipped", "timestamp": now, "notes": action.notes or "Shipment confirmed"})
    elif a == "customs_clear":
        if trade["status"] not in ("shipped", "funded"):
            raise HTTPException(400, "Invalid status")
        trade["status"] = "customs_cleared"
        trade["history"].append({"event": "customs_cleared", "timestamp": now, "notes": action.notes or "Customs clearance confirmed (simulated)"})
    elif a == "release":
        if trade["status"] != "customs_cleared":
            raise HTTPException(400, "Release only after customs clearance")
        released = trade["escrow_balance"]
        trade["escrow_balance"] = 0.0
        trade["status"] = "settled"
        trade["history"].append({"event": "escrow_released", "amount": released, "timestamp": now, "notes": action.notes or "Funds released to seller via simulated PAPSS"})
    elif a == "dispute":
        trade["status"] = "disputed"
        trade["history"].append({"event": "dispute_raised", "timestamp": now, "notes": action.notes or "Dispute opened"})
    else:
        raise HTTPException(400, f"Unknown action: {a}")

    trade["updated_at"] = now
    await save_trade(trade)
    return trade

@app.get("/api/demo/sample")
async def sample():
    body = TradeCreate(
        seller=Party(name="Kente Weavers Cooperative", country="Ghana", email="export@kenteweavers.gh", phone="+233241234567"),
        buyer=Party(name="Nairobi Fashion Hub Ltd", country="Kenya", email="procurement@nairobifashion.co.ke", phone="+254712345678"),
        items=[
            ProductItem(description="Handwoven Kente cloth (traditional design)", hs_code="5805.00", quantity=200, unit="metres", unit_price=18.50, weight_kg=45.0, package_count=8),
            ProductItem(description="Matching accessory sets", hs_code="6217.10", quantity=50, unit="sets", unit_price=12.00, weight_kg=8.5, package_count=5),
        ],
        origin_country="Ghana",
        destination_country="Kenya",
        incoterms="CIF",
        notes="Sample intra-African trade under AfCFTA preferential rules"
    )
    return await create_trade(body)
