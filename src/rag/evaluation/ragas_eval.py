from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import structlog

from rag.config.settings import get_settings

logger = structlog.get_logger(__name__)


class RAGASEvaluator:
    def __init__(self) -> None:
        self._settings = get_settings().mlflow

    async def evaluate(
        self,
        questions: list[str],
        answers: list[str],
        contexts: list[list[str]],
        ground_truths: list[str] | None = None,
    ) -> dict[str, Any]:
        try:
            from ragas import evaluate
            from ragas.metrics import (
                answer_relevancy,
                context_precision,
                context_recall,
                faithfulness,
            )

            eval_data = {
                "question": questions,
                "answer": answers,
                "contexts": contexts,
            }

            if ground_truths:
                eval_data["ground_truth"] = ground_truths

            from datasets import Dataset
            dataset = Dataset.from_dict(eval_data)

            metrics = [faithfulness, answer_relevancy, context_precision]
            if ground_truths:
                metrics.append(context_recall)

            result = evaluate(dataset, metrics=metrics)

            scores = {metric.name: float(result[metric.name]) for metric in metrics}

            logger.info("ragas_evaluation_completed", scores=scores)
            return scores

        except ImportError:
            logger.warning("ragas_not_installed")
            return {"error": "ragas not installed. Install with: pip install ragas"}
        except Exception as e:
            logger.error("ragas_evaluation_failed", error=str(e))
            return {"error": str(e)}

    def save_results(self, results: dict[str, Any], path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            json.dump(results, f, indent=2)
        logger.info("evaluation_results_saved", path=str(path))
