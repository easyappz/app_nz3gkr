from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from .models import Listing


ALLOWED_AVITO_DOMAIN = "avito.ru"
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru,en;q=0.9",
}


@dataclass
class AvitoMetadata:
    title: str | None
    image_url: str | None
    price: Optional[Decimal]
    description: str | None
    published_at: Optional[datetime]


def _is_allowed_avito_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        host = parsed.netloc.lower()
        return host == ALLOWED_AVITO_DOMAIN or host.endswith("." + ALLOWED_AVITO_DOMAIN)
    except Exception:
        return False


def _safe_get_meta_content(soup: BeautifulSoup, *, property: str | None = None, name: str | None = None) -> Optional[str]:
    if property:
        tag = soup.find("meta", attrs={"property": property})
        if tag and tag.get("content"):
            return tag.get("content")
    if name:
        tag = soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            return tag.get("content")
    return None


def _parse_price_from_text(text: str | None) -> Optional[Decimal]:
    if not text:
        return None
    # Keep only digits, dots and commas, then normalize comma to dot
    allowed_chars = set("0123456789.,")
    cleaned_chars = []
    for ch in text:
        if ch in allowed_chars:
            cleaned_chars.append(ch)
    if not cleaned_chars:
        return None
    cleaned = "".join(cleaned_chars).replace(",", ".")
    # Remove multiple dots except the last
    # Simple approach: keep first dot for decimal part from the right
    if cleaned.count(".") > 1:
        parts = cleaned.split(".")
        cleaned = "".join(parts[:-1]).replace(".", "") + "." + parts[-1]
    try:
        return Decimal(cleaned)
    except Exception:
        return None


def fetch_avito_metadata(url: str) -> AvitoMetadata:
    if not _is_allowed_avito_url(url):
        raise ValueError("Only avito.ru domain is allowed")

    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=12)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Title
    title = _safe_get_meta_content(soup, property="og:title")

    # Image
    image_url = _safe_get_meta_content(soup, property="og:image")

    # Description
    description = _safe_get_meta_content(soup, name="description")

    # Price: meta[property="product:price:amount"] or itemprop="price"
    price_raw = _safe_get_meta_content(soup, property="product:price:amount")
    price: Optional[Decimal] = None
    if price_raw:
        price = _parse_price_from_text(price_raw)
    else:
        price_tag = soup.find(attrs={"itemprop": "price"})
        if price_tag is not None:
            # try content attribute first
            price = _parse_price_from_text(price_tag.get("content") or price_tag.get_text(strip=True))

    # Published at: meta[property="article:published_time"] or time[datetime]
    published_raw = _safe_get_meta_content(soup, property="article:published_time")
    published_at: Optional[datetime] = None
    if not published_raw:
        time_tag = soup.find("time")
        if time_tag is not None:
            published_raw = time_tag.get("datetime")
    if published_raw:
        try:
            published_at = date_parser.parse(published_raw)
        except Exception:
            published_at = None

    return AvitoMetadata(
        title=title or None,
        image_url=image_url or None,
        price=price,
        description=description or None,
        published_at=published_at,
    )


def upsert_listing_by_url(url: str) -> Listing:
    meta = fetch_avito_metadata(url)

    listing, created = Listing.objects.get_or_create(
        url=url,
        defaults={
            "title": meta.title or "",
            "image_url": meta.image_url or "",
            "price": meta.price,
            "description": meta.description or "",
            "published_at": meta.published_at,
        },
    )

    if not created:
        changed = False
        if meta.title is not None and listing.title != meta.title:
            listing.title = meta.title
            changed = True
        if meta.image_url is not None and listing.image_url != meta.image_url:
            listing.image_url = meta.image_url
            changed = True
        if meta.price is not None and listing.price != meta.price:
            listing.price = meta.price
            changed = True
        if meta.description is not None and listing.description != meta.description:
            listing.description = meta.description
            changed = True
        if meta.published_at is not None and listing.published_at != meta.published_at:
            listing.published_at = meta.published_at
            changed = True
        if changed:
            listing.save()

    return listing
