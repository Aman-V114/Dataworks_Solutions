import os
from dotenv import load_dotenv

load_dotenv()

class Config_API:
    
    def __init__(self):
        
        self.AIPROXY_TOKEN=os.environ.get("PROXY_API_KEY")
        self.ChatEndpoint="http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
        self.EmbeddingEndpoint="http://aiproxy.sanand.workers.dev/openai/v1/embeddings"
        
        pass


