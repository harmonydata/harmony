import os
import io
from datetime import datetime
from typing import List, Optional, Tuple
import tempfile
from fpdf import FPDF

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    GRAPHICS_AVAILABLE = True
except ImportError:
    GRAPHICS_AVAILABLE = False

from harmony.schemas.requests.text import Instrument
from harmony.schemas.responses.text import MatchResponse

def sanitize(text: str) -> str:
    """Sanitizer text for pdf output, handling None values and encoding issues."""
    if text is None:
        return ""
    return str(text).encode("latin-1", "ignore").decode("latin-1")

class HarmonyPDFReport(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Arial", "B", 16)
        self.set_text_color(31, 81, 155) 
        self.cell(0, 12, sanitize("Harmony Harmonisation Report"), ln=True, align="C")
        self.set_text_color(0, 0, 0) 
        self.set_font("Arial", "", 10)
        self.cell(
            0, 8,
            sanitize(f"Generated on {datetime.now():%Y-%m-%d %H:%M:%S}"),
            ln=True, align="C"
        )
        self.ln(8)

    def footer(self):
        """Add page footer with page numbers."""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        self.set_text_color(0, 0, 0)
    
    def chapter_title(self, title: str, color: Tuple[int, int, int] = (31, 81, 155)):
        """Add a chapter title with colored background."""
        self.set_font("Arial", "B", 14)
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, sanitize(title), ln=True, fill=True, align="L")
        self.set_text_color(0, 0, 0)
        self.ln(5)

    def add_image_from_matplotlib(self, fig, x=None, y=None, w=0, h=0):
        """Add matplotlib figure to PDF."""
        if not GRAPHICS_AVAILABLE:
            return
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            fig.savefig(tmp_file.name, format="png", dpi=150, bbox_inches="tight")
            temp_filename = tmp_file.name

        try:
            # Add to PDF
            if x is None:
                x = self.get_x()
            if y is None:
                y = self.get_y()
                
            self.image(temp_filename, x, y, w, h)
        finally:
            # Clean up
            try:
                os.remove(temp_filename)
            except:
                pass
            plt.close(fig)

    def add_executive_summary(self, stats: dict):
        """Add executive summary with key metrics."""
        self.chapter_title("Executive Summary")
        
        # Key metrics in boxes
        metrics = [
            ("Total Questions Analyzed", stats['total_questions']),
            ("Questions Successfully Harmonised", stats['harmonised_questions']),
            ("Harmonisation Success Rate", f"{stats['success_rate']:.1f}%"),
            ("Average Match Score", f"{stats['avg_match_score']:.1f}%"),
        ]
        
        box_width = 90
        box_height = 25
        x_start = 15
        y_start = self.get_y()
        
        for i, (label, value) in enumerate(metrics):
            x = x_start + (i % 2) * (box_width + 10)
            y = y_start + (i // 2) * (box_height + 5)
            
            self.set_xy(x, y)
            
            # Box border
            self.set_fill_color(240, 248, 255)
            self.rect(x, y, box_width, box_height, 'F')
            self.rect(x, y, box_width, box_height, 'D')
            
            # Label
            self.set_xy(x + 2, y + 3)
            self.set_font("Arial", "", 9)
            self.set_text_color(100, 100, 100)
            self.cell(box_width - 4, 8, sanitize(label), align="C")
            
            # Value
            self.set_xy(x + 2, y + 12)
            self.set_font("Arial", "B", 14)
            self.set_text_color(31, 81, 155)
            self.cell(box_width - 4, 10, sanitize(str(value)), align="C")
            self.set_text_color(0, 0, 0)
        
        self.set_y(y_start + 60)

    def add_instruments_overview(self, instruments: List[Instrument], match_stats: dict):
        """Enhanced instruments overview with statistics."""
        self.chapter_title("Instruments Overview")
        
        # Table header
        self.set_font("Arial", "B", 10)
        self.set_fill_color(230, 230, 230)
        
        col_widths = [60, 30, 40, 60]
        headers = ["Instrument Name", "Questions", "Matches Found", "Avg Match Score"]
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, sanitize(header), border=1, fill=True)
        self.ln()
        
        # Table rows
        self.set_font("Arial", "", 9)
        self.set_fill_color(255, 255, 255)
        
        for inst in instruments:
            name = inst.instrument_name or "Unnamed Instrument"
            q_count = len(inst.questions) if inst.questions else 0
            
            # Get stats for this instrument
            inst_matches = match_stats.get('by_instrument', {}).get(name, {})
            matches_found = inst_matches.get('matches', 0)
            avg_score = inst_matches.get('avg_score', 0)
            
            # Truncate long names
            display_name = name[:22] + "..." if len(name) > 25 else name
            
            self.cell(col_widths[0], 8, sanitize(display_name), border=1)
            self.cell(col_widths[1], 8, sanitize(str(q_count)), border=1, align="C")
            self.cell(col_widths[2], 8, sanitize(str(matches_found)), border=1, align="C")
            self.cell(col_widths[3], 8, sanitize(f"{avg_score:.1f}%"), border=1, align="C")
            self.ln()
        
        self.ln(5)


