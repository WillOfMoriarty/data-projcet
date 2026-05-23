"""
parser.py
Parses raw OCR text from receipts into structured data.

Handles common Indonesian receipt formats:
  AQUA 600ML          2X   3.000    6.000
  INDOMIE GORENG      3X   3.500   10.500
  CHITATO BBQ         1X  12.000   12.000

Also extracts: store name, date, total, subtotal, discount.
"""

import re
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class ReceiptItem:
    item_name: str
    qty: int
    price: int       # harga satuan
    total: int       # qty * price


@dataclass
class ParsedReceipt:
    store_name: str = ""
    date: str = ""
    items: list[ReceiptItem] = field(default_factory=list)
    subtotal: int = 0
    discount: int = 0
    total: int = 0
    raw_text: str = ""
    parse_warnings: list[str] = field(default_factory=list)


# ── Helpers ──────────────────────────────────────────────────────────────────

def clean_number(s: str) -> int:
    """
    Convert Indonesian number format to int.
    '12.000' → 12000
    '1.500.000' → 1500000
    """
    cleaned = re.sub(r"[^\d]", "", s)
    return int(cleaned) if cleaned else 0


def normalize_line(line: str) -> str:
    """Collapse multiple spaces to one, strip edges."""
    return re.sub(r" {2,}", " ", line).strip()


# ── Item line patterns ────────────────────────────────────────────────────────

# Format: NAMA PRODUK   2X   3.000   6.000
ITEM_PATTERN_QTY_PRICE_TOTAL = re.compile(
    r"^(.+?)\s+(\d+)[Xx]\s+([\d.,]+)\s+([\d.,]+)$"
)

# Format: NAMA PRODUK   6.000   (no explicit qty, assume 1)
ITEM_PATTERN_NAME_TOTAL = re.compile(
    r"^(.+?)\s+([\d]{1,3}(?:[.,]\d{3})+)$"
)

# Format: NAMA PRODUK   3   6000
ITEM_PATTERN_QTY_TOTAL_NOFMT = re.compile(
    r"^(.+?)\s+(\d+)\s+(\d{3,})$"
)


def parse_item_line(line: str) -> Optional[ReceiptItem]:
    """
    Try to extract item info from a single OCR line.
    Returns ReceiptItem or None if line doesn't match any pattern.
    """
    line = normalize_line(line)

    # Pattern 1: NAME  QTYx  PRICE  TOTAL
    m = ITEM_PATTERN_QTY_PRICE_TOTAL.match(line)
    if m:
        name = m.group(1).strip().upper()
        qty = int(m.group(2))
        price = clean_number(m.group(3))
        total = clean_number(m.group(4))
        if price > 0 and total > 0:
            return ReceiptItem(item_name=name, qty=qty, price=price, total=total)

    # Pattern 2: NAME  TOTAL (assume qty=1, price=total)
    m = ITEM_PATTERN_NAME_TOTAL.match(line)
    if m:
        name = m.group(1).strip().upper()
        total = clean_number(m.group(2))
        if total > 0 and len(name) > 2:
            return ReceiptItem(item_name=name, qty=1, price=total, total=total)

    # Pattern 3: NAME  QTY  TOTAL (no decimal formatting)
    m = ITEM_PATTERN_QTY_TOTAL_NOFMT.match(line)
    if m:
        name = m.group(1).strip().upper()
        qty = int(m.group(2))
        total = clean_number(m.group(3))
        price = total // qty if qty > 0 else total
        if total > 0 and len(name) > 2:
            return ReceiptItem(item_name=name, qty=qty, price=price, total=total)

    return None


# ── Receipt-level extractors ──────────────────────────────────────────────────

def extract_store_name(lines: list[str]) -> str:
    """
    Store name is usually in the first 3 non-empty lines.
    Heuristic: all caps, no numbers, > 3 chars.
    """
    for line in lines[:5]:
        line = line.strip()
        if len(line) > 3 and line.isupper() and not re.search(r"\d", line):
            return line
    # Fallback: just return first non-empty line
    for line in lines[:3]:
        if line.strip():
            return line.strip()
    return "UNKNOWN STORE"


