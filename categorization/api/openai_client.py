import time
import json
import random
from openai import OpenAI

class OpenAIClient:
    """Handles interactions with the OpenAI API."""
    
    def __init__(self, api_key, model, logger=None):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: OpenAI API key
            model: Model to use for requests (e.g., "gpt-4o")
            logger: Logger object
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.logger = logger
        self.test_mode = False  # Flag to toggle test mode

        # Timing metrics storage
        self.metrics = {
            "requests": [],
            "total_time": 0,
            "total_tokens": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_payload_size": 0
        }
    
    def set_test_mode(self, enabled=True):
        """Enable or disable test mode."""
        self.test_mode = enabled
    
    def categorize_ideas(self, batch, categories, batch_num=None):
        """
        Send a batch of ideas to OpenAI for categorization.
        
        Args:
            batch: List of idea dictionaries
            categories: List of available categories
            batch_num: Optional batch number for logging
            
        Returns:
            tuple: (processed_response, completion_tokens, api_response, timing_info)
        """
        if self.test_mode:
            return self._dummy_categorize(batch, categories)
        
        batch_content = json.dumps(batch, indent=2)
        prompt = self._build_categorization_prompt(batch_content, categories)

        # Calculate payload size in bytes
        payload_size = len(prompt.encode('utf-8'))
        
        batch_info = f"Batch {batch_num}" if batch_num is not None else "Batch"
        if self.logger:
            self.logger.info(f"{batch_info} in progress")
        
        # Record request time
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for categorizing startup ideas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )

            # Calculate response time
            end_time = time.time()
            response_time = end_time - start_time

            # TODO calculate prompt_tokens and response_tokens for visualization?
            # Calculate tokens per second
            total_tokens = response.usage.total_tokens
            tokens_per_second = total_tokens / response_time if response_time > 0 else 0

            # Store metrics for this request
            request_metrics = {
                "batch_num": batch_num,
                "response_time": response_time,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": total_tokens,
                "payload_size": payload_size,
                "tokens_per_second": tokens_per_second,
                "ideas_count": len(batch)
            }

            # Update aggregate metrics
            self.metrics["requests"].append(request_metrics)
            self.metrics["total_time"] += response_time
            self.metrics["total_tokens"] += total_tokens
            self.metrics["total_prompt_tokens"] += response.usage.prompt_tokens
            self.metrics["total_completion_tokens"] += response.usage.completion_tokens
            self.metrics["total_payload_size"] += payload_size

            if self.logger:
                self.logger.info(
                    f"{batch_info} completed in {response_time:.2f}s - "
                    f"{total_tokens} tokens ({tokens_per_second:.2f} tokens/s) - "
                    f"Payload: {payload_size/1024:.2f} KB"
                )
            
            # TODO Check what is being returned
            return response.choices[0].message.content, response.usage.completion_tokens, response, request_metrics
            
        except Exception as e:
            # Calculate response time for errors
            end_time = time.time()
            response_time = end_time - start_time

            if self.logger:
                self.logger.error(f"API request error: {e}")
            
            # Store error metrics
            error_metrics = {
                "batch_num": batch_num,
                "response_time": response_time,
                "error": str(e),
                "payload_size": payload_size,
                "ideas_count": len(batch)
            }
            self.metrics["requests"].append(error_metrics)
            self.metrics["total_time"] += response_time
            self.metrics["total_payload_size"] += payload_size

            raise
    
    def _build_categorization_prompt(self, batch_content, categories):
        """
        Build the prompt for idea categorization.
        
        Args:
            batch_content: JSON string of idea batch
            categories: List of available categories
            
        Returns:
            str: Formatted prompt
        """
        return (
            "You are an expert startup idea categorizer. "
            "Categorize each of the following ideas into one of the given categories.\n\n"
            f"Categories: {categories}\n\n"
            "Do not create additional categories outside of the given list. "
            "For each idea, return an object with the original '_id', and an additional field 'category' indicating the chosen category. "
            "Return your answer as a JSON array of objects with the following structure:\n"
            '{ "_id": original id, "category": chosen category }\n\n'
            "Here are the ideas:\n"
            f"{batch_content}"
        )
    
    def _dummy_categorize(self, batch, categories):
        """
        Generate dummy responses for testing.
        
        Args:
            batch: List of idea dictionaries
            categories: List of available categories
            
        Returns:
            tuple: (JSON response string, dummy completion tokens, dummy response, timing info)
        """
        # Simulate API response time (between 0.5 and 2 seconds)
        start_time = time.time()
        sleep_time = random.uniform(0.5, 2.0) 
        time.sleep(sleep_time)
        end_time = time.time()
        response_time = end_time - start_time

        dummy_results = []
        for idea in batch:
            dummy_results.append({
                "_id": idea["_id"],
                "category": random.choice(categories)
            })
        
        # Simulate API response
        dummy_json = json.dumps(dummy_results)
        payload_size = len(dummy_json.encode('utf-8'))
        dummy_tokens = len(dummy_json) // 4  # Rough approximation
        
        # Create timing info
        request_metrics = {
            "response_time": response_time,
            "prompt_tokens": dummy_tokens // 2,
            "completion_tokens": dummy_tokens // 2,
            "total_tokens": dummy_tokens,
            "payload_size": payload_size,
            "tokens_per_second": dummy_tokens / response_time,
            "ideas_count": len(batch)
        }

        # Update aggregate metrics
        self.metrics["requests"].append(request_metrics)
        self.metrics["total_time"] += response_time
        self.metrics["total_tokens"] += dummy_tokens
        self.metrics["total_prompt_tokens"] += dummy_tokens // 2
        self.metrics["total_completion_tokens"] += dummy_tokens // 2
        self.metrics["total_payload_size"] += payload_size
        
        # Create a dummy response object with a usage attribute
        class DummyUsage:
            def __init__(self, tokens):
                self.total_tokens = tokens
                self.prompt_tokens = tokens // 2
                self.completion_tokens = tokens // 2
                
        class DummyResponse:
            def __init__(self, tokens):
                self.usage = DummyUsage(tokens)
                
        dummy_response = DummyResponse(dummy_tokens)

        if self.logger:
            self.logger.info(
                f"Dummy request completed in {response_time:.2f}s - "
                f"{dummy_tokens} tokens ({dummy_tokens / response_time:.2f} tokens/s) - "
                f"Payload: {payload_size/1024:.2f} KB"
            )
        
        return dummy_json, dummy_tokens // 2, dummy_response, request_metrics
    
    def get_metrics(self):
        """Get the API timing metrics."""
        # Calculate aggregate metrics
        if self.metrics["total_time"] > 0:
            self.metrics["avg_tokens_per_second"] = self.metrics["total_tokens"] / self.metrics["total_time"]
        else:
            self.metrics["avg_tokens_per_second"] = 0
            
        # Count successful requests
        successful_requests = [r for r in self.metrics["requests"] if "error" not in r]
        self.metrics["successful_requests"] = len(successful_requests)
        self.metrics["failed_requests"] = len(self.metrics["requests"]) - len(successful_requests)
        
        # Add average metrics for successful requests
        if successful_requests:
            self.metrics["avg_response_time"] = sum(r["response_time"] for r in successful_requests) / len(successful_requests)
            self.metrics["avg_tokens"] = sum(r["total_tokens"] for r in successful_requests) / len(successful_requests)
            self.metrics["avg_payload_size"] = sum(r["payload_size"] for r in successful_requests) / len(successful_requests)
        
        return self.metrics