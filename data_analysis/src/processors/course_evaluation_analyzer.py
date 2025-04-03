"""
Course evaluation analyzer for data analysis.
"""

from collections import defaultdict
from typing import Dict, List, Any

from src.processors.base_analyzer import BaseAnalyzer
from src.utils import StatsUtils


class CourseEvaluationAnalyzer(BaseAnalyzer):
    """Analyzes course evaluation data."""
    
    def __init__(self, evaluations: List[Dict[str, Any]]):
        """
        Initialize the course evaluation analyzer.
        
        Args:
            evaluations: List of processed evaluation records
        """
        super().__init__("course_eval_analyzer")
        self.evaluations = evaluations
    
    def validate_data(self) -> None:
        """Validate input evaluation data."""
        if not self.evaluations:
            self.logger.warning("No evaluation data provided")
            return
        
        # Check that evaluations have required fields
        for eval_data in self.evaluations:
            if 'semester' not in eval_data:
                self.logger.warning("Evaluation missing 'semester' field")
            if 'evaluation_metrics' not in eval_data:
                self.logger.warning("Evaluation missing 'evaluation_metrics' field")
    
    def perform_analysis(self) -> Dict[str, Any]:
        """
        Perform comprehensive evaluation analysis.
        
        Returns:
            Dictionary of analysis results
        """
        self.logger.info("Performing course evaluation analysis")
        
        results = {
            'semester_comparison': self._analyze_semester_comparison(),
            'tool_impact': self._analyze_tool_impact(),
            'section_analysis': self._analyze_section_performance(),
            'question_analysis': self._analyze_key_questions(),
            'trend_analysis': self._analyze_rating_trends(),
            'time_spent_analysis': self._analyze_time_spent(),
            'overall_rating_analysis': self._analyze_overall_rating()
        }
        
        return results
    
    def _analyze_semester_comparison(self) -> Dict[str, Any]:
        """
        Compare evaluations across different semesters.
        
        Returns:
            Dictionary of semester comparison results
        """
        self.logger.info("Analyzing semester comparison")
        
        # Group evaluations by semester
        semester_data = {}
        semester_codes = []
        
        for eval_data in self.evaluations:
            semester = eval_data.get('semester', {})
            code = semester.get('code')
            
            if code:
                semester_codes.append(code)
                semester_data[code] = {
                    'display_name': semester.get('display_name'),
                    'term': semester.get('term'),
                    'year': semester.get('year'),
                    'order': semester.get('order', 0), 
                    'overall_metrics': eval_data.get('overall_metrics', {}),
                    'tool_version': eval_data.get('tool_version')
                }
        
        # Sort semesters by year and then by order (Spring then Fall)
        # First, create a list of tuples (code, year, order) for sorting
        semester_sort_data = [(code, semester_data[code]['year'], semester_data[code].get('order', 0)) 
                            for code in semester_codes]
        
        # Sort by year (ascending) and then by order (ascending, with Spring before Fall)
        sorted_semester_data = sorted(semester_sort_data, key=lambda x: (x[1], x[2]))
        
        # Extract just the sorted semester codes
        sorted_semesters = [code for code, _, _ in sorted_semester_data]
        
        # Extract metrics for comparison
        comparison = {
            'semesters': sorted_semesters,
            'display_names': [semester_data[code]['display_name'] for code in sorted_semesters],
            'overall_avg': [semester_data[code]['overall_metrics'].get('overall_avg') for code in sorted_semesters],
            'tool_versions': [semester_data[code].get('tool_version') for code in sorted_semesters],
            'term_comparisons': self._compare_terms(semester_data)
        }
        
        return comparison
    
    def _analyze_tool_impact(self) -> Dict[str, Any]:
        """
        Analyze the impact of different tool versions on evaluations.
        
        Returns:
            Dictionary of tool impact analysis results
        """
        self.logger.info("Analyzing tool impact")
        
        # Group evaluations by tool version
        version_data = defaultdict(list)
        
        for eval_data in self.evaluations:
            tool_version = eval_data.get('tool_version')
                
            version_data[tool_version].append({
                'semester': eval_data.get('semester', {}),
                'overall_metrics': eval_data.get('overall_metrics', {})
            })
        
        # Calculate metrics by tool version
        version_metrics = {}
        
        for version, evals in version_data.items():
            avg_scores = [e['overall_metrics'].get('overall_avg') for e in evals 
                         if e['overall_metrics'].get('overall_avg') is not None]
            
            if avg_scores:
                version_metrics[version] = {
                    'avg_score': sum(avg_scores) / len(avg_scores),
                    'num_semesters': len(evals),
                    'semesters': [e['semester'].get('display_name') for e in evals]
                }
        
        # Compare sequential versions to identify improvements
        versions = ['v1', 'v2']  # Expected version progression
        version_improvements = []
        
        for i in range(1, len(versions)):
            prev_version = versions[i-1]
            curr_version = versions[i]
            
            if prev_version in version_metrics and curr_version in version_metrics:
                prev_score = version_metrics[prev_version]['avg_score']
                curr_score = version_metrics[curr_version]['avg_score']
                
                version_improvements.append({
                    'from_version': prev_version,
                    'to_version': curr_version,
                    'score_change': curr_score - prev_score,
                    'percent_change': (curr_score - prev_score) / prev_score * 100 if prev_score else None
                })
        
        # Separate fall/spring semesters for each version to control for seasonal effects
        seasonal_impact = {}
        
        for version, evals in version_data.items():
            fall_evals = [e for e in evals if e['semester'].get('term') == 'fall']
            spring_evals = [e for e in evals if e['semester'].get('term') == 'spring']
            
            fall_scores = [e['overall_metrics'].get('overall_avg') for e in fall_evals 
                          if e['overall_metrics'].get('overall_avg') is not None]
            
            spring_scores = [e['overall_metrics'].get('overall_avg') for e in spring_evals 
                            if e['overall_metrics'].get('overall_avg') is not None]
            
            seasonal_impact[version] = {
                'fall_avg': sum(fall_scores) / len(fall_scores) if fall_scores else None,
                'spring_avg': sum(spring_scores) / len(spring_scores) if spring_scores else None,
                'fall_semesters': len(fall_scores),
                'spring_semesters': len(spring_scores)
            }
        
        return {
            'version_metrics': version_metrics,
            'version_improvements': version_improvements,
            'seasonal_impact': seasonal_impact
        }
    
    def _analyze_section_performance(self) -> Dict[str, Any]:
        """
        Analyze performance across different evaluation sections.
        
        Returns:
            Dictionary of section analysis results
        """
        self.logger.info("Analyzing section performance")
        
        # Collect all section names
        all_sections = set()
        for eval_data in self.evaluations:
            metrics = eval_data.get('evaluation_metrics', [])
            for section in metrics:
                section_name = section.get('section')
                if section_name:
                    all_sections.add(section_name)
        
        # Track section averages by semester
        section_by_semester = {}
        
        for eval_data in self.evaluations:
            semester = eval_data.get('semester', {})
            semester_code = semester.get('code')
            
            if not semester_code:
                continue
                
            section_averages = {}
            
            for section in eval_data.get('evaluation_metrics', []):
                section_name = section.get('section')
                if not section_name:
                    continue
                    
                questions = section.get('questions', [])
                valid_scores = [q.get('avg') for q in questions if q.get('avg') is not None]
                
                if valid_scores:
                    section_averages[section_name] = sum(valid_scores) / len(valid_scores)
            
            if section_averages:
                section_by_semester[semester_code] = {
                    'display_name': semester.get('display_name'),
                    'tool_version': eval_data.get('tool_version'),
                    'section_averages': section_averages
                }
        
        # Organize data for comparison
        section_comparison = {
            'sections': sorted(all_sections),
            'by_semester': section_by_semester
        }
        
        return section_comparison
    
    def _analyze_key_questions(self) -> Dict[str, Any]:
        """
        Analyze responses to key questions across semesters.
        
        Returns:
            Dictionary of question analysis results
        """
        self.logger.info("Analyzing key questions")
        
        # Define key questions to track
        key_questions = {
            'overall_satisfaction': [
                'Overall, this subject was worthwhile',
                'I found the subject worthwhile',
                'The subject was worthwhile'
            ],
            'learning_experience': [
                'My learning experience was enhanced by the teaching team',
                'I learned a lot from this subject',
                'This subject helped me learn',
                'The subject enhanced my educational experience'
            ],
            'feedback_quality': [
                'I received helpful feedback on my work',
                'Feedback on coursework was useful',
                'The feedback on my work was helpful'
            ],
            'materials_quality': [
                'The instructional materials supported my learning',
                'Subject materials were helpful',
                'The materials supported my learning'
            ]
        }
        
        # Track question responses by semester
        question_data = {}
        
        for category, possible_questions in key_questions.items():
            question_data[category] = {'semesters': {}}
            
            for eval_data in self.evaluations:
                semester = eval_data.get('semester', {})
                semester_code = semester.get('code')
                
                if not semester_code:
                    continue
                
                # Look for matching questions
                found_scores = []
                found_questions = []
                
                for section in eval_data.get('evaluation_metrics', []):
                    for question in section.get('questions', []):
                        question_text = question.get('question', '')
                        
                        if any(possible_q.lower() in question_text.lower() for possible_q in possible_questions):
                            avg_score = question.get('avg')
                            if avg_score is not None:
                                found_scores.append(avg_score)
                                found_questions.append(question_text)
                
                if found_scores:
                    avg_score = sum(found_scores) / len(found_scores)
                    question_data[category]['semesters'][semester_code] = {
                        'display_name': semester.get('display_name'),
                        'tool_version': eval_data.get('tool_version'),
                        'avg_score': avg_score,
                        'matching_questions': found_questions
                    }
        
        return question_data
    
    def _analyze_rating_trends(self) -> Dict[str, Any]:
        """
        Analyze rating trends over time.
        
        Returns:
            Dictionary of trend analysis results
        """
        self.logger.info("Analyzing rating trends")
        
        # Sort evaluations chronologically, respecting the specified order
        def sort_key(eval_data):
            semester = eval_data.get('semester', {})
            year = semester.get('year', 0)
            # Use the order field if present, otherwise infer from term
            if 'order' in semester:
                order = semester['order']
            else:
                order = 1 if semester.get('term', '').lower() == 'spring' else 2
            return (year, order)
        
        sorted_evals = sorted(self.evaluations, key=sort_key)
        
        # Extract overall averages
        timeline = []
        for eval_data in sorted_evals:
            semester = eval_data.get('semester', {})
            overall_metrics = eval_data.get('overall_metrics', {})
            
            timeline.append({
                'semester_code': semester.get('code'),
                'display_name': semester.get('display_name'),
                'term': semester.get('term'),
                'year': semester.get('year'),
                'order': semester.get('order', 0),
                'tool_version': eval_data.get('tool_version'),
                'overall_avg': overall_metrics.get('overall_avg')
            })
        
        # Calculate semester-to-semester changes
        changes = []
        for i in range(1, len(timeline)):
            prev = timeline[i-1]
            curr = timeline[i]
            
            if prev.get('overall_avg') is not None and curr.get('overall_avg') is not None:
                change = curr['overall_avg'] - prev['overall_avg']
                pct_change = change / prev['overall_avg'] * 100 if prev['overall_avg'] else None
                
                changes.append({
                    'from_semester': prev['display_name'],
                    'to_semester': curr['display_name'],
                    'change': change,
                    'percent_change': pct_change,
                    'tool_change': prev['tool_version'] != curr['tool_version'],
                    'from_tool': prev['tool_version'],
                    'to_tool': curr['tool_version']
                })
        
        # Calculate term-specific trends
        term_trends = {}
        for term in ['fall', 'spring']:
            term_evals = [e for e in timeline if e.get('term') == term]
            if len(term_evals) >= 2:
                term_trend = StatsUtils.calculate_trend([e.get('overall_avg') for e in term_evals])
                term_trends[term] = {
                    'evals': len(term_evals),
                    'trend': term_trend,
                    'years': [e.get('year') for e in term_evals]
                }
        
        return {
            'timeline': timeline,
            'changes': changes,
            'term_trends': term_trends
        }
    
    def _analyze_time_spent(self) -> Dict[str, Any]:
        """
        Analyze time spent on the course across semesters.
        
        Returns:
            Dictionary of time spent analysis results
        """
        self.logger.info("Analyzing time spent")
        
        # Track time spent by semester
        time_data = {
            'by_semester': {},
            'by_tool_version': defaultdict(list),
            'timeline': []
        }
        
        # Sort evaluations chronologically
        sorted_evals = sorted(
            self.evaluations,
            key=self._semester_sort_key
        )
        
        for eval_data in sorted_evals:
            semester = eval_data.get('semester', {})
            semester_code = semester.get('code')
            tool_version = eval_data.get('tool_version')
            
            if tool_version is None:
                tool_version = 'none'
            
            if not semester_code:
                continue
            
            # Initialize data structure for this semester
            if semester_code not in time_data['by_semester']:
                time_data['by_semester'][semester_code] = {
                    'display_name': semester.get('display_name'),
                    'tool_version': tool_version,
                    'term': semester.get('term'),
                    'year': semester.get('year'),
                    'time_questions': []
                }
            
            # Look specifically for "Time Spent" section
            for section in eval_data.get('evaluation_metrics', []):
                section_name = section.get('section', '')
                
                if section_name == "Time Spent":
                    self.logger.info(f"Found 'Time Spent' section for semester {semester_code}")
                    
                    # Process questions in this section
                    for question in section.get('questions', []):
                        question_text = question.get('question', '')
                        avg_value = question.get('avg')
                        
                        if avg_value is not None:
                            # Extract information about classroom vs outside time
                            is_outside_classroom = "outside" in question_text.lower()
                            
                            # Store in semester data
                            time_data['by_semester'][semester_code]['time_questions'].append({
                                'question': question_text,
                                'value': avg_value,
                                'section': section_name,
                                'outside_classroom': is_outside_classroom
                            })
                            
                            # Add to tool version data
                            time_data['by_tool_version'][tool_version].append(avg_value)
                            
                            # Add to timeline
                            time_data['timeline'].append({
                                'semester_code': semester_code,
                                'display_name': semester_data.get('display_name'),
                                'tool_version': tool_version,
                                'term': semester_data.get('term'),
                                'year': semester_data.get('year'),
                                'time_value': avg_value,
                                'question': question_text,
                                'outside_classroom': is_outside_classroom
                            })
        
        # Calculate total time spent (classroom + outside) for each semester
        for semester_code, semester_data in time_data['by_semester'].items():
            time_questions = semester_data.get('time_questions', [])
            
            classroom_time = 0
            outside_time = 0
            
            for question in time_questions:
                if question.get('outside_classroom'):
                    outside_time = question.get('value', 0)
                else:
                    classroom_time = question.get('value', 0)
            
            total_time = classroom_time + outside_time
            
            # Add total time to semester data
            time_data['by_semester'][semester_code]['classroom_time'] = classroom_time
            time_data['by_semester'][semester_code]['outside_time'] = outside_time
            time_data['by_semester'][semester_code]['total_time'] = total_time
            
            # Add total time to timeline
            time_data['timeline'].append({
                'semester_code': semester_code,
                'display_name': semester_data.get('display_name'),
                'tool_version': semester_data.get('tool_version'),
                'term': semester_data.get('term'),
                'year': semester_data.get('year'),
                'time_value': total_time,
                'question': 'Total time spent (in and outside classroom)',
                'is_total': True
            })
        
        # Filter timeline to keep only total time entries for cleaner visualization
        time_data['total_time_timeline'] = [
            entry for entry in time_data['timeline'] 
            if entry.get('is_total', False)
        ]
        
        # Calculate average time spent by tool version (using total time)
        time_data['avg_by_tool_version'] = {}
        tool_version_totals = defaultdict(list)
        
        # Collect total times by tool version
        for semester_code, semester_data in time_data['by_semester'].items():
            tool_version = semester_data.get('tool_version')
            total_time = semester_data.get('total_time')
            
            if tool_version and total_time is not None:
                tool_version_totals[tool_version].append(total_time)
        
        # Calculate averages
        for version, values in tool_version_totals.items():
            if values:
                time_data['avg_by_tool_version'][version] = {
                    'avg_time': sum(values) / len(values),
                    'classroom_outside_ratio': None,  # Could calculate this if needed
                    'num_data_points': len(values)
                }
        
        # Calculate semester-to-semester changes in total time
        time_data['changes'] = []
        sorted_semesters = sorted(time_data['by_semester'].keys())
        
        for i in range(1, len(sorted_semesters)):
            prev_semester = sorted_semesters[i-1]
            curr_semester = sorted_semesters[i]
            
            prev_data = time_data['by_semester'][prev_semester]
            curr_data = time_data['by_semester'][curr_semester]
            
            prev_time = prev_data.get('total_time', 0)
            curr_time = curr_data.get('total_time', 0)
            
            change = curr_time - prev_time
            pct_change = change / prev_time * 100 if prev_time else None
            
            time_data['changes'].append({
                'from_semester': prev_data.get('display_name'),
                'to_semester': curr_data.get('display_name'),
                'change': change,
                'percent_change': pct_change,
                'tool_change': prev_data.get('tool_version') != curr_data.get('tool_version'),
                'from_tool': prev_data.get('tool_version'),
                'to_tool': curr_data.get('tool_version')
            })
        
        # Calculate time spent trend for total time
        if len(sorted_semesters) >= 2:
            total_times = [time_data['by_semester'][s].get('total_time', 0) for s in sorted_semesters]
            time_data['trend'] = StatsUtils.calculate_trend(total_times)
        
        # Add log for debugging
        self.logger.info(f"Time spent analysis found {len(time_data['timeline'])} data points")
        if not time_data['timeline']:
            self.logger.warning("No time spent data found in evaluations")
        
        return time_data
    
    def _analyze_overall_rating(self) -> Dict[str, Any]:
        """
        Perform detailed analysis of overall course ratings over time.
        
        Returns:
            Dictionary of overall rating analysis results
        """
        self.logger.info("Analyzing detailed overall ratings")
        
        # Define overall rating questions to look for
        overall_questions = [
            'Overall, this subject was', 
            'Overall rating',
            'Overall evaluation',
            'Overall satisfaction',
            'Overall quality'
        ]
        
        # Track ratings by semester and tool version
        rating_data = {
            'by_semester': {},
            'by_tool_version': defaultdict(list),
            'timeline': [],
            'correlation_with_time': {}
        }
        
        # Sort evaluations chronologically
        sorted_evals = sorted(
            self.evaluations,
            key=self._semester_sort_key
        )
        
        # First pass: collect overall ratings
        for eval_data in sorted_evals:
            semester = eval_data.get('semester', {})
            semester_code = semester.get('code')
            tool_version = eval_data.get('tool_version')
            
            if tool_version is None:
                tool_version = 'none'
            
            if not semester_code:
                continue
                
            # Initialize semester data
            if semester_code not in rating_data['by_semester']:
                rating_data['by_semester'][semester_code] = {
                    'display_name': semester.get('display_name'),
                    'tool_version': tool_version,
                    'term': semester.get('term'),
                    'year': semester.get('year'),
                    'rating_questions': []
                }
            
            # Look for overall rating questions
            overall_scores = []
            found_questions = []
            
            for section in eval_data.get('evaluation_metrics', []):
                for question in section.get('questions', []):
                    question_text = question.get('question', '')
                    
                    # Check if this is an overall rating question
                    if any(overall_phrase in question_text for overall_phrase in overall_questions):
                        avg_score = question.get('avg')
                        if avg_score is not None:
                            overall_scores.append(avg_score)
                            found_questions.append(question_text)
                            
                            # Add to rating questions list
                            rating_data['by_semester'][semester_code]['rating_questions'].append({
                                'question': question_text,
                                'value': avg_score,
                                'section': section.get('section')
                            })
            
            # Calculate average overall rating
            if overall_scores:
                avg_rating = sum(overall_scores) / len(overall_scores)
                
                # Add to semester data
                rating_data['by_semester'][semester_code]['avg_rating'] = avg_rating
                rating_data['by_semester'][semester_code]['num_questions'] = len(overall_scores)
                
                # Add to tool version data
                rating_data['by_tool_version'][tool_version].append(avg_rating)
                
                # Add to timeline
                rating_data['timeline'].append({
                    'semester_code': semester_code,
                    'display_name': semester.get('display_name'),
                    'tool_version': tool_version,
                    'term': semester.get('term'),
                    'year': semester.get('year'),
                    'avg_rating': avg_rating,
                    'questions': found_questions
                })
        
        # Calculate average rating by tool version
        rating_data['avg_by_tool_version'] = {}
        for version, values in rating_data['by_tool_version'].items():
            if values:
                rating_data['avg_by_tool_version'][version] = {
                    'avg_rating': sum(values) / len(values),
                    'num_semesters': len(values)
                }
        
        # Calculate rating changes between tool versions
        versions = ['none', 'v1', 'v2']  # Expected version progression
        version_changes = []
        
        for i in range(1, len(versions)):
            prev_version = versions[i-1]
            curr_version = versions[i]
            
            if (prev_version in rating_data['avg_by_tool_version'] and 
                curr_version in rating_data['avg_by_tool_version']):
                
                prev_rating = rating_data['avg_by_tool_version'][prev_version]['avg_rating']
                curr_rating = rating_data['avg_by_tool_version'][curr_version]['avg_rating']
                
                version_changes.append({
                    'from_version': prev_version,
                    'to_version': curr_version,
                    'change': curr_rating - prev_rating,
                    'percent_change': (curr_rating - prev_rating) / prev_rating * 100 if prev_rating else None
                })
        
        rating_data['version_changes'] = version_changes
        
        # Calculate semester-to-semester changes
        rating_data['changes'] = []
        sorted_timeline = sorted(rating_data['timeline'], key=lambda x: x['semester_code'])
        
        for i in range(1, len(sorted_timeline)):
            prev = sorted_timeline[i-1]
            curr = sorted_timeline[i]
            
            change = curr['avg_rating'] - prev['avg_rating']
            pct_change = change / prev['avg_rating'] * 100 if prev['avg_rating'] else None
            
            rating_data['changes'].append({
                'from_semester': prev['display_name'],
                'to_semester': curr['display_name'],
                'change': change,
                'percent_change': pct_change,
                'tool_change': prev['tool_version'] != curr['tool_version'],
                'from_tool': prev['tool_version'],
                'to_tool': curr['tool_version']
            })
        
        # Calculate overall rating trend
        if len(rating_data['timeline']) >= 2:
            rating_values = [entry['avg_rating'] for entry in sorted_timeline]
            rating_data['trend'] = StatsUtils.calculate_trend(rating_values)
        
        # Attempt to calculate correlation between time spent and overall rating
        # This requires us to have both time spent and overall rating data for the same semesters
        time_data = self._analyze_time_spent()
        time_by_semester = {}
        
        for entry in time_data.get('timeline', []):
            semester_code = entry.get('semester_code')
            if semester_code and entry.get('is_total', False):
                time_by_semester[semester_code] = entry.get('time_value')
        
        # Collect paired data points (time spent and rating from same semester)
        paired_data = []
        for entry in rating_data['timeline']:
            semester_code = entry.get('semester_code')
            if semester_code in time_by_semester:
                paired_data.append({
                    'semester': entry.get('display_name'),
                    'time_spent': time_by_semester[semester_code],
                    'rating': entry.get('avg_rating'),
                    'tool_version': entry.get('tool_version')
                })
        
        rating_data['correlation_with_time'] = {
            'paired_data': paired_data,
            'correlation': StatsUtils.calculate_correlation(
                [p['time_spent'] for p in paired_data], 
                [p['rating'] for p in paired_data]
            ) if paired_data else None
        }
        
        return rating_data
    
    def _compare_terms(self, semester_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare fall vs spring evaluations.
        
        Args:
            semester_data: Grouped evaluation data by semester
            
        Returns:
            Dictionary of term comparison results
        """
        # Separate fall and spring data
        fall_scores = []
        spring_scores = []
        
        for code, data in semester_data.items():
            term = data.get('term')
            overall_avg = data.get('overall_metrics', {}).get('overall_avg')
            
            if overall_avg is not None:
                if term == 'fall':
                    fall_scores.append(overall_avg)
                elif term == 'spring':
                    spring_scores.append(overall_avg)
        
        # Calculate averages
        fall_avg = sum(fall_scores) / len(fall_scores) if fall_scores else None
        spring_avg = sum(spring_scores) / len(spring_scores) if spring_scores else None
        
        # Calculate seasonal difference
        seasonal_diff = fall_avg - spring_avg if fall_avg is not None and spring_avg is not None else None
        
        return {
            'fall_avg': fall_avg,
            'spring_avg': spring_avg,
            'fall_semesters': len(fall_scores),
            'spring_semesters': len(spring_scores),
            'seasonal_difference': seasonal_diff,
            'percent_difference': (seasonal_diff / spring_avg * 100) if spring_avg and seasonal_diff is not None else None
        }
    
    def _semester_sort_key(self, eval_data):
        """Generate a sort key for semester-based sorting."""
        semester = eval_data.get('semester', {})
        year = semester.get('year', 0)
        # Use the order field if present, otherwise infer from term
        if 'order' in semester:
            order = semester['order']
        else:
            order = 1 if semester.get('term', '').lower() == 'spring' else 2
        return (year, order)