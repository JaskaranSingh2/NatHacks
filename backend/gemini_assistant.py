# gemini_assistant.py
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel
from google.api_core.exceptions import GoogleAPICallError, DefaultCredentialsError
import logging
from collections import OrderedDict

# pip3 install google-cloud-aiplatform

# TODO: verify caching is ok
# TODO: unit tests, hardware integration tests

LOGGER = logging.getLogger("gemini_assistant")

class GeminiAssistant:
    """
    Wrapper for Gemini api (vertex ai)
    """

    def __init__(self, project_id: str, location: str = "us-central1", model_name: str = "gemini-2.5", max_retries=3):
        self.enabled = False
        self.max_retries = max_retries
        self.cache = OrderedDict()
        self.max_cache_size = 100        
        try:
            aiplatform.init(project=project_id, location=location)
            self.model = GenerativeModel(model_name)
            self.enabled = True
        except DefaultCredentialsError as e:
            LOGGER.warning(f"GeminiAssistant not initialized properly: {e}")
            self.model = None
            
            
    def _cache_response(self, key: str, value: str):
        if len(self.cache) >= self.max_cache_size:
            self.cache.popitem(last=False)
        self.cache[key] = value


    def generate_text(self, prompt: str, system_instruction: str = None) -> str:
        """
        generate a response from Gemini
        """
        if not self.enabled:
            LOGGER.warning("GeminiAssistant is disabled & can't generate text")
            return ""
        
        full_prompt = f"{system_instruction}\n\nUser: {prompt}" if system_instruction else prompt
        if full_prompt in self.cache:
            return self.cache[full_prompt]

        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(full_prompt)
                text = response.text.strip() if response and response.text else ""
                if text:
                    self._cache_response(full_prompt, text)
                    return text
                else:
                    LOGGER.warning(f"Empty response on attempt {attempt+1}")
            except GoogleAPICallError as e:
                LOGGER.warning(f"Gemini generation failed on attempt {attempt+1}: {e}")
            except Exception as e:
                LOGGER.warning(f"Gemini encountered an unexpected error: {e}")

        LOGGER.error(f"GeminiAssistant failed to generate response after {retries} attempts.")
        return ""
