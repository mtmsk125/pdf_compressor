from PyPDF2 import PdfMerger, PdfReader, PdfWriter

def merge_pdf(files, output):
    merger = PdfMerger()
    for f in files:
        merger.append(f)
    merger.write(output)
    merger.close()

def split_pdf(input_file, pages, output):
    reader = PdfReader(input_file)
    writer = PdfWriter()

    for part in pages.split(','):
        part = part.strip()
        if '-' in part:
            s, e = map(int, part.split('-'))
            for i in range(s-1, e):
                if i < len(reader.pages):
                    writer.add_page(reader.pages[i])
        else:
            i = int(part) - 1
            if i < len(reader.pages):
                writer.add_page(reader.pages[i])

    with open(output, 'wb') as f:
        writer.write(f)
