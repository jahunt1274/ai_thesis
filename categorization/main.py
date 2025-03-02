import argparse
import os
from utils.logger_setup import LoggerSetup
from categorizer import IdeaCategorizer
from config import DATA_DIR, OUTPUT_DIR, LOG_DIR
from constants import IDEA_CATEGORIES, OpenAIModels
from keys import OPENAI_API_THESIS_KEY

def main():
    """Main CLI entry point for the idea categorization tool."""
    
    parser = argparse.ArgumentParser(description='Categorize startup ideas using OpenAI API')

    parser.add_argument(
        '--input', 
        type=str, 
        default=f'{DATA_DIR}/ideas.json', 
        help='Path to input JSON file containing ideas'
    )
    parser.add_argument(
        '--output-dir',
        type=str, 
        default=OUTPUT_DIR, 
        help='Directory to save output files'
    )
    parser.add_argument(
        '--batch-size', 
        type=int, 
        default=1000, 
        help='Maximum size of each batch (in characters for text mode)'
    )
    available_models = [model.value for model in OpenAIModels]
    parser.add_argument(
        '--model', 
        type=str,
        choices=available_models,
        default=OpenAIModels.GPT35.value, 
        help='OpenAI model to use'
    )
    parser.add_argument(
        '--max-workers', 
        type=int, 
        default=2, 
        help='Maximum number of concurrent workers for batch processing'
    )
    parser.add_argument(
        '--sequential', 
        action='store_true', 
        help='Process batches sequentially instead of in parallel'
    )
    parser.add_argument(
        '--test', 
        action='store_true', 
        help='Run in test mode with dummy responses'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    logger_setup = LoggerSetup(LOG_DIR)
    logger = logger_setup.setup_logger(
        'idea_categorization', 
        log_file=f'idea_categorization_{args.model}.log'
    )
    
    logger.info(f"Starting idea categorization with model: {args.model}")
    logger.info(f"Input file: {args.input}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Processing mode: {'Sequential' if args.sequential else 'Parallel'}")
    
    # Initialize categorizer
    categorizer = IdeaCategorizer(
        input_file=args.input,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        api_key=OPENAI_API_THESIS_KEY,
        model=args.model,
        categories=IDEA_CATEGORIES,
        logger=logger,
        is_batch=not args.sequential,
        max_workers=args.max_workers
    )
    
    # Enable test mode if requested
    if args.test:
        logger.info("Running in test mode with dummy responses")
        categorizer.openai_client.set_test_mode(True)
    
    # Run the categorization
    try:
        categorizer.run()
        logger.info("Categorization completed successfully")
    except Exception as e:
        logger.error(f"Error during categorization: {e}")
        raise

if __name__ == "__main__":
    main()