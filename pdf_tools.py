from PyPDF2 import PdfMerger, PdfReader, PdfWriter

def merge_pdf(files, output):
    merger = PdfMerger()
    for f in files: merger.append(f)
    merger.write(output)
    merger.close()

def split_pdf(input_file, pages, output):
    reader = PdfReader(input_file)
    writer = PdfWriter()
    for p in pages.split(','):
        if '-' in p:
            s,e = map(int, p.split('-'))
            for i in range(s-1, e): writer.add_page(reader.pages[i])
        else:
            writer.add_page(reader.pages[int(p)-1])
    with open(output, 'wb') as f: writer.write(f)
