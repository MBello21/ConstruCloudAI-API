import requests
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class EmbeddingService:

    def __init__(self):
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN", None)
        self.model_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
        self.headers = {}
        if self.hf_token:
            self.headers["Authorization"] = f"Bearer {self.hf_token}"

    def generar_embedding(self, texto: str) -> List[float]:

        try:
            response = requests.post(
                self.model_url,
                headers=self.headers,
                json={"inputs": texto},
                timeout=10
            )

            if response.status_code == 200:
                embeddings = response.json()

                if isinstance(embeddings[0], list):
                    return embeddings[0]
                else:
                    return embeddings

            elif response.status_code == 503:

                print("⏳ Modelo Hugging Face cargando... retry en 5s")
                import time
                time.sleep(5)
                return self.generar_embedding(texto)

            else:
                raise Exception(
                    f"Error HF API ({response.status_code}): {response.text}")
        except requests.Timeout:
            raise Exception("Timeout conectando a Hugging Face")
        except Exception as e:
            raise Exception(f"Error generando embedding: {str(e)}")

    def generar_embeddings_batch(self, textos: List[str]) -> List[List[float]]:

        embeddings = []

        for texto in textos:
            try:
                emb = self.generar_embedding(texto)
                embeddings.append(emb)
            except Exception as e:
                print(f"⚠️ Error con texto '{texto[:50]}...': {e}")
                embeddings.append([0.0]*384)

        return embeddings
