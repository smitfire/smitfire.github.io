from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
import io
import csv
from datetime import datetime

# Paths to the input and output PDF
input_pdf_path = "chomage-jobsheet.pdf"
output_pdf_path = "filled-janvier.pdf"
csv_file_path = "saved_jobs.csv"
positive_string = "X"

# Initial coordinates for the "Date de l’offre de services" boxes
# These coordinates are based on the pdfplumber output
initial_date_positions = [
    (233, 50),
    (233, 63),
    (233, 76),
    (233, 89),
]

checkbox_positions = [
    (233, 470),
    (233, 517),
    (233, 592),
]

company_name_positions = [
    (233, 110),
]

job_title_positions = [
    (239, 300),
]

url_positions = [
    (239, 280),
]

# Read the CSV file and extract the necessary information
jobs = []
with open(csv_file_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        date_applied_str = row['Date Applied']
        if date_applied_str == 'N/A':
            day_month = '0701'
        else:
            date_applied = datetime.strptime(date_applied_str, '%d/%m/%Y')
            if date_applied.month == 1 and date_applied.year == 2025:  # Only use entries from January 2025
                day_month = date_applied.strftime('%d%m')
            else:
                continue  # Skip entries not from January 2025
        jobs.append({
            'company': row['Company'],
            'job_title': row['Job Title'],
            'date_string': day_month,
            'job_url': row['Job URL']
        })

print(len(jobs))
# Create a new PDF with the filled data
packet = io.BytesIO()
can = canvas.Canvas(packet, pagesize=letter)

# Set font size for company name and job title
font_size = 8
can.setFont("Helvetica", font_size)

# Loop to fill in the subsequent rows for date_string, company_name, job_title, and job_url
for index, job in enumerate(jobs):
    if index > 0 and index % 8 == 0:
        can.showPage()  # Start a new page after every 8 rows
        can.setFont("Helvetica", font_size)  # Reset font size for the new page

    # Write "TEST" in the middle of the second page
    if index > 8:
        can.setFont("Helvetica", 50)
        can.drawString(50, 100, "TEST")

    repetition = index % 8  # Determine the position on the current page

    date_string = job['date_string']
    company_name = job['company']
    job_title = job['job_title']
    job_url = job['job_url']

    # Fill in the date_string
    for i, char in enumerate(date_string):
        y, x = initial_date_positions[i]
        y += repetition * 34
        can.saveState()
        can.translate(y, x)
        can.rotate(90)
        can.drawString(0, 0, char)
        can.restoreState()

    # Fill in the positive_string
    for y, x in checkbox_positions:
        y += repetition * 34
        can.saveState()
        can.translate(y, x)
        can.rotate(90)
        can.drawString(0, 0, positive_string)
        can.restoreState()

    # Fill in the company_name
    for y, x in company_name_positions:
        y += repetition * 34
        can.saveState()
        can.translate(y, x)
        can.rotate(90)
        can.drawString(0, 0, company_name)
        can.restoreState()

    # Define a paragraph style with the same font size for the job title
    styles = getSampleStyleSheet()
    style = ParagraphStyle(
        name='Normal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=font_size,
    )

    # Fill in the job_title with text wrapping
    width_limit = 100  # Set the width limit for the job title
    for y, x in job_title_positions:
        y += repetition * 34
        can.saveState()
        can.translate(y, x)
        can.rotate(90)
        p = Paragraph(job_title, style)
        p.wrapOn(can, width_limit, 100)  # Set the width limit and height
        p.drawOn(can, 0, 0)
        can.restoreState()

    # Fill in the job_url with smaller text
    small_font_size = 6
    can.setFont("Helvetica", small_font_size)
    for y, x in job_title_positions:  # Use job_title_positions to align with job title
        y += (repetition * 34) + 5
        can.saveState()
        can.translate(y, x)
        can.rotate(90)
        can.drawString(0, 0, job_url)
        can.restoreState()

    # Reset font size for the next iteration
    can.setFont("Helvetica", font_size)

can.save()

# Move to the beginning of the StringIO buffer
packet.seek(0)

# Read the existing PDF
existing_pdf = PdfReader(input_pdf_path)
print(f"Number of pages in the existing PDF: {len(existing_pdf.pages)}")  # Print the number of pages in the existing PDF
output = PdfWriter()

# Add the "watermark" (which is the new PDF) on the existing page
new_pdf = PdfReader(packet)
page = existing_pdf.pages[0]
page.merge_page(new_pdf.pages[0])
output.add_page(page)

# Add remaining pages if any
for i in range(1, len(existing_pdf.pages)):
    output.add_page(existing_pdf.pages[i])

# Finally, write the output to a new PDF file
with open(output_pdf_path, "wb") as outputStream:
    output.write(outputStream)

print(f"Filled PDF saved as {output_pdf_path}")