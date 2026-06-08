import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPICallError, GoogleAPIError

logger = logging.getLogger("backend.services.gemini")

class GeminiService:
    """
    Service layer to interact with the Google Gemini API.
    """
    def __init__(self) -> None:
        self.api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
        self.model_name: str = os.getenv("GEMINI_MODEL_NAME", "gemini-3.5-flash")
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY environment variable is not set.")
        else:
            # Configure the SDK with the provided API key
            genai.configure(api_key=self.api_key)
            logger.info("Google Generative AI SDK configured successfully.")

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Converts the generic message history format to the format required by Google's Gemini SDK.
        Gemini requires 'user' or 'model' roles, and content inside a list of parts.
        """
        formatted_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            # Map standard assistant/bot roles to 'model'
            if role in ["assistant", "bot", "system"]:
                role = "model"
            elif role != "user":
                role = "user"
            
            content = msg.get("content", "")
            if not content:
                continue
                
            formatted_messages.append({
                "role": role,
                "parts": [content]
            })
        return formatted_messages

    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generates a chat response from the Gemini model given a conversation history.
        Runs the blocking API call in an external thread pool to prevent blocking the async loop.
        """
        if not self.api_key:
            logger.error("Attempted Gemini API call without GEMINI_API_KEY set.")
            raise ValueError("GEMINI_API_KEY is not configured on the backend server.")

        if not messages:
            raise ValueError("Conversation history/message list cannot be empty.")

        # Format messages for Gemini API
        formatted_contents = self._convert_messages(messages)
        if not formatted_contents:
            raise ValueError("No valid message content was provided.")

        # Extract the last message (current query) if we are not passing history
        # Or construct a full chat sequence.
        # Note: In standard chat sessions, Gemini takes the entire sequence of conversation.
        # We can configure the model and run generate_content on the entire contents list.
        
        # Define the task to run in the thread pool
        def call_gemini_api() -> str:
            try:
                # Initialize model with system instruction if provided
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=system_instruction
                )
                
                # Call the API
                logger.info(f"Sending request to Gemini Model: {self.model_name} with {len(formatted_contents)} messages")
                response = model.generate_content(formatted_contents)
                
                if not response or not response.text:
                    logger.error("Gemini API returned an empty or invalid response.")
                    raise GoogleAPICallError("Empty response returned from Gemini.")
                    
                return response.text
            except GoogleAPICallError as e:
                logger.error(f"Google API call failed: {str(e)}")
                # Provide user-friendly messages for common API errors
                if "API_KEY_INVALID" in str(e) or e.code == 400:
                    raise ValueError("The provided Gemini API Key is invalid or inactive.") from e
                raise e
            except Exception as e:
                logger.error(f"Unexpected error in Gemini API call: {str(e)}")
                raise e

        # Execute blocking call in a separate thread to keep FastAPI server responsive
        try:
            return await asyncio.to_thread(call_gemini_api)
        except Exception as e:
            # Re-raise clean exceptions
            if isinstance(e, (ValueError, GoogleAPIError, GoogleAPICallError)):
                raise e
            raise RuntimeError(f"Failed to generate response due to internal API error: {str(e)}") from e

