#!/usr/bin/env python3
import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
import requests
from rich.console import Console
from rich.prompt import Prompt
import PyPDF2
from markdown import markdown
import html2text
from sklearn.metrics.pairwise import cosine_similarity

class RAGTool:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.console = Console()
        self.documents = {}
        self.embeddings = {}
        
    def load_directory(self, directory: Path) -> None:
        """Load and process all files in the given directory."""
        self.console.print(f"Loading files from {directory}...", style="bold blue")
        
        for file_path in directory.glob('**/*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    # Handle different file types
                    content = self._parse_file(file_path)
                    
                    # Create chunks of text for better embedding
                    chunks = self._create_chunks(content, chunk_size=1000)
                    
                    # Store document chunks
                    self.documents[str(file_path)] = chunks
                    
                    # Create and store embeddings for each chunk
                    self.embeddings[str(file_path)] = [
                        self.embeddings_model.encode(chunk) for chunk in chunks
                    ]
                    
                    self.console.print(f"Processed: {file_path}", style="green")
                except Exception as e:
                    self.console.print(f"Error processing {file_path}: {e}", style="red")

    def _parse_file(self, file_path: Path) -> str:
        """Parse different file types and return their content."""
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == '.pdf':
                # Handle PDF files
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    return ' '.join(page.extract_text() for page in pdf_reader.pages)
                    
            elif suffix == '.md':
                # Handle Markdown files
                with open(file_path, 'r', encoding='utf-8') as file:
                    md_content = file.read()
                    html_content = markdown(md_content)
                    h = html2text.HTML2Text()
                    return h.handle(html_content)
                    
            elif suffix in ['.txt', '.py', '.js', '.html', '.css', '.json']:
                # Handle text-based files
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
                    
            else:
                self.console.print(f"Unsupported file type: {suffix}", style="yellow")
                return ""
                
        except Exception as e:
            self.console.print(f"Error reading {file_path}: {str(e)}", style="red")
            return ""

    def _create_chunks(self, text: str, chunk_size: int) -> List[str]:
        """Split text into chunks of approximately equal size."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1  # +1 for space
            
            if current_size >= chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
                
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks

    def find_relevant_chunks(self, query: str, top_k: int = 3) -> List[Dict]:
        """Find the most relevant chunks for a given query."""
        query_embedding = self.embeddings_model.encode(query)
        
        all_similarities = []
        for file_path, file_embeddings in self.embeddings.items():
            for chunk_idx, chunk_embedding in enumerate(file_embeddings):
                similarity = cosine_similarity(
                    [query_embedding], 
                    [chunk_embedding]
                )[0][0]
                all_similarities.append({
                    'file_path': file_path,
                    'chunk_idx': chunk_idx,
                    'similarity': similarity
                })
        
        # Sort by similarity and get top_k
        all_similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return all_similarities[:top_k]

    def query_ollama(self, prompt: str, context: str) -> str:
        """Query the Ollama model with prompt and context."""
        url = "http://localhost:11434/api/generate"
        
        # Construct the prompt with context
        full_prompt = f"""Context information is below.
        ---------------------
        {context}
        ---------------------
        Given the context information, please answer the following question:
        {prompt}
        
        If the answer cannot be found in the context, please say so."""

        data = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False
        }

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            return f"Error querying Ollama: {str(e)}"

    def chat_loop(self) -> None:
        """Start an interactive chat loop with the user."""
        self.console.print("\nStarting chat session. Type 'exit' to quit.", style="bold blue")
        
        while True:
            query = Prompt.ask("\nWhat would you like to know")
            
            if query.lower() == 'exit':
                break
                
            # Find relevant chunks
            relevant_chunks = self.find_relevant_chunks(query)
            
            if not relevant_chunks:
                self.console.print("No relevant information found.", style="yellow")
                continue
                
            # Combine relevant chunks into context
            context = "\n\n".join([
                self.documents[chunk['file_path']][chunk['chunk_idx']]
                for chunk in relevant_chunks
            ])
            
            # Query Ollama
            response = self.query_ollama(query, context)
            
            # Print response
            self.console.print("\nResponse:", style="bold")
            self.console.print(response)
            
            # Optionally print sources
            sources = set(chunk['file_path'] for chunk in relevant_chunks)
            self.console.print("\nSources:", style="dim")
            for source in sources:
                self.console.print(f"- {source}")

def main():
    parser = argparse.ArgumentParser(description='RAG Directory Tool')
    parser.add_argument('model', help='Ollama model to use (e.g., llama2:latest)')
    parser.add_argument('directory', nargs='?', default='.', 
                        help='Directory to process (default: current directory)')
    
    args = parser.parse_args()
    
    # Initialize and run RAG tool
    rag_tool = RAGTool(args.model)
    rag_tool.load_directory(Path(args.directory))
    rag_tool.chat_loop()

if __name__ == '__main__':
    main()