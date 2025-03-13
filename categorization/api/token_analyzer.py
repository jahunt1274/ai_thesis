"""
Token counter for the categorization service.

This module provides functionality to count tokens, estimate response sizes,
and calculate API costs.
"""

import json
import tiktoken
from typing import Dict, List, Any, Union, Tuple
from constants import OpenAIModels, OPENAI_API_COSTS, OPENAI_API_RATE_LIMITS
from .prompt_handler import PromptHandler

class TokenCounter:
    """Handles token counting and cost estimation for the OpenAI API."""
    
    def __init__(self, model: str):
        """
        Initialize the token counter for a specific model.
        
        Args:
            model: The model name (e.g., "gpt-4o")
        """
        self.model = self._get_model_type(model)
        self.encoder = self._get_encoder(model)
    
    def _get_model_type(self, model: str) -> OpenAIModels:
        """Convert model string to ModelType enum."""
        for model_type in OpenAIModels:
            if model_type.value == model:
                return model_type
        # Default to GPT-3.5 Turbo if model not recognized
        return OpenAIModels.GPT35Turbo
    
    def _get_encoder(self, model: str):
        """Get the appropriate encoder for the model."""
        try:
            if "gpt-4" in model:
                return tiktoken.encoding_for_model("gpt-4")
            elif "gpt-3.5" in model:
                return tiktoken.encoding_for_model("gpt-3.5-turbo")
            else:
                # Fall back to cl100k_base for unknown models
                return tiktoken.get_encoding("cl100k_base")
        except KeyError:
            # Fall back to cl100k_base for unknown models
            return tiktoken.get_encoding("cl100k_base")
        
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a string.
        
        Args:
            text: The input text
            
        Returns:
            Number of tokens
        """
        tokens = self.encoder.encode(text)
        return len(tokens)

    def count_message_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Count tokens in a list of messages for chat completions.
        
        Args:
            messages: List of message dictionaries with role and content
            
        Returns:
            Number of tokens
        """
        num_tokens = 0
        for message in messages:
            # Every message has a base token count of 3 for the formatting
            num_tokens += 3
            
            # Count tokens in the content
            for key, value in message.items():
                num_tokens += self.count_tokens(value)
                
                # Each key (like "role" or "content") adds 1 token
                num_tokens += 1
        
        # Add 3 tokens for the assistant's formatting
        num_tokens += 3
        
        return num_tokens
    
    def estimate_idea_response_tokens(self, num_ideas: int) -> int:
        """
        Estimate the number of tokens in the response based on idea count.
        
        Args:
            num_ideas: Number of ideas in the batch
            
        Returns:
            Estimated number of output tokens
        """
        # Average tokens per idea in response (ID + category) is roughly 25
        # Include some overhead for JSON formatting, etc.
        per_idea_tokens = 25
        base_tokens = 20  # Base overhead for response
        
        return base_tokens + (num_ideas * per_idea_tokens)

    def calculate_batch_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate the cost for a batch.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost in USD
        """
        model_cost_data = OPENAI_API_COSTS[self.model]
        input_cost = (input_tokens / model_cost_data["delim"]) * model_cost_data[self.model]["input"]
        output_cost = (output_tokens / model_cost_data["delim"]) * model_cost_data["output"]
        
        return input_cost + output_cost
    
    def get_rate_limits(self) -> Dict[str, int]:
        """
        Get the rate limits for the model.
        
        Returns:
            Dictionary with tpm (tokens per minute) and rpm (requests per minute)
        """
        return OPENAI_API_RATE_LIMITS[self.model]
    
    def estimate_categorization_prompt_tokens(self, prompt: str) -> int:
        """
        Estimate the number of tokens for a categorization prompt.
        
        Args:
            prompt: String of the prompt being sent ot the API client
            
        Returns:
            Estimated token count
        """
        # Count tokens in the prompt
        return self.count_tokens(prompt)
    
    def optimize_batch_size(self, ideas: List[Dict[str, Any]], categories: List[str], 
                           max_input_tokens: int = 125000) -> List[List[Dict[str, Any]]]:
        """
        Optimize and split batches based on token count to avoid exceeding limits.
        
        Args:
            ideas: List of all ideas to process
            categories: List of available categories
            max_input_tokens: Maximum tokens per request
            
        Returns:
            List of batches, where each batch is a list of ideas
        """
        batches = []
        current_batch = []
        current_token_count = 0
        
        # Create fixed part of prompt
        prompt_handler = PromptHandler()
        prompt = prompt_handler.create_idea_categorization_prompt(categories=categories)
        
        # Token count for the fixed part of the prompt (categories and instructions)
        fixed_prompt_tokens = self.count_tokens(prompt)
        
        # Allocate tokens for the fixed part of the prompt
        current_token_count = fixed_prompt_tokens
        
        for idea in ideas:
            # Convert idea to JSON to count tokens as it will appear in the prompt
            idea_json = json.dumps(idea, indent=2)
            idea_tokens = self.count_tokens(idea_json)
            
            # If adding this idea would exceed the limit, create a new batch
            if current_token_count + idea_tokens > max_input_tokens and current_batch:
                batches.append(current_batch)
                current_batch = []
                current_token_count = fixed_prompt_tokens
            
            # Add idea to the current batch
            current_batch.append(idea)
            current_token_count += idea_tokens
        
        # Add the last batch if not empty
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def calculate_rate_limit_delay(self, batch_sizes: List[int]) -> float:
        """
        Calculate the delay needed between requests to stay within rate limits.
        
        Args:
            batch_sizes: List of token counts for each batch
            
        Returns:
            Recommended delay in seconds between requests
        """
        rate_limits = self.get_rate_limits()
        tpm = rate_limits["tpm"]  # tokens per minute
        rpm = rate_limits["rpm"]  # requests per minute
        
        # Calculate average tokens per batch
        avg_tokens = sum(batch_sizes) / len(batch_sizes) if batch_sizes else 0
        
        # Calculate minimum delay based on both token and request limits
        token_based_delay = (avg_tokens / tpm) * 60  # in seconds
        request_based_delay = 60 / rpm  # in seconds
        
        # Take the larger of the two delays to ensure we don't exceed either limit
        return max(token_based_delay, request_based_delay)
