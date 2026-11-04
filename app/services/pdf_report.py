"""PDF report generation service for typing test evaluations.

Uses ReportLab to generate a clean, official evaluation report containing:
- Candidate name & roll number
- Test metrics: WPM, Accuracy, KDPH, Errors, Time Taken
- Assigned reference paragraph (as-is)
- Candidate typed paragraph (as-is)
"""
import os
import sys
import html
import subprocess
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


def generate_typing_report(output_path: str, data: dict) -> str:
    """Generate a comprehensive typing evaluation PDF report.

    Parameters
    ----------
    output_path : str
        The destination file path for the PDF.
    data : dict
        Keys:
            student_name: str
            student_roll: str
            wpm: float
            accuracy: float
            kdph: float
            errors: int
            time_taken: int
            total_keystrokes: int
            correct_keystrokes: int
            paragraph_title: str
            assigned_paragraph: str
            typed_text: str
            submission_time: str (optional)

    Returns
    -------
    str
        The absolute path to the generated PDF.
    """
    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(out_file),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1e3a8a"),
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#334155"),
    )

    sub_sub_style = ParagraphStyle(
        "ReportCategory",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748b"),
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#0f172a"),
        alignment=TA_LEFT,
    )

    ref_body_style = ParagraphStyle(
        "RefBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#1e293b"),
        alignment=TA_JUSTIFY,
    )

    label_style = ParagraphStyle(
        "TableLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#475569"),
    )

    value_style = ParagraphStyle(
        "TableValue",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#0f172a"),
    )

    metric_title_style = ParagraphStyle(
        "MetricTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#475569"),
    )

    metric_val_style = ParagraphStyle(
        "MetricValue",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=19,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1e3a8a"),
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("DELHI TECHNOLOGICAL UNIVERSITY", title_style))
    story.append(Spacer(1, 3))
    story.append(Paragraph("TYPING TEST EVALUATION REPORT", subtitle_style))
    story.append(Spacer(1, 2))
    submission_dt = data.get("submission_time") or datetime.now().strftime("%d-%b-%Y  %I:%M:%S %p")
    story.append(Paragraph(f"Issued on: {submission_dt}", sub_sub_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=14))

    # 2. Candidate Information Table
    student_name = data.get("student_name", "N/A")
    student_roll = data.get("student_roll", "N/A")
    duration = data.get("time_taken", 60)
    mins, secs = divmod(duration, 60)
    time_str = f"{mins}m {secs}s" if mins else f"{secs}s"
    para_title = data.get("paragraph_title", "Typing Exercise")

    cand_table_data = [
        [
            Paragraph("CANDIDATE NAME", label_style),
            Paragraph(html.escape(student_name), value_style),
            Paragraph("TEST DURATION", label_style),
            Paragraph(time_str, value_style),
        ],
        [
            Paragraph("STUDENT ID / ROLL NO", label_style),
            Paragraph(html.escape(student_roll), value_style),
            Paragraph("EXAM STATUS", label_style),
            Paragraph("COMPLETED", ParagraphStyle("Success", parent=value_style, textColor=colors.HexColor("#16a34a"))),
        ],
        [
            Paragraph("ASSIGNED PARAGRAPH", label_style),
            Paragraph(html.escape(para_title), value_style),
            Paragraph("TEST DATE", label_style),
            Paragraph(datetime.now().strftime("%d-%m-%Y"), value_style),
        ],
    ]

    cand_table = Table(cand_table_data, colWidths=[130, 140, 110, 150])
    cand_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(cand_table)
    story.append(Spacer(1, 14))

    # 3. Performance Metrics Grid (WPM, Accuracy, KDPH, Errors)
    wpm = float(data.get("wpm", 0.0))
    acc = float(data.get("accuracy", 0.0))
    kdph = float(data.get("kdph", 0.0))
    errors = int(data.get("errors", 0))
    total_keys = int(data.get("total_keystrokes", 0))

    metrics_data = [
        [
            Paragraph("NET SPEED", metric_title_style),
            Paragraph("ACCURACY", metric_title_style),
            Paragraph("KDPH (DEPRESSIONS/HR)", metric_title_style),
            Paragraph("TOTAL ERRORS", metric_title_style),
            Paragraph("KEYSTROKES", metric_title_style),
        ],
        [
            Paragraph(f"{wpm:.1f} WPM", ParagraphStyle("WpmVal", parent=metric_val_style, textColor=colors.HexColor("#16a34a"))),
            Paragraph(f"{acc:.1f}%", ParagraphStyle("AccVal", parent=metric_val_style, textColor=colors.HexColor("#2563eb"))),
            Paragraph(f"{kdph:,.1f}", ParagraphStyle("KdphVal", parent=metric_val_style, textColor=colors.HexColor("#d97706"))),
            Paragraph(str(errors), ParagraphStyle("ErrVal", parent=metric_val_style, textColor=colors.HexColor("#dc2626"))),
            Paragraph(str(total_keys), ParagraphStyle("KeysVal", parent=metric_val_style, textColor=colors.HexColor("#475569"))),
        ],
    ]

    metrics_table = Table(metrics_data, colWidths=[106, 106, 116, 101, 101])
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ffffff")),
        ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#93c5fd")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 3),
        ("TOPPADDING", (0, 1), (-1, 1), 3),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 10),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 16))

    # 4. Assigned Reference Paragraph
    story.append(Paragraph("1. Assigned Reference Paragraph", section_heading))
    assigned_text = data.get("assigned_paragraph", "").strip()
    safe_assigned = html.escape(assigned_text).replace("\n", "<br/>") or "<i>(No reference text assigned)</i>"
    
    ref_table = Table(
        [[Paragraph(safe_assigned, ref_body_style)]],
        colWidths=[530],
    )
    ref_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(ref_table)
    story.append(Spacer(1, 14))

    # 5. Candidate's Typed Paragraph (Space where user typing is printed)
    story.append(Paragraph("2. Candidate's Typed Submission", section_heading))
    typed_raw = data.get("typed_text", "").strip()
    if typed_raw:
        safe_typed = html.escape(typed_raw).replace("\n", "<br/>")
    else:
        safe_typed = "<i>(No text typed by candidate during the test)</i>"

    typed_table = Table(
        [[Paragraph(safe_typed, body_style)]],
        colWidths=[530],
    )
    typed_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(typed_table)

    # Build the document
    doc.build(story)
    return str(out_file)


def open_pdf_file(filepath: str) -> bool:
    """Open the PDF file with the system's default viewer."""
    try:
        path = os.path.abspath(filepath)
        if sys.platform.startswith("win"):
            os.startfile(path)
            return True
        elif sys.platform.startswith("darwin"):
            subprocess.run(["open", path], check=False)
            return True
        else:
            subprocess.run(["xdg-open", path], check=False)
            return True
    except Exception:
        return False

