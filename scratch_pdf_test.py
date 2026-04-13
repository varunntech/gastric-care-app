import re
from pypdf import PdfReader

reader = PdfReader("Gastric Cancer Chatbot Handbook.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

raw_chunks = re.split(r'(?<=[.!?])\s+', text)
pdf_content = [chunk.strip() for chunk in raw_chunks if len(chunk.strip()) > 20]

print("Total extracted raw text length:", len(text))
print("Number of chunks:", len(pdf_content))
for i, chunk in enumerate(pdf_content[:5]):
    print(f"--- Chunk {i} ---")
    print(chunk)
