import re
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

reader = PdfReader("Gastric Cancer Chatbot Handbook.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n\n"

# By paragraphs
raw_chunks = re.split(r'\n(?=[A-Z0-9])', text) 
# Actually, let's chunk by overlapping windows or split by custom heading regex if possible.
# Wait, just splitting by \n\n or \n is safer?
raw_chunks = [c for c in text.split('\n') if len(c.strip()) > 5]

print("Number of lines:", len(raw_chunks))
# Let's combine lines into chunks of 3 lines each to provide more context per match
chunks = []
current_chunk = ""
for line in raw_chunks:
    if line.strip().endswith('.') or line.strip().endswith('?'):
        current_chunk += " " + line.strip()
        chunks.append(current_chunk.strip())
        current_chunk = ""
    else:
        current_chunk += " " + line.strip()
if current_chunk:
    chunks.append(current_chunk.strip())
    
print("Number of chunks:", len(chunks))

vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(chunks)

queries = [
    "What is Gastric Cancer?",
    "yes",
]

for q in queries:
    query_vec = vectorizer.transform([q])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    best_idx = similarities.argmax()
    best_score = similarities[best_idx]
    print(f"Query: '{q}' -> Best Score: {best_score}")
    print(f"Matched Chunk: {chunks[best_idx]}\n")
