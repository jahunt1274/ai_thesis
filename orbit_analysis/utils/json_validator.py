import json
from typing import Tuple, Optional
from utils.logger import LoggerSetup
from config import LOG_DIR
import re

class JSONValidator:
    def __init__(self, logger=None):
        # Set up logger
        if not logger:
            logger_setup = LoggerSetup(LOG_DIR)
            self.logger = logger_setup.setup_logger('json_validator')
        else:
            self.logger = logger

    def _check_common_issues(self, content: str) -> Optional[str]:
        """Check for common JSON formatting issues."""
        issues = []
        
        # Check for unescaped quotes within strings
        quote_matches = re.finditer(r'"(?:[^"\\]|\\.)*"', content)
        for match in quote_matches:
            string_content = match.group(0)[1:-1]  # Remove outer quotes
            if '"' in string_content and '\\"' not in string_content:
                line_no = content[:match.start()].count('\n') + 1
                issues.append(f"Unescaped quote found in string at line {line_no}")

        # Check for unescaped line breaks in strings
        if re.search(r'"[^"]*[\n\r][^"]*"', content):
            issues.append("Unescaped line breaks found in strings")

        # Check for trailing commas
        if re.search(r',\s*[}\]]', content):
            issues.append("Trailing commas found")

        # Check for JavaScript-style comments
        if re.search(r'//|/\*|\*/', content):
            issues.append("JavaScript-style comments found")

        # Check for missing commas between elements
        if re.search(r'[}\]"]["{\[]', content):
            issues.append("Missing commas between elements")

        return "\n".join(issues) if issues else None
    
    def validate_content(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Validate JSON content and identify specific issues.
        
        Args:
            content (str): JSON content to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # Check for common issues before parsing
        issues = self._check_common_issues(content)
        if issues:
            return False, issues

        # Try to parse JSON
        try:
            json.loads(content)
            return True, None
        except json.JSONDecodeError as e:
            # Get context around the error
            context = self._get_error_context(content, e.lineno, e.colno)
            self.logger.error(
                f"JSON Decode Error: {str(e)}\n"
                f"Line {e.lineno}, Column {e.colno}\n"
                f"Context:\n{context}"
            )
            return False, (
                f"JSON Decode Error: {str(e)}\n"
                f"Line {e.lineno}, Column {e.colno}\n"
                f"Context:\n{context}"
            )
    
    def _fix_json_content(self, content: str) -> str:
        """
        Fix common JSON issues including special characters.
        
        Args:
            content (str): Original JSON content
            
        Returns:
            str: Fixed JSON content
        """
        if self.logger:
            self.logger.info("Attempting to fix JSON issues...")
        
        fixes_applied = []
        
        # Step 1: Handle special characters and whitespace
        # Replace tabs with spaces
        if '\t' in content:
            content = content.replace('\t', '    ')
            fixes_applied.append("Replaced tabs with spaces")
        
        # Replace bullet points and other special characters
        if '•' in content:
            content = content.replace('•', '-')
            fixes_applied.append("Replaced bullet points with hyphens")
        
        # Handle other special characters that might cause issues
        special_chars_map = {
            '\u2013': '-',  # en dash
            '\u2014': '-',  # em dash
            '\u2018': "'",  # left single quote
            '\u2019': "'",  # right single quote
            '\u201C': '"',  # left double quote
            '\u201D': '"',  # right double quote
            '\u2026': '...' # ellipsis
        }
        
        for char, replacement in special_chars_map.items():
            if char in content:
                content = content.replace(char, replacement)
                fixes_applied.append(f"Replaced special character {char} with {replacement}")
        
        # Step 2: Handle line breaks and normalize newlines
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Step 3: Fix escaped quotes inside strings
        # We'll handle this by properly processing string content
        
        # Step 4: Remove comments
        if '//' in content or '/*' in content:
            # Single-line comments
            content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
            # Multi-line comments
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            fixes_applied.append("Removed JavaScript-style comments")
        
        # Step A: First pass for strings
        # Process string literals to fix internal issues
        strings = re.finditer(r'"(?:[^"\\]|\\[^"]|\\"|\\\\)*"', content)
        fixed_content = ''
        last_end = 0
        
        for match in strings:
            start, end = match.span()
            fixed_content += content[last_end:start]
            
            string_content = content[start:end]
            original_string = string_content
            
            # Handle escaped quotes in JSON strings
            if '\\\"' in string_content:
                # The escaped backslash should be a single backslash (JSON already escapes it)
                string_content = string_content.replace('\\\"', '\\"')
                fixes_applied.append("Fixed incorrectly escaped quotes")
            
            # Fix unescaped quotes
            if re.search(r'(?<!\\)"(?!$)', string_content[1:-1]):
                string_content = re.sub(r'(?<!\\)"(?!$)', '\\"', string_content[1:-1])
                string_content = f'"{string_content}"'
                fixes_applied.append("Escaped quotes within strings")
            
            # Escape newlines
            if '\n' in string_content or '\r' in string_content:
                # Remove the surrounding quotes first
                inner_content = string_content[1:-1]
                inner_content = inner_content.replace('\n', '\\n').replace('\r', '\\r')
                string_content = f'"{inner_content}"'
                fixes_applied.append("Escaped line breaks in strings")
            
            if original_string != string_content:
                fixes_applied.append("Fixed string content")
            
            fixed_content += string_content
            last_end = end
        
        # Add the remaining content
        fixed_content += content[last_end:]
        content = fixed_content
        
        # Step 5: Fix missing colons in property definitions
        # Find all potential property definitions missing colons
        content = re.sub(r'("(?:[^"\\]|\\.)*")\s+("(?:[^"\\]|\\.)*"|[\d.]+|true|false|null|{|\[)', r'\1:\2', content)
        fixes_applied.append("Added missing colons between properties and values")
        
        # Step 6: Fix comma issues
        # Comprehensive comma fixing - multiple passes may be needed
        original_content = None
        while original_content != content:
            original_content = content
            
            # Fix missing commas between elements
            content = re.sub(r'}\s*{', '},{', content)  # Between objects
            content = re.sub(r'}\s*\[', '},\[', content)  # Between object and array
            content = re.sub(r']\s*{', '],[{', content)  # Between array and object
            content = re.sub(r']\s*\[', '],\[', content)  # Between arrays
            
            # Fix missing commas between array elements of different types
            content = re.sub(r'(\d+|true|false|null)\s*"', r'\1,"', content)  # Between value and string
            content = re.sub(r'"(?:[^"\\]|\\.)*"\s*(\d+|true|false|null)', r'",\1', content)  # Between string and value
            
            if original_content != content:
                fixes_applied.append("Added missing commas between elements")
        
        # Step 7: Remove trailing commas
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        fixes_applied.append("Removed trailing commas if any")
        
        # Log fixes
        if self.logger and fixes_applied:
            self.logger.info("Applied fixes:")
            for fix in fixes_applied:
                self.logger.info(f"- {fix}")
        
        return content

    def _get_error_context(self, content: str, line_no: int, col_no: int, context_lines: int = 3) -> str:
        """Get context around an error location."""
        lines = content.split('\n')
        start_line = max(0, line_no - context_lines - 1)
        end_line = min(len(lines), line_no + context_lines)
        
        context = []
        for i in range(start_line, end_line):
            line_marker = '-> ' if i == line_no - 1 else '   '
            context.append(f"{line_marker}{i + 1:4d} | {lines[i]}")
            if i == line_no - 1:
                # Add pointer to specific column
                context.append('     ' + ' ' * (col_no - 1) + '^')
        
        return '\n'.join(context)
    
    def _backup_file(self, file_path: str, content: str) -> None:
        """Create a backup of the original file."""
        backup_path = f"{file_path}.backup"
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            if self.logger:
                self.logger.info(f"Original file backed up to: {backup_path}")
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to create backup file: {str(e)}")
    
    def validate_and_fix_file(self, file_path: str, auto_fix: bool = True) -> Tuple[bool, Optional[str], str]:
        """
        Validate a JSON file and fix common issues if requested.
        
        Args:
            file_path (str): Path to the JSON file
            auto_fix (bool): Whether to attempt fixing issues
            
        Returns:
            Tuple[bool, Optional[str], str]: (is_valid, error_message, content)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # First try validation
            try:
                json.loads(content)
                is_valid = True
                error_message = None
            except json.JSONDecodeError as e:
                is_valid = False
                error_message = str(e)
                
                if self.logger:
                    self.logger.error(f"JSON validation failed: {error_message}")
            
            # print(f"not is_valid: {not is_valid}\nauto_fix: {auto_fix}\n")
            # if not is_valid and auto_fix:
            if auto_fix:
                # Try to fix the content
                fixed_content = self._fix_json_content(content)
                
                # Validate the fixed content
                try:
                    json.loads(fixed_content)
                    is_valid = True
                    error_message = None
                    
                    if self.logger:
                        self.logger.info("Successfully fixed JSON issues!")
                    
                    # Save fixed content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    
                    return True, None, fixed_content
                except json.JSONDecodeError as e:
                    is_valid = False
                    error_message = str(e)
                    
                    if self.logger:
                        self.logger.error(f"Unable to fix all JSON issues: {error_message}")
                    return False, error_message, content
            
            return is_valid, error_message, content
            
        except Exception as e:
            error_msg = f"Error processing file: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return False, error_msg, ""
    
    
    
    
    
    #  def validate_and_fix_file(self, file_path: str, auto_fix: bool = True) -> Tuple[bool, Optional[str], str]:
    #     """
    #     Validate a JSON file and fix common issues if requested.
        
    #     Args:
    #         file_path (str): Path to the JSON file
    #         auto_fix (bool): Whether to attempt fixing issues
            
    #     Returns:
    #         Tuple[bool, Optional[str], str]: (is_valid, error_message, content)
    #     """
    #     try:
    #         with open(file_path, 'r', encoding='utf-8') as f:
    #             content = f.read()

    #         # First try validation
    #         is_valid, error_message = self.validate_content(content)
            
    #         if not is_valid and auto_fix:
    #             if self.logger:
    #                 self.logger.info("Attempting to fix JSON issues...")
                
    #             # Try to fix the content
    #             fixed_content = self._fix_json_content(content)
                
    #             # Validate the fixed content
    #             is_valid, error_message = self.validate_content(fixed_content)
                
    #             if is_valid:
    #                 if self.logger:
    #                     self.logger.info("Successfully fixed JSON issues!")
                    
    #                 # Create backup of original file
    #                 # self._backup_file(file_path, content)
                    
    #                 # Save fixed content
    #                 with open(file_path, 'w', encoding='utf-8') as f:
    #                     f.write(fixed_content)
                    
    #                 return True, None, fixed_content
    #             else:
    #                 if self.logger:
    #                     self.logger.error(f"Unable to fix all JSON issues:\n{error_message}")
    #                 return False, error_message, content
            
    #         return is_valid, error_message, content
            
    #     except Exception as e:
    #         error_msg = f"Error processing file: {str(e)}"
    #         if self.logger:
    #             self.logger.error(error_msg)
    #         return False, error_msg, ""
    # def _fix_json_content(self, content: str) -> str:
        # """
        # Fix common JSON issues in content.
        
        # Args:
        #     content (str): Original JSON content
            
        # Returns:
        #     str: Fixed JSON content
        # """
        # if self.logger:
        #     self.logger.info("Attempting to fix JSON issues...")
        
        # fixes_applied = []
        
        # # Fix unescaped line breaks in strings
        # pattern = r'(?<=")([^"]*?)(?=")'
        # if re.search(pattern, content):
        #     content = re.sub(pattern,
        #                    lambda m: m.group(1).replace('\n', '\\n').replace('\r', '\\r'),
        #                    content)
        #     fixes_applied.append("Escaped line breaks in strings")
        
        # # Remove JavaScript-style comments
        # if '//' in content or '/*' in content:
        #     # Single-line comments
        #     content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        #     # Multi-line comments
        #     content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        #     fixes_applied.append("Removed JavaScript-style comments")
        
        # # Fix missing commas between elements
        # if re.search(r'[}\]]["{\[]', content):
        #     content = re.sub(r'}\s*{', '},{', content)  # Between objects
        #     content = re.sub(r']\s*{', '],[', content)  # Between arrays and objects
        #     content = re.sub(r'}\s*\[', '},\[', content)  # Between objects and arrays
        #     fixes_applied.append("Added missing commas between elements")
        
        # # Remove trailing commas
        # if re.search(r',(\s*[}\]])', content):
        #     content = re.sub(r',(\s*[}\]])', r'\1', content)
        #     fixes_applied.append("Removed trailing commas")
        
        # if self.logger and fixes_applied:
        #     self.logger.info("Applied fixes:")
        #     for fix in fixes_applied:
        #         self.logger.info(f"- {fix}")
        
        # return content
    
    # def validate_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
    #     """
    #     Validate a JSON file and identify common issues.
        
    #     Args:
    #         file_path (str): Path to the JSON file
            
    #     Returns:
    #         Tuple[bool, Optional[str]]: (is_valid, error_message)
    #     """
    #     try:
    #         self.logger.info(f"Reading from: {file_path}")
    #         with open(file_path, 'r', encoding='utf-8') as f:
    #             content = f.read()
    #             return self.validate_content(content)
    #         self.logger.debug(f"Loaded file {file_path}")
    #     except FileNotFoundError:
    #         self.logger.error(f"Input file '{file_path}' not found")
    #         return False, f"File not found: {file_path}"
    #     except Exception as e:
    #         self.logger.error(f"Error reading file: {str(e)}")
    #         return False, f"Error reading file: {str(e)}"

    # def validate_content(self, content: str) -> Tuple[bool, Optional[str]]:
    #     """
    #     Validate JSON content and identify specific issues.
        
    #     Args:
    #         content (str): JSON content to validate
            
    #     Returns:
    #         Tuple[bool, Optional[str]]: (is_valid, error_message)
    #     """
    #     # Check for common issues before parsing
    #     issues = self._check_common_issues(content)
    #     if issues:
    #         return False, issues

    #     # Try to parse JSON
    #     try:
    #         json.loads(content)
    #         return True, None
    #     except json.JSONDecodeError as e:
    #         # Get context around the error
    #         context = self._get_error_context(content, e.lineno, e.colno)
    #         self.logger.error(
    #             f"JSON Decode Error: {str(e)}\n"
    #             f"Line {e.lineno}, Column {e.colno}\n"
    #             f"Context:\n{context}"
    #         )
    #         return False, (
    #             f"JSON Decode Error: {str(e)}\n"
    #             f"Line {e.lineno}, Column {e.colno}\n"
    #             f"Context:\n{context}"
    #         )

    # def _check_common_issues(self, content: str) -> Optional[str]:
    #     """Check for common JSON formatting issues."""
    #     issues = []
        
    #     # Check for unescaped quotes within strings
    #     quote_matches = re.finditer(r'"(?:[^"\\]|\\.)*"', content)
    #     for match in quote_matches:
    #         string_content = match.group(0)[1:-1]  # Remove outer quotes
    #         if '"' in string_content and '\\"' not in string_content:
    #             line_no = content[:match.start()].count('\n') + 1
    #             issues.append(f"Unescaped quote found in string at line {line_no}")

    #     # Check for unescaped line breaks in strings
    #     if re.search(r'"[^"]*[\n\r][^"]*"', content):
    #         issues.append("Unescaped line breaks found in strings")

    #     # Check for trailing commas
    #     if re.search(r',\s*[}\]]', content):
    #         issues.append("Trailing commas found")

    #     # Check for JavaScript-style comments
    #     if re.search(r'//|/\*|\*/', content):
    #         issues.append("JavaScript-style comments found")

    #     # Check for missing commas between elements
    #     if re.search(r'[}\]"]["{\[]', content):
    #         issues.append("Missing commas between elements")

    #     return "\n".join(issues) if issues else None

    # def _get_error_context(self, content: str, line_no: int, col_no: int, context_lines: int = 3) -> str:
    #     """Get context around an error location."""
    #     lines = content.split('\n')
    #     start_line = max(0, line_no - context_lines - 1)
    #     end_line = min(len(lines), line_no + context_lines)
        
    #     context = []
    #     for i in range(start_line, end_line):
    #         line_marker = '-> ' if i == line_no - 1 else '   '
    #         context.append(f"{line_marker}{i + 1:4d} | {lines[i]}")
    #         if i == line_no - 1:
    #             # Add pointer to specific column
    #             context.append('     ' + ' ' * (col_no - 1) + '^')
        
    #     return '\n'.join(context)

    # def fix_common_issues(self, content: str) -> str:
    #     """
    #     Attempt to fix common JSON formatting issues.
        
    #     Args:
    #         content (str): Original JSON content
            
    #     Returns:
    #         str: Fixed JSON content
    #     """
    #     # Escape quotes within strings
    #     content = re.sub(r'(?<!\\)"(?!,|\s*[}\]])', '\\"', content)
        
    #     # Escape line breaks
    #     content = content.replace('\n', '\\n').replace('\r', '\\r')
        
    #     # Remove trailing commas
    #     content = re.sub(r',(\s*[}\]])', r'\1', content)
        
    #     # Remove comments
    #     content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    #     content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
    #     return content