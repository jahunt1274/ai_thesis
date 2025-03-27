"""
Idea categorizer for the AI thesis analysis.
"""

import os
import json
import time
import math
import concurrent.futures
from typing import Dict, List, Any, Optional, Tuple, Callable
import openai

from config import OPENAI_API_KEY, DEFAULT_MODEL, IDEA_CATEGORIES, DEFAULT_BATCH_SIZE, DEFAULT_MAX_WORKERS
from src.utils import FileHandler, get_logger

logger = get_logger("idea_categorizer")


class IdeaCategorizer:
    """Categorizes ideas using OpenAI API."""
    
    def __init__(
            self, 
            ideas: List[Dict[str, Any]], 
            output_dir: str,
            api_key: str = OPENAI_API_KEY,
            model: str = DEFAULT_MODEL,
            batch_size: int = DEFAULT_BATCH_SIZE,
            max_workers: int = DEFAULT_MAX_WORKERS,
            categories: Optional[List[str]] = None
        ):
        """
        Initialize the idea categorizer.
        
        Args:
            ideas: List of ideas to categorize
            output_dir: Directory to save output files
            api_key: OpenAI API key
            model: OpenAI model to use
            batch_size: Size of batches for API calls
            max_workers: Maximum number of concurrent workers
            categories: List of categories to use (defaults to IDEA_CATEGORIES)
        """
        self.ideas = ideas
        self.output_dir = output_dir
        self.api_key = api_key
        self.model = model
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.categories = categories or IDEA_CATEGORIES
        
        self.file_handler = FileHandler()
        self.openai_client = openai.OpenAI(api_key=api_key)
        
        # Initialize trackers
        self.categorized_ideas = []
        self.failed_ideas = []
        self.metrics = self._initialize_metrics()
        
        # Create output file paths
        self.output_file = self.file_handler.generate_filename(
            output_dir,
            prefix="categorized_ideas",
            suffix=self.model
        )
        self.metrics_file = self.file_handler.generate_filename(
            output_dir,
            prefix="categorization_metrics",
            suffix=self.model
        )
        
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Initialized IdeaCategorizer with {len(ideas)} ideas using {model} model")
    
    def categorize(self) -> List[Dict[str, Any]]:
        """
        Categorize all ideas.
        
        Returns:
            List of categorized ideas
        """
        start_time = time.time()
        
        # Create batches
        batches = self._create_batches()
        logger.info(f"Created {len(batches)} batches of size ~{self.batch_size}")
        
        # Process batches using appropriate method (parallel or sequential)
        if self.max_workers > 1 and len(batches) > 1:
            self._process_batches_parallel(batches)
        else:
            self._process_batches_sequential(batches)
        
        # Calculate average tokens per idea
        if self.metrics["successful_categorizations"] > 0:
            self.metrics["avg_tokens_per_idea"] = (
                self.metrics["total_tokens"] / self.metrics["successful_categorizations"]
            )
        
        # Calculate total time
        end_time = time.time()
        self.metrics["total_time"] = end_time - start_time
        
        # Save results
        self.save_results()
        
        self._log_completion_summary()
        
        return self.categorized_ideas
    
    def save_results(self):
        """Save categorized ideas and metrics to files."""
        # Save categorized ideas
        self.file_handler.save_json(self.categorized_ideas, self.output_file)
        logger.info(f"Saved categorized ideas to {self.output_file}")
        
        # Save metrics
        self.file_handler.save_json(self.metrics, self.metrics_file)
        logger.info(f"Saved metrics to {self.metrics_file}")
    
    def _initialize_metrics(self) -> Dict[str, Any]:
        """Initialize metrics dictionary."""
        return {
            "total_ideas": len(self.ideas),
            "successful_categorizations": 0,
            "failed_categorizations": 0,
            "total_tokens": 0,
            "total_cost": 0,
            "avg_tokens_per_idea": 0,
            "total_time": 0,
            "batches": []
        }
    
    def _create_batches(self) -> List[List[Dict[str, Any]]]:
        """
        Create batches of ideas for efficient processing.
        
        Returns:
            List of idea batches
        """
        if not self.ideas:
            return []
        
        # Calculate total number of batches
        num_batches = math.ceil(len(self.ideas) / self.batch_size)
        
        # Create batches
        batches = []
        for i in range(num_batches):
            start_idx = i * self.batch_size
            end_idx = min((i + 1) * self.batch_size, len(self.ideas))
            batches.append(self.ideas[start_idx:end_idx])
        
        return batches
    
    def _process_batches_parallel(self, batches: List[List[Dict[str, Any]]]):
        """
        Process batches in parallel using thread pool.
        
        Args:
            batches: List of batches to process
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._process_batch, batch, i+1): i+1
                for i, batch in enumerate(batches)
            }
            
            for future in concurrent.futures.as_completed(futures):
                batch_num = futures[future]
                try:
                    batch_results, batch_metrics = future.result()
                    self._update_metrics(batch_results, batch_metrics)
                    logger.info(f"Batch {batch_num} completed: {len(batch_results)} ideas categorized")
                    
                except Exception as e:
                    logger.error(f"Error processing batch {batch_num}: {str(e)}")
                    self.metrics["failed_categorizations"] += len(batches[batch_num-1])
    
    def _process_batches_sequential(self, batches: List[List[Dict[str, Any]]]):
        """
        Process batches sequentially.
        
        Args:
            batches: List of batches to process
        """
        for i, batch in enumerate(batches):
            try:
                batch_results, batch_metrics = self._process_batch(batch, i+1)
                self._update_metrics(batch_results, batch_metrics)
                logger.info(f"Batch {i+1} completed: {len(batch_results)} ideas categorized")
            except Exception as e:
                logger.error(f"Error processing batch {i+1}: {str(e)}")
                self.metrics["failed_categorizations"] += len(batch)
    
    def _update_metrics(self, batch_results: List[Dict[str, Any]], batch_metrics: Dict[str, Any]):
        """
        Update metrics with batch results.
        
        Args:
            batch_results: List of categorized ideas from the batch
            batch_metrics: Metrics from the batch processing
        """
        # Update categorized ideas
        self.categorized_ideas.extend(batch_results)
        
        # Update metrics
        self.metrics["successful_categorizations"] += len(batch_results)
        self.metrics["total_tokens"] += batch_metrics.get("total_tokens", 0)
        
        # Calculate cost based on model
        batch_metrics["cost"] = self._calculate_batch_cost(batch_metrics)
        self.metrics["total_cost"] += batch_metrics.get("cost", 0)
        self.metrics["batches"].append(batch_metrics)
    
    def _calculate_batch_cost(self, batch_metrics: Dict[str, Any]) -> float:
        """
        Calculate the cost for a batch based on model and token usage.
        
        Args:
            batch_metrics: Batch processing metrics
            
        Returns:
            Estimated cost
        """
        prompt_tokens = batch_metrics.get("prompt_tokens", 0)
        completion_tokens = batch_metrics.get("completion_tokens", 0)
        
        if self.model == "gpt-4o":
            # $0.01 per 1K input tokens, $0.03 per 1K output tokens (estimated)
            input_cost = (prompt_tokens / 1000) * 0.01
            output_cost = (completion_tokens / 1000) * 0.03
            return input_cost + output_cost
        
        elif self.model == "gpt-3.5-turbo":
            # $0.0015 per 1K input tokens, $0.002 per 1K output tokens (estimated)
            input_cost = (prompt_tokens / 1000) * 0.0015
            output_cost = (completion_tokens / 1000) * 0.002
            return input_cost + output_cost
        
        # Default for unknown models
        return 0
    
    def _process_batch(self, batch: List[Dict[str, Any]], batch_num: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Process a batch of ideas.
        
        Args:
            batch: List of ideas to categorize
            batch_num: Batch number for logging
            
        Returns:
            Tuple of (categorized ideas, batch metrics)
        """
        batch_metrics = {
            "batch_num": batch_num,
            "batch_size": len(batch),
            "start_time": time.time(),
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "processing_time": 0
        }
        
        try:
            # Prepare batch for API call
            batch_content = self._prepare_batch_content(batch)
            
            # Generate prompt
            prompt = self._build_categorization_prompt(batch_content)
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for categorizing startup ideas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            
            # Update token metrics
            batch_metrics["prompt_tokens"] = response.usage.prompt_tokens
            batch_metrics["completion_tokens"] = response.usage.completion_tokens
            batch_metrics["total_tokens"] = response.usage.total_tokens
            
            # Process the response
            response_text = response.choices[0].message.content
            
            # Parse categorized ideas
            categorized_ideas = self._parse_response(response_text, batch)
            
            # Calculate processing time
            batch_metrics["end_time"] = time.time()
            batch_metrics["processing_time"] = batch_metrics["end_time"] - batch_metrics["start_time"]
            
            return categorized_ideas, batch_metrics
            
        except Exception as e:
            logger.error(f"Error in batch {batch_num}: {str(e)}")
            
            # Update batch metrics with error
            batch_metrics["end_time"] = time.time()
            batch_metrics["processing_time"] = batch_metrics["end_time"] - batch_metrics["start_time"]
            batch_metrics["error"] = str(e)
            
            # Add ideas to failed list
            self.failed_ideas.extend(batch)
            
            return [], batch_metrics
    
    def _prepare_batch_content(self, batch: List[Dict[str, Any]]) -> str:
        """
        Prepare batch content for API call.
        
        Args:
            batch: List of ideas to categorize
            
        Returns:
            JSON string of simplified idea data
        """
        # Simplify ideas to just the necessary fields
        simplified_batch = [
            {
                "_id": idea.get("id"),
                "title": idea.get("title"),
                "description": idea.get("description", "")
            }
            for idea in batch
        ]
        
        return json.dumps(simplified_batch, indent=2)
    
    def _build_categorization_prompt(self, batch_content: str) -> str:
        """
        Build the prompt for idea categorization.
        
        Args:
            batch_content: JSON string of idea batch
            
        Returns:
            Formatted prompt
        """
        return (
            "You are an expert in categorizing startup ideas. "
            "Categorize each of the following ideas into one of the provided categories.\n\n"
            f"Categories: {self.categories}\n\n"
            "Do not create additional categories outside of the given list. "
            "For each idea, return a JSON object with the original '_id', and a 'category' field indicating the chosen category.\n"
            "Return your answer as a JSON array of objects with this structure: { '_id': original id, 'category': chosen category }\n\n"
            "Here are the ideas to categorize:\n"
            f"{batch_content}"
        )
    
    def _parse_response(self, response_text: str, original_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse the API response to extract categorized ideas.
        
        Args:
            response_text: Text response from API
            original_batch: Original batch of ideas
            
        Returns:
            List of categorized ideas
        """
        # Clean response text
        response_text = self._clean_api_response(response_text)
        
        # Parse JSON
        try:
            categorizations = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing API response: {str(e)}")
            logger.error(f"Response text: {response_text}")
            return []
        
        # Create map of original ideas by ID
        original_ideas = {idea.get("id"): idea for idea in original_batch}
        
        # Build categorized ideas
        categorized_ideas = []
        
        for item in categorizations:
            # Extract ID and category
            idea_id = item.get("_id")
            category = item.get("category")
            
            if not idea_id or not category:
                logger.warning(f"Missing ID or category in response item: {item}")
                continue
            
            # Find original idea
            original_idea = original_ideas.get(idea_id)
            if not original_idea:
                logger.warning(f"Couldn't find original idea with ID: {idea_id}")
                continue
            
            # Create categorized idea
            categorized_idea = original_idea.copy()
            categorized_idea["category"] = category
            
            categorized_ideas.append(categorized_idea)
        
        return categorized_ideas
    
    def _clean_api_response(self, response_text: str) -> str:
        """
        Clean API response text by removing markdown and other formatting.
        
        Args:
            response_text: Raw response text from API
            
        Returns:
            Cleaned response text
        """
        # Clean response text
        response_text = response_text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
        
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        return response_text.strip()
    
    def _log_completion_summary(self):
        """Log a summary of the categorization process."""
        logger.info(f"Categorization completed in {self.metrics['total_time']:.2f} seconds")
        logger.info(f"Categorized {self.metrics['successful_categorizations']} ideas successfully")
        logger.info(f"Failed to categorize {self.metrics['failed_categorizations']} ideas")
        logger.info(f"Average tokens per idea: {self.metrics['avg_tokens_per_idea']:.2f}")
        logger.info(f"Estimated cost: ${self.metrics['total_cost']:.4f}")