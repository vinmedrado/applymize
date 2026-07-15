import re
from sqlalchemy.orm import Session
from backend.models.tenant import Tenant


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower()).strip("-")
    return slug or "tenant"


def unique_slug(db: Session, name: str) -> str:
    base = slugify(name)
    slug = base
    index = 2
    while db.query(Tenant).filter(Tenant.slug == slug).first():
        slug = f"{base}-{index}"
        index += 1
    return slug
