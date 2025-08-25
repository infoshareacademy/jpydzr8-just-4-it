from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .db import get_db
from .models import Reservation
from .schemas import ReservationCreate, ReservationOut

router = APIRouter(prefix="/api/reservations", tags=["reservations"])

@router.get("", response_model=List[ReservationOut])
def list_reservations(date_from: Optional[str] = None, date_to: Optional[str] = None, seat_id: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Reservation)
    if seat_id:
        q = q.filter(Reservation.seat_id == seat_id)
    if date_from:
        q = q.filter(Reservation.date >= date_from)
    if date_to:
        q = q.filter(Reservation.date <= date_to)
    rows = q.order_by(Reservation.date.asc()).all()
    out = []
    for r in rows:
        out.append({
            "id": r.id,
            "seat_id": r.seat_id,
            "date": r.date,
            "name": r.name,
            "email": r.email,
            "notes": r.notes,
            "created_at": (r.created_at.isoformat() if isinstance(r.created_at, datetime) else str(r.created_at))
        })
    return out

@router.get("/check/{seat_id}/{date}")
def check(seat_id: str, date: str, db: Session = Depends(get_db)):
    e = db.query(Reservation).filter(and_(Reservation.seat_id == seat_id, Reservation.date == date)).first()
    return {"seat_id": seat_id, "date": date, "reserved": bool(e), "reservation_id": e.id if e else None}

@router.post("", response_model=ReservationOut)
def create_reservation(p: ReservationCreate, db: Session = Depends(get_db)):
    e = db.query(Reservation).filter(and_(Reservation.seat_id == p.seat_id, Reservation.date == p.date)).first()
    if e:
        raise HTTPException(status_code=409, detail="Seat already reserved for that date")
    rid = f"R-{int(datetime.utcnow().timestamp())}"
    r = Reservation(id=rid, seat_id=p.seat_id, date=p.date, name=p.name, email=p.email, notes=p.notes or "")
    db.add(r); db.commit(); db.refresh(r)
    return {
        "id": r.id, "seat_id": r.seat_id, "date": r.date, "name": r.name, "email": r.email,
        "notes": r.notes, "created_at": (r.created_at.isoformat() if isinstance(r.created_at, datetime) else str(r.created_at))
    }

@router.put("/{reservation_id}", response_model=ReservationOut)
def update_reservation(reservation_id: str, seat_id: Optional[str] = None, date: Optional[str] = None, name: Optional[str] = None, email: Optional[str] = None, notes: Optional[str] = None, db: Session = Depends(get_db)):
    r = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if seat_id is not None:
        r.seat_id = seat_id
    if date is not None:
        # sprawdź kolizję daty+seat
        clash = db.query(Reservation).filter(and_(Reservation.seat_id == (seat_id or r.seat_id), Reservation.date == date, Reservation.id != r.id)).first()
        if clash:
            raise HTTPException(status_code=409, detail="Seat already reserved for that date")
        r.date = date
    if name is not None:
        r.name = name
    if email is not None:
        r.email = email
    if notes is not None:
        r.notes = notes
    db.commit(); db.refresh(r)
    return {
        "id": r.id, "seat_id": r.seat_id, "date": r.date, "name": r.name, "email": r.email,
        "notes": r.notes, "created_at": (r.created_at.isoformat() if isinstance(r.created_at, datetime) else str(r.created_at))
    }

@router.delete("/{reservation_id}")
def cancel(reservation_id: str, db: Session = Depends(get_db)):
    r = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Reservation not found")
    db.delete(r); db.commit()
    return {"ok": True, "deleted": reservation_id}
