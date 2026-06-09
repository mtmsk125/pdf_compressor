from flask import Flask, render_template
from pdf_tools import compress_pdf, merge_pdf, split_pdf, pdf_to_word, word_to_pdf
from image_tools import remove_background, image_to_webp

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pdf/compress', methods=['GET', 'POST'])
def compress():
    return compress_pdf()

@app.route('/pdf/merge', methods=['GET', 'POST'])
def merge():
    return merge_pdf()

@app.route('/pdf/split', methods=['GET', 'POST'])
def split():
    return split_pdf()

@app.route('/pdf/to-word', methods=['GET', 'POST'])
def pdf2word():
    return pdf_to_word()

@app.route('/word/to-pdf', methods=['GET', 'POST'])
def word2pdf():
    return word_to_pdf()

@app.route('/image/remove-bg', methods=['GET', 'POST'])
def remove_bg():
    return remove_background()

@app.route('/image/to-webp', methods=['GET', 'POST'])
def to_webp():
    return image_to_webp()

if __name__ == '__main__':
    app.run(debug=True)
