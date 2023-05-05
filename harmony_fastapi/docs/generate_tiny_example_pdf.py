import pdfkit
doc_html = "1. Feeling nervous, anxious, or on edge<br/>2. Not being able to stop or control worrying"
pdf_bytes = pdfkit.from_string(doc_html)
print (len(pdf_bytes))
with open("example_tiny_pdf_file.pdf", "wb") as binary_file:
    # Write bytes to file
    binary_file.write(pdf_bytes)