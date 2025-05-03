import pytest
from pathlib import Path
from src.harmony.services.export_pdf_report import generate_pdf_report
from harmony import create_instrument_from_list, example_instruments, match_instruments

@pytest.fixture
def sample_data(tmp_path):
    gad_7_norwegian = create_instrument_from_list(
        [
            "Følt deg nervøs, engstelig eller veldig stresset",
            "Ikke klart å slutte å bekymre deg eller kontrolleren bekymringene dine"
        ],
        instrument_name="GAD-7 Norwegian"
    )
    instruments = [
        example_instruments["CES_D English"],
        example_instruments["GAD-7 Portuguese"],
        gad_7_norwegian
    ]
    match_response = match_instruments(
        instruments,
        topics=["anxiety", "nervous", "difficulty", "scared", "unhappy", "sleep", "eating"]
    )
    return match_response, instruments, tmp_path

def test_high_threshold_creates_pdf(sample_data):
    match_response, instruments, tmp_path = sample_data
    out_file = tmp_path / "report_high_thresh.pdf"

    generate_pdf_report(match_response, instruments, filename=str(out_file), threshold=0.99)

    assert out_file.exists(), "PDF file was not created"
    assert out_file.stat().st_size > 0, "PDF file is empty"

def test_default_threshold_creates_pdf(sample_data):
    match_response, instruments, tmp_path = sample_data
    out_file = tmp_path / "report_default_thresh.pdf"

    generate_pdf_report(match_response, instruments, filename=str(out_file))

    assert out_file.exists(), "PDF file was not created"
    assert out_file.stat().st_size > 0, "PDF file is empty"