def create_match_distribution_chart(raw_matches: List[Tuple], threshold: float):
    """Create a histogram of match score distribution."""
    if not GRAPHICS_AVAILABLE:
        return None
        
    scores = [abs(score) for _, _, score in raw_matches]
    
    if not scores:
        return None
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    try:
        # Create histogram
        n, bins, patches = ax.hist(scores, bins=min(20, len(set(scores))), 
                                  alpha=0.7, color='skyblue', edgecolor='black')
        
        # Color bars based on threshold
        for i, patch in enumerate(patches):
            if bins[i] >= threshold:
                patch.set_facecolor('lightgreen')
            else:
                patch.set_facecolor('lightcoral')
        
        # Add threshold line
        ax.axvline(threshold, color='red', linestyle='--', linewidth=2, 
                   label=f'Threshold ({threshold:.0%})')
        
        ax.set_xlabel('Match Score')
        ax.set_ylabel('Number of Question Pairs')
        ax.set_title('Distribution of Match Scores')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig
    except Exception:
        plt.close(fig)
        return None


def create_instrument_heatmap(instruments: List[Instrument], similarity_matrix, question_meta: dict):
    """Create a heatmap showing matches between instruments."""
    if not GRAPHICS_AVAILABLE or len(instruments) < 2:
        return None
        
    try:
        # Create instrument-to-instrument match matrix
        inst_names = [inst.instrument_name or f"Instrument {i+1}" 
                      for i, inst in enumerate(instruments)]
        
        # Initialize matrix
        n_inst = len(instruments)
        inst_matrix = np.zeros((n_inst, n_inst))
        inst_counts = np.zeros((n_inst, n_inst))
        
        # Map questions to instruments
        q_to_inst = {}
        q_idx = 0
        for inst_idx, inst in enumerate(instruments):
            for _ in (inst.questions or []):
                q_to_inst[q_idx] = inst_idx
                q_idx += 1
        
        # Fill matrix with average scores between instruments
        for i in range(similarity_matrix.shape[0]):
            for j in range(similarity_matrix.shape[1]):
                if i != j and similarity_matrix[i][j] > 0:
                    inst_i = q_to_inst.get(i, 0)
                    inst_j = q_to_inst.get(j, 0)
                    if inst_i != inst_j:
                        inst_matrix[inst_i][inst_j] += similarity_matrix[i][j]
                        inst_counts[inst_i][inst_j] += 1
        
        # Calculate averages
        for i in range(n_inst):
            for j in range(n_inst):
                if inst_counts[i][j] > 0:
                    inst_matrix[i][j] /= inst_counts[i][j]
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Truncate long names for display
        display_names = [name[:15] + "..." if len(name) > 15 else name 
                         for name in inst_names]
        
        sns.heatmap(inst_matrix, annot=True, fmt='.2f', cmap='RdYlBu_r',
                    xticklabels=display_names, yticklabels=display_names,
                    ax=ax, cbar_kws={'label': 'Average Match Score'})
        
        ax.set_title('Cross-Instrument Harmonisation Heatmap')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        return fig
    except Exception:
        return None


