import re
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

reader = PdfReader("Gastric Cancer Chatbot Handbook.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 10]
chunk_size = 5
overlap = 2
chunks = []
for i in range(0, len(lines), chunk_size - overlap):
    chunk_text = " ".join(lines[i:i + chunk_size])
    if len(chunk_text) > 30 and not chunk_text.lower().startswith("all greeting variations"):
        chunks.append(chunk_text)

# Remove exact duplicates while preserving order
pdf_content = list(dict.fromkeys(chunks))

print("Total chunks extracted:", len(pdf_content))
for i, chunk in enumerate(pdf_content):
    print(f"--- Chunk {i} ---")
    print(chunk.encode('ascii', 'ignore').decode('ascii'))
