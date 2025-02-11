import os

class Config:
    API_KEY=os.environ.get("PROXY_API_KEY")
    ChatEndpoint=os.environ.get("API_chat_endpoint")
    EmbeddingEndpoint=os.environ.get("API_embedding_endpoint")
    