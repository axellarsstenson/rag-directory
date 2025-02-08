# RAG Directory

A command-line tool for Retrieval-Augmented Generation (RAG) using local files and Ollama models.

## Installation

```bash
pip install rag-directory
```

## Requirements

- Python 3.10+
- Ollama running locally (default: http://localhost:11434)

## Usage

```bash
# Using the command-line tool
rag-directory llama2:latest [directory]

# Or using Python
from rag_directory.cli import RAGTool
rag = RAGTool("llama2:latest")
rag.load_directory("path/to/directory")
rag.chat_loop()
```

## Features

- Process multiple file types (PDF, Markdown, text files)
- Semantic search using sentence transformers
- Interactive chat interface
- Source attribution for answers
- Integrates with Ollama models

## Example

```bash
$ rag-directory llama2:latest ./docs
Loading files from ./docs...
Processed: ./docs/architecture.pdf
Processed: ./docs/api.md
Starting chat session. Type 'exit' to quit.

What would you like to know: What is the system architecture?
```

## License

MIT License. See LICENSE file for details.