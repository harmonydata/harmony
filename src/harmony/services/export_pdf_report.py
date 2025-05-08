import os
from datetime import datetime
from typing import List

from fpdf import FPDF

from harmony.schemas.requests.text import Instrument
from harmony.schemas.responses.text import MatchResponse


def sanitize(text: str) -> str:
    return text.encode("latin-1", "ignore").decode("latin-1")


class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, sanitize("Harmony Match Report"), ln=True, align="C")
        self.set_font("Arial", "", 10)
        self.cell(
            0, 10,
            sanitize(f"Generated on {datetime.now():%Y-%m-%d %H:%M:%S}"),
            ln=True, align="C"
        )
        self.ln(5)

    def chapter_title(self, title: str):
        self.set_font("Arial", "B", 11)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 8, sanitize(title), ln=True, fill=True)
        self.ln(2)


def generate_pdf_report(
        match_response: MatchResponse,
        instruments: List[Instrument],
        filename: str = "harmony_report.pdf",
        threshold: float = 0.5
):
    """
    Generate a PDF of matched questions.
    :param match_response: the MatchResponse from match_instruments(...)
    :param instruments: the list of Instrument objects you passed in
    :param filename: output path
    :param threshold: only show matches with |score| >= threshold
    """
    pdf = PDFReport()
    pdf.add_page()

    # 1) Map question-index → (instrument_name, question_no)
    question_meta = {}
    idx = 0
    for inst in instruments:
        for q in inst.questions:
            question_meta[idx] = (inst.instrument_name, q.question_no)
            idx += 1

    # 2) Collect & sort all pairs
    raw_matches = []
    questions = match_response.questions
    sim = match_response.similarity_with_polarity
    for i in range(sim.shape[0]):
        for j in range(sim.shape[1]):
            if i != j and sim[i][j] > 0:
                raw_matches.append((i, j, sim[i][j]))
    raw_matches.sort(key=lambda x: abs(x[2]), reverse=True)

    # 3) Count how many pass the threshold
    displayed = sum(1 for (_, _, s) in raw_matches if abs(s) >= threshold)

    # 4) Chapter title with count and threshold
    pct = int(threshold * 100)
    pdf.chapter_title(f"Matched Questions ({displayed}) with Threshold: {pct}%")

    # 5) Table header
    w1, w2, w3 = 60, 20, 110
    pdf.set_font("Arial", "B", 10)
    pdf.cell(w1, 8, sanitize("Instrument"), border=1)
    pdf.cell(w2, 8, sanitize("Nr."), border=1)
    pdf.cell(w3, 8, sanitize("Question"), border=1)
    pdf.ln()

    # 6) Render each passing match
    total_w = w1 + w2 + w3
    for i, j, score in raw_matches:
        if abs(score) >= threshold:
            inst1, q1_no = question_meta[i]
            inst2, q2_no = question_meta[j]
            q1 = questions[i]
            q2 = questions[j]

            # — Row 1: only top + outer verticals
            pdf.set_font("Arial", "", 9)
            pdf.cell(w1, 6, sanitize(inst1), border='TLR')
            pdf.cell(w2, 6, sanitize(str(q1_no)), border='TR')
            pdf.multi_cell(w3, 6, sanitize(q1.question_text), border='TR')

            # — Row 2: verticals + bottom (gives the thin line)
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Arial", "", 9)
            pdf.cell(w1, 6, sanitize(inst2), border='LRB')
            pdf.cell(w2, 6, sanitize(str(q2_no)), border='RB')
            pdf.multi_cell(w3, 6, sanitize(q2.question_text), border='RB')

            # — Score row: full width, only outer verticals + bottom
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Arial", "I", 8)
            pdf.cell(
                total_w, 6,
                sanitize(f"Match Score: {round(score * 100)}%"),
                border='LRB',
                ln=True
            )

            pdf.ln(4)

    # 7) Save
    out = os.path.abspath(filename)
    pdf.output(out)
    return out
