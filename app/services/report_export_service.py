import csv
import io
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.notice import Notice
from app.models.client import Client
from app.models.notice_risk_metadata import NoticeRiskMetadata
from app.models.user import User


def export_reports(db: Session, report_type: str):

    if report_type == "high-risk":
        return export_high_risk(db)

    if report_type == "overdue":
        return export_overdue(db)

    if report_type == "client-summary":
        return export_client_summary(db)

    if report_type == "section-summary":
        return export_section_summary(db)

    if report_type == "workload":
        return export_workload(db)

    raise ValueError("Invalid report type")


# -----------------------------
# High Risk Report
# -----------------------------

def export_high_risk(db: Session):

    results = (
        db.query(
            Notice.notice_number,
            Client.name,
            Notice.section_reference,
            Notice.due_date,
            NoticeRiskMetadata.risk_score,
        )
        .join(Client, Client.id == Notice.client_id)
        .join(
            NoticeRiskMetadata,
            NoticeRiskMetadata.notice_id == Notice.id
        )
        .filter(NoticeRiskMetadata.risk_score >= 3)
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Notice",
        "Client",
        "Section",
        "Due Date",
        "Risk Score"
    ])

    for r in results:
        writer.writerow([
            r.notice_number,
            r.name,
            r.section_reference,
            r.due_date,
            r.risk_score
        ])

    output.seek(0)
    return output


# -----------------------------
# Overdue Notices
# -----------------------------

def export_overdue(db: Session):

    today = date.today()

    results = (
        db.query(
            Notice.notice_number,
            Client.name,
            Notice.section_reference,
            Notice.due_date
        )
        .join(Client, Client.id == Notice.client_id)
        .filter(Notice.due_date < today)
        .filter(Notice.status != "closed")
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Notice",
        "Client",
        "Section",
        "Due Date"
    ])

    for r in results:
        writer.writerow([
            r.notice_number,
            r.name,
            r.section_reference,
            r.due_date
        ])

    output.seek(0)
    return output


# -----------------------------
# Client Summary
# -----------------------------

def export_client_summary(db: Session):

    results = (
        db.query(
            Client.name,
            func.count(Notice.id).label("total")
        )
        .join(Notice, Notice.client_id == Client.id)
        .group_by(Client.name)
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Client",
        "Total Notices"
    ])

    for r in results:
        writer.writerow([
            r.name,
            r.total
        ])

    output.seek(0)
    return output


# -----------------------------
# Section Summary
# -----------------------------

def export_section_summary(db: Session):

    results = (
        db.query(
            Notice.section_reference,
            func.count(Notice.id)
        )
        .group_by(Notice.section_reference)
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Section",
        "Notices"
    ])

    for r in results:
        writer.writerow([
            r.section_reference,
            r[1]
        ])

    output.seek(0)
    return output


# -----------------------------
# Workload Report
# -----------------------------

def export_workload(db: Session):

    results = (
        db.query(
            User.full_name,
            func.count(Notice.id)
        )
        .join(Notice, Notice.assigned_to == User.id)
        .group_by(User.full_name)
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "CA Name",
        "Assigned Notices"
    ])

    for r in results:
        writer.writerow([
            r.full_name,
            r[1]
        ])

    output.seek(0)
    return output