def calculate_harmonisation_statistics(
    match_response: MatchResponse,
    instruments: List[Instrument],
    raw_matches: List[Tuple],
    threshold: float
) -> dict:
    """Calculate comprehensive statistics about the harmonisation."""
    
    # Basic counts
    total_questions = sum(len(inst.questions or []) for inst in instruments)
    total_possible_matches = len(raw_matches)
    successful_matches = sum(1 for _, _, score in raw_matches if abs(score) >= threshold)
    
    # Questions that have at least one match above threshold
    questions_with_matches = set()
    for i, j, score in raw_matches:
        if abs(score) >= threshold:
            questions_with_matches.add(i)
            questions_with_matches.add(j)
    
    harmonised_questions = len(questions_with_matches)
    
    # Average scores
    successful_scores = [abs(score) for _, _, score in raw_matches if abs(score) >= threshold]
    
    avg_match_score = (sum(successful_scores) / len(successful_scores) * 100) if successful_scores else 0
    success_rate = (harmonised_questions / total_questions * 100) if total_questions > 0 else 0
    
    # Per-instrument statistics
    by_instrument = {}
    question_meta = {}
    idx = 0
    
    for inst_num, inst in enumerate(instruments):
        inst_name = inst.instrument_name or f"Instrument {inst_num + 1}"
        inst_questions = set(range(idx, idx + len(inst.questions or [])))
        
        # Count matches for this instrument
        inst_matches = sum(1 for i, j, score in raw_matches 
                          if abs(score) >= threshold and (i in inst_questions or j in inst_questions))
        
        # Average score for this instrument
        inst_scores = [abs(score) for i, j, score in raw_matches 
                      if abs(score) >= threshold and (i in inst_questions or j in inst_questions)]
        inst_avg_score = (sum(inst_scores) / len(inst_scores) * 100) if inst_scores else 0
        
        by_instrument[inst_name] = {
            'matches': inst_matches,
            'avg_score': inst_avg_score
        }
        
        for q_num, q in enumerate(inst.questions or []):
            question_meta[idx] = (inst_name, getattr(q, 'question_no', q_num + 1))
            idx += 1
    
    return {
        'total_questions': total_questions,
        'total_possible_matches': total_possible_matches,
        'successful_matches': successful_matches,
        'harmonised_questions': harmonised_questions,
        'success_rate': success_rate,
        'avg_match_score': avg_match_score,
        'by_instrument': by_instrument,
        'question_meta': question_meta
    }


def generate_pdf_report(
        match_response: MatchResponse,
        instruments: List[Instrument],
        filename: str = "harmony_report.pdf",
        threshold: float = 0.5
) -> str:
    """
    ORIGINAL FUNCTION - Maintains backward compatibility with existing tests.
    Generate a PDF of matched questions (basic version).
    
    :param match_response: the MatchResponse from match_instruments(...)
    :param instruments: the list of Instrument objects you passed in
    :param filename: output path
    :param threshold: only show matches with |score| >= threshold
    :return: absolute path to the generated PDF file
    """
    if not instruments or not match_response:
        raise ValueError("Instruments and match_response cannot be empty")
    
    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, sanitize("Harmony Match Report"), ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(
        0, 10,
        sanitize(f"Generated on {datetime.now():%Y-%m-%d %H:%M:%S}"),
        ln=True, align="C"
    )
    pdf.ln(5)

    # 1) Map question-index → (instrument_name, question_no)
    question_meta = {}
    idx = 0
    for inst in instruments:
        inst_name = inst.instrument_name or f"Instrument {idx + 1}"
        for q_num, q in enumerate(inst.questions or []):
            question_meta[idx] = (inst_name, getattr(q, 'question_no', q_num + 1))
            idx += 1

    # 2) Collect & sort all pairs
    raw_matches = []
    questions = match_response.questions
    sim = match_response.similarity_with_polarity
    
    if sim is None or questions is None:
        raise ValueError("Invalid match response: missing similarity matrix or questions")
    
    for i in range(sim.shape[0]):
        for j in range(sim.shape[1]):
            if i != j and sim[i][j] > 0:
                raw_matches.append((i, j, sim[i][j]))
    
    raw_matches.sort(key=lambda x: abs(x[2]), reverse=True)

    # 3) Count how many pass the threshold
    displayed = sum(1 for (_, _, s) in raw_matches if abs(s) >= threshold)

    # 4) Chapter title with count and threshold
    pct = int(threshold * 100)
    pdf.set_font("Arial", "B", 11)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 8, sanitize(f"Matched Questions ({displayed}) with Threshold: {pct}%"), 
             ln=True, fill=True)
    pdf.ln(2)

    if displayed == 0:
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, sanitize(f"No matches found above {pct}% threshold."), ln=True)
    else:
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
                inst1, q1_no = question_meta.get(i, ("Unknown", "?"))
                inst2, q2_no = question_meta.get(j, ("Unknown", "?"))
                
                if i < len(questions) and j < len(questions):
                    q1 = questions[i]
                    q2 = questions[j]

                    # Row 1: Question 1
                    pdf.set_font("Arial", "", 9)
                    pdf.cell(w1, 6, sanitize(str(inst1)[:25]), border='TLR')
                    pdf.cell(w2, 6, sanitize(str(q1_no)), border='TR')
                    
                    # Handle multi-line text
                    q1_text = sanitize(q1.question_text or "No text available")
                    if len(q1_text) > 50:
                        q1_text = q1_text[:47] + "..."
                    
                    pdf.multi_cell(w3, 6, q1_text, border='TR')

                    # Row 2: Question 2
                    pdf.set_x(pdf.l_margin)
                    pdf.cell(w1, 6, sanitize(str(inst2)[:25]), border='LRB')
                    pdf.cell(w2, 6, sanitize(str(q2_no)), border='RB')
                    
                    q2_text = sanitize(q2.question_text or "No text available")
                    if len(q2_text) > 50:
                        q2_text = q2_text[:47] + "..."
                    
                    pdf.multi_cell(w3, 6, q2_text, border='RB')

                    # Score row
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
    try:
        out = os.path.abspath(filename)
        pdf.output(out)
        return out
    except Exception as e:
        raise IOError(f"Failed to save PDF report: {str(e)}")


