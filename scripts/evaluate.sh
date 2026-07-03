#!/usr/bin/env bash
set -euo pipefail

echo "=== Running RAG Evaluation ==="

uv run python -c "
import asyncio
import json
from rag.evaluation.ragas_eval import RAGASEvaluator

evaluator = RAGASEvaluator()

questions = [
    'What is the main topic of the document?',
    'Summarize the key points discussed.',
    'What are the conclusions drawn?',
]

# These would normally come from actual RAG queries
answers = [
    'The document discusses production ML systems.',
    'Key points include scalability and monitoring.',
    'The conclusion emphasizes reliability.',
]

contexts = [
    ['Production ML systems require careful engineering.'],
    ['Scalability and monitoring are critical components.'],
    ['Reliability is the foundation of production systems.'],
]

results = asyncio.run(evaluator.evaluate(questions, answers, contexts))
print(json.dumps(results, indent=2))
evaluator.save_results(results, 'logs/evaluation_results.json')
"
