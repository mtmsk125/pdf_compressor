FROM python:3.10-slim

RUN apt-get update && apt-get install -y ghostscript && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pdf_compressor.py .

EXPOSE 8501

CMD streamlit run pdf_compressor.py --server.port=$PORT --server.address=0.0.0.0
