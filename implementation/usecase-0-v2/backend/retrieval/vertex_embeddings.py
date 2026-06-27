from __future__ import annotations


class VertexTextEmbeddingModel:
    def __init__(self, project_id: str, location: str, model_name: str = "text-embedding-005"):
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self._model = None

    def embed(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str], task_type: str | None = None) -> list[list[float]]:
        model = self._get_model()
        inputs = _build_inputs(texts, task_type)
        embeddings = model.get_embeddings(inputs)
        return [[float(value) for value in embedding.values] for embedding in embeddings]

    def _get_model(self):
        if self._model is not None:
            return self._model
        try:
            import vertexai
            from vertexai.language_models import TextEmbeddingModel
        except Exception as exc:
            raise RuntimeError(
                "Vertex AI embedding dependencies are missing. Install requirements-embeddings.txt."
            ) from exc

        vertexai.init(project=self.project_id, location=self.location)
        self._model = TextEmbeddingModel.from_pretrained(self.model_name)
        return self._model


def _build_inputs(texts: list[str], task_type: str | None):
    if not task_type:
        return texts
    try:
        from vertexai.language_models import TextEmbeddingInput
    except Exception:
        return texts
    return [TextEmbeddingInput(text, task_type) for text in texts]
