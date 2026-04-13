import re
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

reader = PdfReader("Gastric Cancer Chatbot Handbook.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

raw_chunks = re.split(r'(?<=[.!?])\s+', text)
pdf_content = [chunk.strip() for chunk in raw_chunks if len(chunk.strip()) > 20]

vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(pdf_content)

queries = [
    "What is Gastric Cancer?",
    "COMPLETE Gastric Cancer Knowledge What is Gastric Cancer?"
]

for q in queries:
    query_vec = vectorizer.transform([q])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    best_idx = similarities.argmax()
    best_score = similarities[best_idx]
    print(f"Query: '{q}' -> Best Score: {best_score}")
    print(f"Matched Chunk: {pdf_content[best_idx]}\n")
