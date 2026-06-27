from __future__ import annotations


class VertexTextEmbeddingModel:
    def __init__(self, project_id: str, location: str, model_name: str = "text-embedding-005"):
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self._client = None

    def embed(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str], task_type: str | None = None) -> list[list[float]]:
        client = self._get_client()
        config = _build_embed_config(task_type)
        response = client.models.embed_content(
            model=self.model_name,
            contents=texts,
            config=config,
        )
        return [_embedding_values(embedding) for embedding in response.embeddings]

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from google import genai
            from google.genai.types import HttpOptions
        except Exception as exc:
            raise RuntimeError(
                "Google Gen AI embedding dependencies are missing. Install requirements-embeddings.txt."
            ) from exc

        self._client = genai.Client(
            vertexai=True,
            project=self.project_id,
            location=self.location,
            http_options=HttpOptions(api_version="v1"),
        )
        return self._client


def _build_embed_config(task_type: str | None):
    if not task_type:
        return None
    try:
        from google.genai.types import EmbedContentConfig
    except Exception:
        return {"task_type": task_type}
    return EmbedContentConfig(task_type=task_type)


def _embedding_values(embedding) -> list[float]:
    values = getattr(embedding, "values", None)
    if values is None and isinstance(embedding, dict):
        values = embedding.get("values")
    if values is None:
        raise RuntimeError("Embedding response did not include vector values.")
    return [float(value) for value in values]
