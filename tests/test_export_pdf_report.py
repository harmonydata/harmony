import PyPDF2
from pathlib import Path
import pytest

from harmony.services.export_pdf_report import generate_pdf_report
from harmony import create_instrument_from_list, example_instruments, match_instruments

@pytest.fixture
def sample_data(tmp_path):
    gad_7_norwegian = create_instrument_from_list(
        ["Følt deg nervøs, engstelig eller veldig stresset",
         "Ikke klart å slutte å bekymre deg eller kontrolleren bekymringene dine"],
        instrument_name="GAD-7 Norwegian"
    )
    instruments = [
        example_instruments["CES_D English"],
        example_instruments["GAD-7 Portuguese"],
        gad_7_norwegian
    ]
    match_response = match_instruments(
        instruments,
        topics=[
            "anxiety", "nervous", "difficulty",
            "scared", "unhappy", "sleep", "eating"
        ]
    )
    return match_response, instruments, tmp_path

def extract_text(pdf_path: Path) -> str:
    reader = PyPDF2.PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def test_high_threshold_yields_no_matches(sample_data):
    match_response, instruments, tmp_path = sample_data
    out_pdf = tmp_path / "high_thresh.pdf"
    generate_pdf_report(
        match_response,
        instruments,
        filename=str(out_pdf),
        threshold=0.99
    )
    assert out_pdf.exists() and out_pdf.stat().st_size > 0
    text = extract_text(out_pdf)
    assert "Threshold: 99%" in text
    assert "Matched Questions (0)" in text

def test_default_threshold_yields_some_matches(sample_data):
    match_response, instruments, tmp_path = sample_data
    out_pdf = tmp_path / "default_thresh.pdf"
    # omit threshold → uses default 0.5
    generate_pdf_report(
        match_response,
        instruments,
        filename=str(out_pdf)
    )
    assert out_pdf.exists() and out_pdf.stat().st_size > 0
    text = extract_text(out_pdf)
    assert "Threshold: 50%" in text
    header_line = next(
        line for line in text.splitlines() if "Matched Questions" in line
    )
    count_str = header_line.split("Matched Questions (")[1].split(")")[0]
    assert count_str.isdigit() and int(count_str) > 0
