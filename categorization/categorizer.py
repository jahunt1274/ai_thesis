import os
import json
import time
import math
import concurrent.futures
import openai
from datetime import timedelta

from utils.file_handler import FileHandler
from batch_manager import BatchManager
from api.openai_client import OpenAIClient
from api.response_processor import ResponseProcessor
from api.token_analyzer import TokenCounter

class IdeaCategorizer:
    """Main class that orchestrates the idea categorization process."""
    
    def __init__(
            self,
            input_file,
            output_dir,
            batch_size,
            api_key,
            model,
            categories,
            logger=None,
            is_batch=True,
            max_workers=2,
            skip_delay = True
        ):
        """
        Initialize the idea categorizer.
        
        Args:
            input_file: Path to input JSON file containing ideas
            output_dir: Directory to save output files
            batch_size: Size of batches for processing
            api_key: OpenAI API key
            model: Model to use for API requests
            categories: List of categories to use
            logger: Logger object
            is_batch: Whether to use batch processing
            max_workers: Maximum number of concurrent workers
        """
        self.logger = logger
        self.input_file = input_file
        self.output_dir = output_dir
        self.batch_size = batch_size
        self.is_batch = is_batch
        self.max_workers = max_workers
        self.model = model
        self.categories = categories
        self.skip_delay =skip_delay
        
        # Initialize components
        self.token_counter = TokenCounter(model)
        self.file_handler = FileHandler()
        self.batch_manager = BatchManager(
            logger=logger, 
            token_counter=self.token_counter
        )
        self.openai_client = OpenAIClient(api_key, model, logger)
        self.response_processor = ResponseProcessor(logger)
        
        # Initialize state
        self.ideas = None
        self.results = []
        self.ideas_to_retry = []
        self.retry_count = 0
        self.min_delay = 1.0
        
        # Initialize performance metrics
        self.performance_metrics = {
            "start_time": None,
            "end_time": None,
            "total_runtime": 0,
            "load_time": 0,
            "processing_time": 0,
            "retry_time": 0,
            "saving_time": 0,
            "batch_metrics": {},
            "timing_data": [],
            "token_metrics": {
                "total_tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_cost": 0.0,
                "token_distribution": {}
            }
        }
        
        # Set up output files
        self.output_file = self.file_handler.generate_filename(
            output_dir,
            prefix="categorized_ideas",
            suffix=self.model
        )

        # Set up performance metrics file
        self.metrics_file = self.file_handler.generate_filename(
            os.path.join(output_dir, "metrics"),
            prefix="performance_metrics",
            suffix=self.model
        )
        
        if logger:
            logger.info(f"Initialized IdeaCategorizer with model {model}")
            logger.info(f"Output will be saved to {self.output_file}")
    
    def format_time_delta(self, seconds):
        """Format seconds into a human-readable time string."""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if td.days > 0:
            return f"{td.days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds:.2f}s"
    
    def load_ideas(self):
        """Load ideas from the input file."""
        start_time = time.time()
        self.ideas = self.file_handler.load_json(self.input_file)
        end_time = time.time()

        self.performance_metrics["load_time"] = end_time - start_time
        
        if self.logger:
            load_time = self.format_time_delta(self.performance_metrics["load_time"])
            self.logger.info(f"Loaded {len(self.ideas)} ideas from {self.input_file} in {load_time}")
    
    def save_results(self, filepath=None):
        """Save current results to the specified file."""
        start_time = time.time()
        
        if filepath is None:
            filepath = self.output_file
            
        self.file_handler.save_json(self.results, filepath)
        
        end_time = time.time()
        saving_time = end_time - start_time
        self.performance_metrics["saving_time"] += saving_time

        if self.logger:
            self.logger.info(f"Saved {len(self.results)} categorized ideas to {filepath} in {self.format_time_delta(saving_time)}")
    
    def save_performance_metrics(self):
        """Save the performance metrics to a JSON file."""
        # Get API metrics
        api_metrics = self.openai_client.get_metrics()
        batch_stats = self.batch_manager.get_batch_stats()
        
        # Combine with our metrics
        combined_metrics = {
            "runtime": {
                "total_seconds": self.performance_metrics["total_runtime"],
                "formatted": self.format_time_delta(self.performance_metrics["total_runtime"]),
                "breakdown": {
                    "loading": {
                        "seconds": self.performance_metrics["load_time"],
                        "percentage": (self.performance_metrics["load_time"] / self.performance_metrics["total_runtime"]) * 100 if self.performance_metrics["total_runtime"] > 0 else 0,
                        "formatted": self.format_time_delta(self.performance_metrics["load_time"])
                    },
                    "processing": {
                        "seconds": self.performance_metrics["processing_time"],
                        "percentage": (self.performance_metrics["processing_time"] / self.performance_metrics["total_runtime"]) * 100 if self.performance_metrics["total_runtime"] > 0 else 0,
                        "formatted": self.format_time_delta(self.performance_metrics["processing_time"])
                    },
                    "retries": {
                        "seconds": self.performance_metrics["retry_time"],
                        "percentage": (self.performance_metrics["retry_time"] / self.performance_metrics["total_runtime"]) * 100 if self.performance_metrics["total_runtime"] > 0 else 0,
                        "formatted": self.format_time_delta(self.performance_metrics["retry_time"])
                    },
                    "saving": {
                        "seconds": self.performance_metrics["saving_time"],
                        "percentage": (self.performance_metrics["saving_time"] / self.performance_metrics["total_runtime"]) * 100 if self.performance_metrics["total_runtime"] > 0 else 0,
                        "formatted": self.format_time_delta(self.performance_metrics["saving_time"])
                    }
                }
            },
            "api": api_metrics,
            "results": {
                "total_ideas": len(self.ideas) if self.ideas else 0,
                "processed_ideas": len(self.results),
                "success_rate": (len(self.results) / len(self.ideas)) * 100 if self.ideas and len(self.ideas) > 0 else 0
            },
            "config": {
                "model": self.model,
                "batch_size": self.batch_size,
                "processing_mode": "Parallel" if self.is_batch else "Sequential",
                "max_workers": self.max_workers,
                "input_file": self.input_file,
                "output_file": self.output_file
            },
            "batch_metrics": self.performance_metrics["batch_metrics"],
            "batch_timing": self.performance_metrics["timing_data"],
            "token_stats": self.performance_metrics["token_metrics"],
            "batch_stats": batch_stats
        }
        
        # Save to file
        self.file_handler.save_json(combined_metrics, self.metrics_file)
        
        if self.logger:
            self.logger.info(f"Performance metrics saved to {self.metrics_file}")
    
    def process_single_batch(self, batch, batch_num):
        """
        Process a single batch of ideas.
        
        Args:
            batch: List of idea dictionaries
            batch_num: Batch number for tracking
            
        Returns:
            tuple: (batch_results, should_retry)
        """
        batch_start_time = time.time()
        batch_metrics = {
            "batch_num": batch_num,
            "ideas_count": len(batch),
            "start_time": batch_start_time,
        }

        try:
            # Call the API to categorize the batch
            response_text, completion_tokens, api_response, request_metrics = self.openai_client.categorize_ideas(
                batch, self.categories, batch_num
            )
            
            # Update batch statistics
            self.batch_manager.update_batch_stats(batch_num, api_response)
            
            # Check if response is too large (potential truncation)
            if completion_tokens >= 4096:
                if self.logger:
                    self.logger.warning(f"Batch {batch_num}: Large completion size ({completion_tokens} tokens), flagging for retry")
                
                batch_end_time = time.time()
                batch_metrics.update({
                    "end_time": batch_end_time,
                    "total_time": batch_end_time - batch_start_time,
                    "status": "flagged_for_retry",
                    "api_metrics": request_metrics
                })
                self.performance_metrics["batch_metrics"][batch_num] = batch_metrics
                self.performance_metrics["timing_data"].append(batch_metrics)

                return None, True
            
            # Process the response
            process_start = time.time()
            batch_results = self.response_processor.parse_json_response(response_text, batch_num)
            process_end = time.time()
            process_time = process_end - process_start

            batch_end_time = time.time()
            batch_metrics.update({
                "end_time": batch_end_time,
                "total_time": batch_end_time - batch_start_time,
                "api_time": request_metrics["response_time"],
                "processing_time": process_time,
                "status": "success",
                "processed_ideas": len(batch_results),
                "api_metrics": request_metrics,
                "token_metrics": {
                    "input_tokens": request_metrics["prompt_tokens"],
                    "output_tokens": request_metrics["completion_tokens"],
                    "total_tokens": request_metrics["total_tokens"],
                    "cost": request_metrics.get("cost", 0.0)
                }
            })

            self.performance_metrics["batch_metrics"][batch_num] = batch_metrics
            self.performance_metrics["timing_data"].append(batch_metrics)
            
            if self.logger:
                self.logger.info(
                    f"Batch {batch_num} completed in {self.format_time_delta(batch_metrics['total_time'])} "
                    f"(API: {self.format_time_delta(request_metrics['response_time'])}, "
                    f"Processing: {self.format_time_delta(process_time)})"
                )
                current_batch_data = self.batch_manager.batch_data["batches"][batch_num]
                if current_batch_data['estimated_prompt_tokens']:
                    self.logger.info(f"Batch {batch_num} estimated prompt tokens: {current_batch_data['estimated_prompt_tokens']}")
                if current_batch_data['estimated_completion_tokens']:
                    self.logger.info(f"Batch {batch_num} estimated completion tokens: {current_batch_data['estimated_completion_tokens']}")
            
            return batch_results, False
            
        except Exception as e:
            batch_end_time = time.time()
            batch_metrics.update({
                "end_time": batch_end_time,
                "total_time": batch_end_time - batch_start_time,
                "status": "error",
                "error": str(e)
            })

            self.performance_metrics["batch_metrics"][batch_num] = batch_metrics
            self.performance_metrics["timing_data"].append(batch_metrics)
            
            if self.logger:
                self.logger.error(f"Error processing batch {batch_num}: {e}")
            return None, True
    
    def batch_process(self, ideas, batch_size):
        """
        Process ideas in parallel batches.
        
        Args:
            ideas: List of ideas to process
            batch_size: Size limit for each batch
        """
        process_start = time.time()
        
        # TODO Figure out how many tokens per batch based on response time and tpm/rpm limits
        # Create batches based on token limits
        batches = self.batch_manager.create_batches_by_token_limit(ideas, self.categories)
        
        # If token batching failed or returned empty, fall back to text-based batching
        if not batches:
            batches = self.batch_manager.create_batches_by_text_limit(ideas, batch_size)
        
        # Create a directory for partial responses
        partial_responses_dir = os.path.join(self.output_dir, "partial_responses")
        os.makedirs(partial_responses_dir, exist_ok=True)
        
        # Generate a filepath for preliminary batch responses
        prelim_response_filepath = self.file_handler.generate_filename(
            partial_responses_dir,
            prefix=self.model,
            suffix="preliminary_batch_responses"
        )
        
        # Save batch information for debugging
        batch_info_filepath = os.path.join(self.output_dir, "batches.json")
        self.file_handler.save_json(batches, batch_info_filepath)
        
        # Calculate rate limit delay if needed
        min_delay = self.min_delay if self.skip_delay else self.calculate_delay_from_batch_size(batches)
 
        
        # Process batches in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_batchnum = {
                executor.submit(self.process_single_batch, batch, i+1): i+1 
                for i, batch in enumerate(batches)
            }
            
            # Submit initial batch of tasks (up to max_workers)
            initial_batches = min(self.max_workers, len(batches))
            for i in range(initial_batches):
                future = executor.submit(self.process_single_batch, batches[i], i+1)
                future_to_batchnum[future] = i+1
            
            # Track the next batch to submit
            next_batch_idx = initial_batches
            
            for future in concurrent.futures.as_completed(future_to_batchnum):
                batch_number = future_to_batchnum[future]
                try:
                    batch_results, should_retry = future.result()
                    
                    if should_retry:
                        self.handle_retry(batches[batch_number-1], batch_number)
                        continue
                    
                    if batch_results:
                        self.results.extend(batch_results)
                        
                        # Save progress periodically
                        self.file_handler.save_json(self.results, prelim_response_filepath)
                
                except openai.RateLimitError as e:
                    if self.logger:
                        self.logger.error(f"OpenAI API request exceeded rate limit: {e}")
                    self.handle_retry(batches[batch_number-1], batch_number)
                    
                    # Sleep to allow rate limit to pass
                    time.sleep(10)
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Batch {batch_number} generated an exception: {e}")
                    self.handle_retry(batches[batch_number-1], batch_number)
        
                # Submit next batch if available
                if next_batch_idx < len(batches):
                    # Apply rate limiting delay if needed
                    if min_delay > 0:
                        time.sleep(min_delay)
                        
                    future = executor.submit(self.process_single_batch, batches[next_batch_idx], next_batch_idx+1)
                    future_to_batchnum[future] = next_batch_idx+1
                    next_batch_idx += 1
        
        process_end = time.time()
        self.performance_metrics["processing_time"] += (process_end - process_start)
        
        # Save final results
        self.save_results()
    
    def sequential_process(self, ideas, batch_size):
        """
        Process ideas in sequential batches.
        
        Args:
            ideas: List of ideas to process
            batch_size: Number of ideas per batch
        """
        process_start = time.time()
        
        # Create batches based on token limits
        batches = self.batch_manager.create_batches_by_token_limit(ideas, self.categories)
        
        # If token batching failed or returned empty, fall back to text-based batching
        if not batches:
            batches = self.batch_manager.create_simple_batches(ideas, batch_size)
        
        if self.logger:
            self.logger.info(f"Created {len(batches)} batches for sequential processing")
        
        # Calculate rate limit delay if needed
        min_delay = self.min_delay if self.skip_delay else self.calculate_delay_from_batch_size(batches)

        for i, batch in enumerate(batches):
            batch_num = i + 1
            if self.logger:
                self.logger.info(f"Processing batch {batch_num}...")
            
            batch_results, should_retry = self.process_single_batch(batch, batch_num)
            
            if should_retry:
                self.handle_retry(batch, batch_num)
                continue
                
            if batch_results:
                self.results.extend(batch_results)
            
            # Apply rate limiting delay
            delay = max(min_delay, 1.0)  # Use at least 1 second between requests
            if self.logger:
                self.logger.info(f"Waiting {delay:.2f} seconds before next request (rate limiting)")
            time.sleep(delay)
        
        process_end = time.time()
        self.performance_metrics["processing_time"] += (process_end - process_start)
        
        self.save_results()
    
    def calculate_delay_from_batch_size(self, batches):
        """
        Calculate delay based on rate limit and batch size.
        
        Args:
            batches: list of batches to be processed
        
        Returns:
            Recommended minimum delay in seconds
        """
        rate_limits = self.token_counter.get_rate_limits()
        if self.logger:
            self.logger.info(f"Rate limits for {self.model}: {rate_limits['tpm']} tokens/min, {rate_limits['rpm']} requests/min")
        
        # Estimate tokens per batch
        avg_batch_size = sum(len(batch) for batch in batches) / len(batches) if batches else 0
        estimated_tokens_per_batch = avg_batch_size * 1000  # Rough estimate: ~1000 tokens per idea
        
        # Calculate minimum delay between requests
        min_delay = 0
        if avg_batch_size > 0:
            # Get batch sizes for rate limit calculation
            batch_sizes = []
            for i, batch in enumerate(batches):
                if i+1 in self.batch_manager.batch_data["batches"]:
                    batch_data = self.batch_manager.batch_data["batches"][i+1]
                    if "token_count" in batch_data and batch_data["token_count"] > 0:
                        batch_sizes.append(batch_data["token_count"])
                    else:
                        # Use estimated token count
                        batch_sizes.append(estimated_tokens_per_batch)
            
            # Calculate delay
            if batch_sizes:
                min_delay = self.token_counter.calculate_rate_limit_delay(batch_sizes)
                if self.logger:
                    self.logger.info(f"Calculated minimum delay between requests: {min_delay:.2f} seconds")
            else:
                # Default to a safe delay if we can't calculate
                min_delay = self.min_delay
        
        return min_delay
    
    def handle_retry(self, batch, batch_number):
        """
        Add a batch to the retry list.
        
        Args:
            batch: Batch to retry
            batch_number: Batch number for logging
        """
        if self.logger:
            self.logger.info(f"Adding batch {batch_number} to retry list")
        
        for idea in batch:
            self.ideas_to_retry.append(idea)
    
    def process_retries(self):
        """Process any ideas that need to be retried."""
        if not self.ideas_to_retry:
            return
            
        retry_start = time.time()
        
        if self.logger:
            self.logger.info(f"Processing {len(self.ideas_to_retry)} retry items with reduced batch size")
        
        # Use a smaller batch size for retries
        retry_batch_size = self.batch_size // 2
        if retry_batch_size < 1:
            retry_batch_size = 1
            
        if self.is_batch:
            self.batch_process(self.ideas_to_retry, retry_batch_size)
        else:
            self.sequential_process(self.ideas_to_retry, retry_batch_size)
            
        retry_end = time.time()
        self.performance_metrics["retry_time"] += (retry_end - retry_start)
        
        # Clear retry list
        self.ideas_to_retry = []
    
    def run(self):
        """Main method to run the categorization process."""
        self.performance_metrics["start_time"] = time.time()
        
        # Load ideas from input file
        self.load_ideas()
        
        # Process ideas
        if self.is_batch:
            self.batch_process(self.ideas, self.batch_size)
        else:
            self.sequential_process(self.ideas, self.batch_size)
        
        # Process any retries
        if self.ideas_to_retry and self.retry_count < 3:
            self.retry_count += 1
            self.process_retries()
        
        # Record end time and calculate total runtime
        self.performance_metrics["end_time"] = time.time()
        self.performance_metrics["total_runtime"] = (
            self.performance_metrics["end_time"] - self.performance_metrics["start_time"]
        )
        
        # Save performance metrics
        self.save_performance_metrics()
        
        # Log final statistics
        if self.logger:
            batch_stats = self.batch_manager.get_batch_stats()
            api_metrics = self.openai_client.get_metrics()
            
            self.logger.info(f"Categorization complete!")
            self.logger.info(f"Total processed ideas: {len(self.results)} of {len(self.ideas)}")
            
            # Log token statistics
            self.logger.info(f"Token usage:")
            self.logger.info(f"  - Input tokens: {batch_stats['input_token_count']}")
            self.logger.info(f"  - Output tokens: {batch_stats['output_token_count']}")
            self.logger.info(f"  - Total tokens: {batch_stats['total_token_count']}")
            self.logger.info(f"  - Estimated cost: ${batch_stats.get('estimated_cost', 0.0):.4f}")
            
            # Log API statistics
            self.logger.info(f"API metrics:")
            self.logger.info(f"  - Total tokens: {api_metrics['input_token_count']}")
            self.logger.info(f"  - Total prompt tokens: {api_metrics['total_prompt_tokens']}")
            self.logger.info(f"  - Total completion tokens: {api_metrics['total_completion_tokens']}")
            self.logger.info(f"  - Total payload size: {api_metrics['total_payload_size']}")
            self.logger.info(f"  - Actual cost: ${api_metrics.get('total_cost', 0.0):.4f}")
            
            # Calculate and log throughput
            ideas_per_second = len(self.results) / self.performance_metrics["total_runtime"]
            tokens_per_second = batch_stats["total_token_count"] / self.performance_metrics["total_runtime"]
            
            self.logger.info(f"Performance metrics:")
            self.logger.info(f"  - Total runtime: {self.format_time_delta(self.performance_metrics['total_runtime'])}")
            self.logger.info(f"  - Loading time: {self.format_time_delta(self.performance_metrics['load_time'])}")
            self.logger.info(f"  - Processing time: {self.format_time_delta(self.performance_metrics['processing_time'])}")
            
            if self.performance_metrics["retry_time"] > 0:
                self.logger.info(f"  - Retry time: {self.format_time_delta(self.performance_metrics['retry_time'])}")
                
            self.logger.info(f"  - Throughput: {ideas_per_second:.2f} ideas/second")
            self.logger.info(f"  - Token rate: {tokens_per_second:.2f} tokens/second")
            
            # Save metrics file location
            self.logger.info(f"Detailed performance metrics saved to: {self.metrics_file}")
            
        return self.results