def generate_harmony_pdf_report(
    match_response: MatchResponse,
    instruments: List[Instrument],
    filename: str = "harmony_harmonisation_report.pdf",
    threshold: float = 0.5,
    include_graphics: bool = True,
    max_matches_displayed: int = 50
) -> str:
    """
    NEW ENHANCED FUNCTION for Issue #53.
    Generate a comprehensive PDF harmonisation report with graphics and detailed statistics.
    
    This creates a human-readable report that's easier to understand than the Excel matrix,
    includes graphics and comprehensive statistics about harmonisation success.
    
    :param match_response: MatchResponse from match_instruments()
    :param instruments: List of Instrument objects
    :param filename: Output PDF filename
    :param threshold: Minimum match score threshold (0.0 to 1.0)
    :param include_graphics: Whether to include charts and graphs
    :param max_matches_displayed: Maximum number of individual matches to show
    :return: Absolute path to generated PDF
    """
    
    if not instruments or not match_response:
        raise ValueError("Instruments and match_response cannot be empty")
    
    # Prepare data
    questions = match_response.questions
    sim = match_response.similarity_with_polarity
    
    if sim is None or questions is None:
        raise ValueError("Invalid match response: missing similarity matrix or questions")
    
    # Collect all matches
    raw_matches = []
    for i in range(sim.shape[0]):
        for j in range(sim.shape[1]):
            if i != j and sim[i][j] > 0:
                raw_matches.append((i, j, sim[i][j]))
    
    raw_matches.sort(key=lambda x: abs(x[2]), reverse=True)
    
    # Calculate statistics
    stats = calculate_harmonisation_statistics(match_response, instruments, raw_matches, threshold)
    
    # Create PDF report
    pdf = HarmonyPDFReport()
    pdf.add_page()
    
    # Executive Summary
    pdf.add_executive_summary(stats)
    
    # Add graphics if requested and available
    if include_graphics and GRAPHICS_AVAILABLE:
        try:
            # Page break for charts
            pdf.add_page()
            
            # Match distribution chart
            pdf.chapter_title("Match Score Distribution")
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 8, sanitize("This chart shows how match scores are distributed across all question pairs."), ln=True)
            pdf.cell(0, 8, sanitize(f"Green bars show matches above the {threshold:.0%} threshold."), ln=True)
            pdf.ln(5)
            
            fig1 = create_match_distribution_chart(raw_matches, threshold)
            if fig1:
                pdf.add_image_from_matplotlib(fig1, x=15, w=180)
                pdf.ln(100)
            
            # Instrument heatmap
            if len(instruments) > 1:
                pdf.chapter_title("Cross-Instrument Harmonisation")
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 8, sanitize("This heatmap shows average match scores between different instruments."), ln=True)
                pdf.cell(0, 8, sanitize("Darker colors indicate stronger harmonisation potential."), ln=True)
                pdf.ln(5)
                
                fig2 = create_instrument_heatmap(instruments, sim, stats['question_meta'])
                if fig2:
                    pdf.add_image_from_matplotlib(fig2, x=15, w=180)
                    pdf.ln(120)
        except Exception as e:
            # Continue without graphics if there's an error
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 8, sanitize("Graphics generation skipped due to technical issues."), ln=True)
            pdf.ln(5)
    
    # Instruments overview
    pdf.add_instruments_overview(instruments, stats)
    
    # Detailed matches
    displayed_matches = [m for m in raw_matches if abs(m[2]) >= threshold][:max_matches_displayed]
    
    pdf.chapter_title(f"Top Harmonised Question Pairs (Showing {len(displayed_matches)})")
    
    if not displayed_matches:
        pdf.set_font("Arial", "I", 11)
        pdf.cell(0, 10, sanitize(f"No question pairs found above {threshold:.0%} threshold."), ln=True)
        pdf.cell(0, 8, sanitize("Consider lowering the threshold to see potential matches."), ln=True)
    else:
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, sanitize(f"The following question pairs achieved match scores above {threshold:.0%}:"), ln=True)
        pdf.ln(5)
        
        # Enhanced match display
        for match_num, (i, j, score) in enumerate(displayed_matches, 1):
            if pdf.get_y() > 250:
                pdf.add_page()
            
            inst1, q1_no = stats['question_meta'].get(i, ("Unknown", "?"))
            inst2, q2_no = stats['question_meta'].get(j, ("Unknown", "?"))
            
            if i < len(questions) and j < len(questions):
                q1 = questions[i]
                q2 = questions[j]
                
                # Match header with score
                pdf.set_font("Arial", "B", 11)
                if score >= 0.8:
                    pdf.set_text_color(0, 128, 0)  # Green for high scores
                elif score >= 0.6:
                    pdf.set_text_color(255, 140, 0)  # Orange for medium scores
                else:
                    pdf.set_text_color(200, 50, 50)  # Red for lower scores
                    
                pdf.cell(0, 8, sanitize(f"Match #{match_num} - Score: {score:.0%}"), ln=True)
                pdf.set_text_color(0, 0, 0)
                
                # Question details
                pdf.set_font("Arial", "", 10)
                pdf.cell(40, 6, sanitize("Question 1:"), border=0)
                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 6, sanitize(f"{inst1} #{q1_no}"), ln=True)
                pdf.set_font("Arial", "", 9)
                pdf.multi_cell(0, 5, sanitize(q1.question_text or "No text available"))
                
                pdf.set_font("Arial", "", 10)
                pdf.cell(40, 6, sanitize("Question 2:"), border=0)
                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 6, sanitize(f"{inst2} #{q2_no}"), ln=True)
                pdf.set_font("Arial", "", 9)
                pdf.multi_cell(0, 5, sanitize(q2.question_text or "No text available"))
                
                pdf.ln(3)
    
    # Footer information
    pdf.add_page()
    pdf.chapter_title("Report Notes")
    pdf.set_font("Arial", "", 10)
    
    notes = [
        f"• This report analyzed {stats['total_questions']} questions across {len(instruments)} instruments",
        f"• Match threshold was set to {threshold:.0%} - only pairs scoring above this are considered 'harmonised'",
        f"• {stats['harmonised_questions']} questions ({stats['success_rate']:.1f}%) successfully found harmonisation matches",
        f"• Average match score among successful pairs: {stats['avg_match_score']:.1f}%",
        "• Match scores represent semantic similarity between question pairs",
        "• This report provides a human-readable alternative to the Excel similarity matrix"
    ]
    
    if not GRAPHICS_AVAILABLE:
        notes.append("• Graphics require matplotlib and seaborn packages for full functionality")
    
    for note in notes:
        pdf.cell(0, 8, sanitize(note), ln=True)
    
    # Save the PDF
    try:
        out_path = os.path.abspath(filename)
        pdf.output(out_path)
        return out_path
    except Exception as e:
        raise IOError(f"Failed to save harmonisation report: {str(e)}")


# Convenience function for basic reports
def generate_basic_harmony_report(
    match_response: MatchResponse,
    instruments: List[Instrument],
    filename: str = "harmony_report.pdf",
    threshold: float = 0.5
) -> str:
    """Generate a basic harmonisation report without graphics (faster generation)."""
    return generate_harmony_pdf_report(
        match_response=match_response,
        instruments=instruments,
        filename=filename,
        threshold=threshold,
        include_graphics=False,
        max_matches_displayed=30
    )