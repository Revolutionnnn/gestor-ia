from fastapi import HTTPException, status
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, GOOGLE_API_KEY, TIMEOUT_LLM, logger


class LLMService:
    def __init__(self):
        self.use_gemini = bool(GOOGLE_API_KEY and not OPENAI_API_KEY)
        self.client = self._initialize_client()
        self.model = OPENAI_MODEL
        
    def _initialize_client(self):
        if self.use_gemini:
            import google.generativeai as genai
            genai.configure(api_key=GOOGLE_API_KEY)
            client = genai.GenerativeModel('gemini-flash-latest')
            logger.info("llm_configured", provider="gemini")
            return client
        elif OPENAI_API_KEY:
            logger.info("llm_configured", provider="openai")
            return OpenAI(api_key=OPENAI_API_KEY, timeout=TIMEOUT_LLM)
        
        logger.warning("llm_not_configured")
        return None
    
    def generate(self, prompt: str, system_message: str = None) -> tuple[str, int]:
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM API key not configured"
            )
        
        try:
            if self.use_gemini:
                return self._generate_gemini(prompt)
            return self._generate_openai(prompt, system_message)
        except Exception as e:
            logger.error("llm_error", error=str(e), provider="gemini" if self.use_gemini else "openai")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en LLM API: {str(e)}"
            )
    
    def _generate_gemini(self, prompt: str) -> tuple[str, int]:
        response = self.client.generate_content(prompt)
        content = response.text
        tokens = len(content.split()) * 2
        return content, tokens
    
    def _generate_openai(self, prompt: str, system_message: str) -> tuple[str, int]:
        messages = [{"role": "user", "content": prompt}]
        if system_message:
            messages.insert(0, {"role": "system", "content": system_message})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        content = response.choices[0].message.content
        tokens = response.usage.total_tokens
        return content, tokens
    
    def is_configured(self) -> bool:
        return self.client is not None


llm_service = LLMService()
