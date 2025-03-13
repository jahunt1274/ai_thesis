import time
import json
from collections import defaultdict
from typing import List, Dict, Any, Optional
from api.prompt_handler import PromptHandler

class BatchManager:
    """Manages the creation and tracking of idea batches for processing."""
    
    def __init__(self, logger=None, token_counter=None):
        self.logger = logger
        self.token_counter = token_counter
        self.batch_data = {
            "batches": {},
            "total_token_count": 0,
            "total_text_count": 0,
            "input_token_count": 0,
            "output_token_count": 0,
            "estimated_cost": 0.0
        }
    
    def create_batches_by_token_limit(self, ideas, categories, max_tokens=125000):
        """
        Create batches such that each batch doesn't exceed the token limit.
        
        Args:
            ideas: List of idea dictionaries
            categories: List of available categories
            max_tokens: Maximum tokens per request (default is lower than most model limits)
            
        Returns:
            List of batches, where each batch is a list of ideas
        """
        # Ensure we have a token counter
        if not self.token_counter:
            if self.logger:
                self.logger.warning("No token counter provided, falling back to text-based batching")
            return self.create_batches_by_text_limit(ideas, 4000)  # Default to ~4000 chars
            
        batches = self.token_counter.optimize_batch_size(ideas, categories, max_tokens)
        
        if self.logger:
            self.logger.info(f"Created {len(batches)} batches based on token limits")
            
            # Log token counts for each batch
            for i, batch in enumerate(batches):
                prompt = PromptHandler().create_idea_categorization_prompt(categories, batch)
                prompt_tokens = self.token_counter.estimate_categorization_prompt_tokens(prompt)
                completion_tokens = self.token_counter.estimate_idea_response_tokens(len(batch))
                
                self.logger.info(
                    f"Batch {i+1}: {len(batch)} ideas, ~{prompt_tokens} input tokens, "
                    f"~{completion_tokens} output tokens, {prompt_tokens + completion_tokens} total tokens"
                )
                
                # Store in batch data for tracking
                self.batch_data["batches"][i+1] = {
                    "text_len": len(json.dumps(batch, indent=2)),
                    "token_count": prompt_tokens + completion_tokens,
                    "ideas_in_batch": len(batch),
                    "estimated_prompt_tokens": prompt_tokens,
                    "estimated_completion_tokens": completion_tokens,
                    "estimated_cost": self.token_counter.calculate_batch_cost(prompt_tokens, completion_tokens)
                }
                
                # Update totals
                self.batch_data["total_token_count"] += (prompt_tokens + completion_tokens)
                self.batch_data["input_token_count"] += prompt_tokens
                self.batch_data["output_token_count"] += completion_tokens
                self.batch_data["estimated_cost"] += self.batch_data["batches"][i+1]["estimated_cost"]
        
        return batches
    
    def create_batches_by_text_limit(self, ideas, batch_size):
        """
        Create batches such that the total text length of the titles in each batch
        does not exceed max_text_count.
        
        Args:
            ideas: List of idea dictionaries
            batch_size: Maximum total text length per batch
            
        Returns:
            List of batches, where each batch is a list of ideas
        """
        batches = []
        current_batch = []
        current_text_count = 0
        batch_num = 0
        idea_num = 0

        for idea in ideas:
            # Compute the text count for the idea
            idea_text = idea.get("title", "")
            text_len = len(idea_text)
            idea_num += 1
            
            # If adding this idea would exceed the limit and the current batch is not empty,
            # finish the current batch and start a new one
            if current_text_count + text_len > batch_size:
                batch_num = batch_num + 1 
                if current_batch:
                    batches.append(current_batch)
                
                self.batch_data["batches"][batch_num] = {
                    "text_len": current_text_count,
                    "token_count": 0,
                    "ideas_in_batch": idea_num
                }
                self.batch_data["total_text_count"] += current_text_count
                
                current_batch = []
                current_text_count = 0
                idea_num = 0
            
            current_batch.append(idea)
            current_text_count += text_len
        
        # Add any remaining ideas as the last batch
        if current_batch:
            batches.append(current_batch)
            batch_num = batch_num + 1 
            self.batch_data["batches"][batch_num] = {
                "text_len": current_text_count,
                "token_count": 0,
                "ideas_in_batch": idea_num
            }
            self.batch_data["total_text_count"] += current_text_count
        
        if self.logger:
            self.logger.info(f"Created {batch_num} batches")
        
        return batches
    
    def create_simple_batches(self, ideas, batch_size):
        """
        Create batches of ideas with a fixed number of items per batch.
        
        Args:
            ideas: List of idea dictionaries
            batch_size: Number of ideas per batch
            
        Returns:
            List of batches, where each batch is a list of ideas
        """
        return [ideas[i:i+batch_size] for i in range(0, len(ideas), batch_size)]
    
    def update_batch_stats(self, batch_num, api_response):
        """
        Update statistics for a batch after API processing.
        
        Args:
            batch_num: The batch number
            api_response: The API response containing usage information
        """
        if batch_num not in self.batch_data["batches"]:
            self.batch_data["batches"][batch_num] = {
                "text_len": 0,
                "token_count": 0,
                "ideas_in_batch": 0
            }
            
        self.batch_data["batches"][batch_num]["token_count"] = api_response.usage.total_tokens
        self.batch_data["total_token_count"] += api_response.usage.total_tokens
        self.batch_data["input_token_count"] += api_response.usage.prompt_tokens
        self.batch_data["output_token_count"] += api_response.usage.completion_tokens
        
        if self.logger:
            current_batch_data = self.batch_data["batches"][batch_num]
            self.logger.info(f"Batch {batch_num} usage stats: {api_response.usage}")
            self.logger.info(
                f"Batch {batch_num} data: "
                f"Token count: {current_batch_data['token_count']}, "
                f"Text count: {current_batch_data['text_len']}, "
                f"Idea count: {current_batch_data['ideas_in_batch']}"
            )
            self.logger.info(
                f"Total batch data: "
                f"Total token count: {self.batch_data['total_token_count']}, "
                f"Total text count: {self.batch_data['total_text_count']}"
            )
    
    def get_batch_stats(self):
        """Get the current batch statistics."""
        return self.batch_data