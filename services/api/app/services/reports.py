from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    PageBreak,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.schemas.order import OrderReportResponse


GREEN = colors.HexColor("#153F32")
MINT = colors.HexColor("#E9F2EE")
AMBER = colors.HexColor("#E9A23B")
INK = colors.HexColor("#23312C")
MUTED = colors.HexColor("#617068")
LINE = colors.HexColor("#D5E0DA")


def draw_footer(canvas: Canvas, document: BaseDocTemplate, report_reference: str) -> None:
    canvas.saveState()
    try:
        width, _ = A4
        canvas.setStrokeColor(LINE)
        canvas.line(18 * mm, 15 * mm, width - 18 * mm, 15 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(18 * mm, 9 * mm, f"CarbonIQ | {report_reference}")
        canvas.drawRightString(width - 18 * mm, 9 * mm, f"Page {document.page}")
    finally:
        canvas.restoreState()


def value_or_na(value: object | None, suffix: str = "") -> str:
    return "Not available" if value is None else f"{value}{suffix}"


def render_order_report_pdf(report: OrderReportResponse) -> bytes:
    """Render a deterministic, readable CarbonIQ simulated-order report."""
    buffer = BytesIO()
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=29,
            textColor=GREEN,
            alignment=TA_CENTER,
            spaceAfter=5 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=GREEN,
            spaceBefore=6 * mm,
            spaceAfter=3 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyMuted",
            parent=styles["BodyText"],
            fontSize=9,
            leading=13,
            textColor=MUTED,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCell",
            parent=styles["BodyText"],
            fontSize=8,
            leading=10,
            textColor=INK,
        )
    )

    document = BaseDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=22 * mm,
        title=f"CarbonIQ Report {report.order_reference}",
        author="CarbonIQ",
        subject="Simulated carbon-credit order report",
    )
    frame = Frame(
        document.leftMargin,
        document.bottomMargin,
        document.width,
        document.height,
        id="content",
    )
    document.addPageTemplates(
        [
            PageTemplate(
                id="report",
                frames=[frame],
                onPage=lambda canvas, doc: draw_footer(
                    canvas, doc, report.order_reference
                ),
            )
        ]
    )

    story = [
        Paragraph("CarbonIQ", styles["ReportTitle"]),
        Paragraph("SIMULATED CARBON-CREDIT ORDER REPORT", styles["Heading2"]),
        Spacer(1, 2 * mm),
        Table(
            [[Paragraph(escape(report.disclaimer), styles["BodyText"])]],
            colWidths=[document.width],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF2DC")),
                    ("BOX", (0, 0), (-1, -1), 1, AMBER),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ]
            ),
        ),
        Paragraph("Order summary", styles["Section"]),
    ]
    summary = [
        ["Order reference", report.order_reference, "Status", report.order_status.value],
        ["Buyer", report.buyer_organization, "Currency", report.currency],
        ["Order created", report.order_created_at.isoformat(), "Report version", report.report_version],
        ["Total credits", f"{report.total_credits:,.3f}", "Estimated impact", f"{report.estimated_carbon_impact_tonnes:,.3f} tCO2e"],
        ["Total cost", f"{report.currency} {report.total_cost_snapshot:,.2f}", "Cancelled", value_or_na(report.cancelled_at.isoformat() if report.cancelled_at else None)],
    ]
    summary_table = Table(summary, colWidths=[30 * mm, 60 * mm, 27 * mm, 57 * mm])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), MINT),
                ("BACKGROUND", (2, 0), (2, -1), MINT),
                ("TEXTCOLOR", (0, 0), (-1, -1), INK),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([summary_table, Paragraph("Allocation breakdown", styles["Section"])])

    allocation_rows = [["Project", "Vintage", "Quantity", "Unit price", "Line total", "Allocation"]]
    for item in report.allocations:
        allocation_rows.append(
            [
                Paragraph(escape(item.project_name), styles["TableCell"]),
                str(item.vintage),
                f"{item.quantity:,.3f}",
                f"{item.unit_price_snapshot:,.2f}",
                f"{item.line_total_snapshot:,.2f}",
                f"{item.allocation_percent:.2f}%",
            ]
        )
    allocation_table = Table(
        allocation_rows,
        repeatRows=1,
        colWidths=[54 * mm, 18 * mm, 25 * mm, 27 * mm, 27 * mm, 23 * mm],
    )
    allocation_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), GREEN),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, MINT]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(allocation_table)

    story.extend([PageBreak(), Paragraph("Project evidence snapshots", styles["Section"])])
    for item in report.allocations:
        evidence = [
            [
                Paragraph(label, styles["TableCell"]),
                Paragraph(escape(value_or_na(value)), styles["TableCell"]),
            ]
            for label, value in (
                ("Registry", item.registry),
                ("Methodology", item.methodology),
                ("Data as of", item.data_as_of),
                ("CarbonIQ score", item.carboniq_score),
                ("Quality score", item.quality_score),
                ("Risk score", item.risk_score),
                ("Score method", item.score_methodology_version),
            )
        ]
        story.append(Paragraph(escape(item.project_name), styles["Heading3"]))
        table = Table(evidence, colWidths=[38 * mm, 137 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), MINT),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(table)
        story.append(
            Paragraph(
                f"Source: {escape(item.source_url) if item.source_url else 'Not available'}",
                styles["BodyMuted"],
            )
        )
        if item.risk_signals:
            for signal in item.risk_signals:
                story.append(
                    Paragraph(
                        f"Risk [{escape(signal.severity)}] {escape(signal.code)}: "
                        f"{escape(signal.title)} - {escape(signal.message)}",
                        styles["BodyMuted"],
                    )
                )
        else:
            story.append(
                Paragraph(
                    "Risk signals: No active risk signals were captured.",
                    styles["BodyMuted"],
                )
            )
        story.append(Spacer(1, 3 * mm))

    if report.simulated_retirement_certificate:
        certificate = report.simulated_retirement_certificate
        story.extend(
            [
                Paragraph("Simulated retirement certificate", styles["Section"]),
                Paragraph(
                    f"Reference: {escape(certificate.reference)}<br/>"
                    f"Quantity: {certificate.quantity:,.3f} tCO2e<br/>"
                    f"Issued: {certificate.issued_at.isoformat()}<br/>"
                    f"{escape(certificate.statement)}",
                    styles["BodyText"],
                ),
            ]
        )

    story.append(Paragraph("Limitations", styles["Section"]))
    for limitation in report.limitations:
        story.append(Paragraph(f"- {escape(limitation)}", styles["BodyMuted"]))
    story.append(Spacer(1, 4 * mm))
    story.append(
        Paragraph(
            f"Generated at {report.generated_at.isoformat()}. {escape(report.disclaimer)}",
            styles["BodyMuted"],
        )
    )

    document.build(story)
    return buffer.getvalue()