def extract_date(raw_text: str) -> str:
    """Extract date from receipt. Supports DD/MM/YYYY and variants."""
    patterns = [
        r"\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\b",   # 28/06/2024
        r"\b(\d{1,2}\s+\w+\s+\d{4})\b",                  # 28 Juni 2024
    ]
    for pat in patterns:
        m = re.search(pat, raw_text)
        if m:
            return m.group(1)
    return ""


def extract_total(raw_text: str) -> int:
    """
    Extract TOTAL value from receipt.
    Looks for lines like 'TOTAL  46.500' or 'GRAND TOTAL  46500'.
    """
    patterns = [
        r"(?:GRAND\s+)?TOTAL\s+([\d.,]+)",
        r"JUMLAH\s+([\d.,]+)",
        r"AMOUNT\s+([\d.,]+)",
    ]
    for pat in patterns:
        m = re.search(pat, raw_text, re.IGNORECASE)
        if m:
            return clean_number(m.group(1))
    return 0


def extract_subtotal(raw_text: str) -> int:
    patterns = [
        r"SUBTOTAL\s+([\d.,]+)",
        r"SUB\s+TOTAL\s+([\d.,]+)",
        r"TOTAL\s+BELANJA\s+([\d.,]+)",
    ]
    for pat in patterns:
        m = re.search(pat, raw_text, re.IGNORECASE)
        if m:
            return clean_number(m.group(1))
    return 0


def extract_discount(raw_text: str) -> int:
    patterns = [
        r"(?:DISKON|DISCOUNT|POTONGAN)\s+([\d.,]+)",
    ]
    for pat in patterns:
        m = re.search(pat, raw_text, re.IGNORECASE)
        if m:
            return clean_number(m.group(1))
    return 0


# ── Skip lines that are NOT items ─────────────────────────────────────────────

SKIP_KEYWORDS = {
    "TOTAL", "SUBTOTAL", "SUB TOTAL", "DISKON", "DISCOUNT",
    "TUNAI", "CASH", "KEMBALI", "CHANGE", "MEMBER", "TERIMA",
    "KASIR", "NOTA", "STRUK", "THANK", "PAJAK", "TAX", "PPN",
    "GRAND", "DEBIT", "KREDIT", "CARD", "KEMBALIAN", "BAYAR",
    "HARGA", "QTY", "JUMLAH", "NAMA", "NO", "----", "====",
    "TEL", "TELP", "JL", "PHONE", "FAX",
}


def is_skip_line(line: str) -> bool:
    upper = line.strip().upper()
    if not upper:
        return True
    for kw in SKIP_KEYWORDS:
        if upper.startswith(kw):
            return True
    # Skip short lines and pure separators
    if len(upper) < 4:
        return True
    if re.match(r"^[\-=\*\.]+$", upper):
        return True
    return False


# ── Main parse function ───────────────────────────────────────────────────────

def parse_receipt(raw_text: str) -> ParsedReceipt:
    """
    Parse raw OCR text into a structured ParsedReceipt object.

    Args:
        raw_text: full text string from OCR

    Returns:
        ParsedReceipt with items, totals, store info
    """
    lines = raw_text.splitlines()
    result = ParsedReceipt(raw_text=raw_text)
    warnings = []

    # Extract receipt-level fields
    result.store_name = extract_store_name(lines)
    result.date = extract_date(raw_text)
    result.total = extract_total(raw_text)
    result.subtotal = extract_subtotal(raw_text)
    result.discount = extract_discount(raw_text)

    # Parse items line by line
    items = []
    for line in lines:
        if is_skip_line(line):
            continue
        item = parse_item_line(line)
        if item:
            items.append(item)

    result.items = items

    # Validation warnings
    if not items:
        warnings.append("No items could be parsed. OCR text may need review.")

    if result.total == 0:
        warnings.append("Total not found. Check OCR output.")

    if items:
        calculated = sum(i.total for i in items)
        if result.total > 0 and abs(calculated - result.total) > result.total * 0.15:
            warnings.append(
                f"Parsed items sum ({calculated:,}) differs from receipt total ({result.total:,}). "
                "Some items may have been missed."
            )

    result.parse_warnings = warnings
    return result


def receipt_to_dict(receipt: ParsedReceipt) -> dict:
    """Convert ParsedReceipt to plain dict (for JSON/SQLite)."""
    d = asdict(receipt)
    d["items"] = [asdict(item) for item in receipt.items]
    return d
