from PyPDF2 import PdfReader, PdfWriter

file_name = r'C:\Users\bruce\Documents\Dave Babcocks IBM 1620 Model F ALD Scan.pdf'

reader = PdfReader(file_name)
page_range = range(0, 500)

for page_num, page in enumerate(reader.pages, 1):
    if page_num in page_range:
        page.rotate(90)
        writer = PdfWriter()
        writer.add_page(page)
        with open(f'pages/ald_{page_num:03d}.pdf', 'wb') as out:
            writer.write(out)
    