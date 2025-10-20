# Local AI Document Analysis Agent

A privacy-focused Retrieval-Augmented Generation (RAG) system that enables natural language querying over document collections using local AI models. Built with LangChain, ChromaDB, and Ollama for complete offline functionality.

## Features

- **Semantic Search**: Query documents using natural language instead of exact keywords
- **Local Processing**: All AI operations run locally - no API keys or internet required
- **Vector Embeddings**: Uses Ollama's mxbai-embed-large model for high-quality text embeddings
- **Persistent Storage**: ChromaDB stores embeddings and metadata for fast retrieval
- **RAG Pipeline**: Combines document retrieval with Llama3.2 for contextual answers

## Architecture

```
User Question → Vector Search → Document Retrieval → LLM Response
     ↓              ↓                ↓                 ↓
  main.py    →  ChromaDB     →   Top 5 Docs    →   Llama3.2
```

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed locally
- Required Ollama models:
  ```bash
  ollama pull llama3.2
  ollama pull mxbai-embed-large
  ```

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd Local-AI-agent
   ```

2. Install dependencies:

   ```bash
   pip install langchain-ollama langchain-chroma langchain-core pandas
   ```

3. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

## Usage

### 1. Prepare Your Data

Place your CSV file with document data in the project directory. The system expects columns like:

- `Title`: Document title
- `Review`/`Content`: Main text content
- `Rating`: Numerical rating (optional)
- `Date`: Document date (optional)

### 2. Initialize Vector Database

Run the vector processing script to create embeddings:

```python
# vector.py
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import pandas as pd

# Load your data
df = pd.read_csv("your_data.csv")

# Initialize embeddings model
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# Create documents
documents = []
for i, row in df.iterrows():
    document = Document(
        page_content=row["Title"] + " " + row["Content"],
        metadata={"rating": row["Rating"], "date": row["Date"]},
        id=str(i)
    )
    documents.append(document)

# Create vector store
vector_store = Chroma(
    collection_name="document_collection",
    persist_directory="./chroma_langchain_db",
    embedding_function=embeddings
)

# Add documents to vector store
vector_store.add_documents(documents=documents)
```

### 3. Query Your Documents

```python
# main.py
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

# Initialize local LLM
model = OllamaLLM(model="llama3.2")

# Create prompt template
template = """
You are an expert assistant analyzing documents.
Here are relevant documents: {reviews}
Here is the question to answer: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Interactive querying
while True:
    question = input("Ask your question (q to quit): ")
    if question == "q":
        break

    # Retrieve relevant documents
    reviews = retriever.invoke(question)

    # Generate response
    result = chain.invoke({"reviews": reviews, "question": question})
    print(result)
```

## Project Structure

```
Local-AI-agent/
├── vector.py              # Vector database setup and document processing
├── main.py               # Interactive query interface
├── your_data.csv         # Your document dataset
├── chroma_langchain_db/  # ChromaDB storage (auto-created)
└── README.md            # This file
```

## How It Works

### 1. Document Processing

- Loads documents from CSV
- Combines title and content for embedding
- Stores metadata (ratings, dates) separately

### 2. Vector Embeddings

```python
embeddings = OllamaEmbeddings(model="mxbai-embed-large")
```

Converts text into high-dimensional vectors that capture semantic meaning.

### 3. Similarity Search

```python
retriever = vector_store.as_retriever(search_kwargs={"k": 5})
```

Finds the 5 most semantically similar documents to your query.

### 4. Response Generation

```python
chain = prompt | model
result = chain.invoke({"reviews": reviews, "question": question})
```

Feeds retrieved documents to Llama3.2 for contextual answers.

## Example Queries

- "What are the main complaints about service?"
- "Find positive feedback about food quality"
- "Which documents mention pricing issues?"
- "Summarize the customer satisfaction trends"

## Advantages

- **Privacy**: All data stays on your machine
- **Cost**: No API fees after initial setup
- **Customization**: Full control over models and parameters
- **Offline**: Works without internet connection
- **Flexibility**: Easy to adapt for different document types

## Performance Tips

- **Hardware**: More RAM and CPU cores improve response times
- **Model Size**: Larger embedding models provide better accuracy
- **Chunk Size**: For large documents, consider splitting into smaller chunks
- **Batch Processing**: Process multiple documents at once for efficiency

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Restart Ollama if needed
ollama serve
```

### Memory Issues

- Reduce the number of retrieved documents (`k` parameter)
- Use smaller embedding models
- Process documents in smaller batches

### Slow Performance

- Ensure Ollama models are fully loaded
- Check available system resources
- Consider using GPU acceleration if available

## Customization

### Different Document Types

Modify the document creation in `vector.py`:

```python
document = Document(
    page_content=f"{row['title']}: {row['content']}",
    metadata={"category": row["category"], "author": row["author"]},
    id=str(i)
)
```

### Custom Prompts

Update the template in `main.py`:

```python
template = """
You are a specialized assistant for [your domain].
Context: {reviews}
Question: {question}
Provide a detailed analysis based on the context.
"""
```

## License

This project is open source and available under the MIT License.
