"""
Course evaluation analyzer for the AI thesis analysis.
"""

from collections import defaultdict
from typing import Dict, List, Any, Optional

from src.utils import get_logger

logger = get_logger("course_eval_analyzer")


class CourseEvaluationAnalyzer:
    """Analyzes course evaluation data."""
    
    def __init__(self, evaluations: List[Dict[str, Any]]):
        """
        Initialize the course evaluation analyzer.
        
        Args:
            evaluations: List of processed evaluation records
        """
        self.evaluations = evaluations
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive evaluation analysis.
        
        Returns:
            Dictionary of analysis results
        """
        logger.info("Performing course evaluation analysis")
        
        results = {
            'semester_comparison': self._analyze_semester_comparison(),
            'tool_impact': self._analyze_tool_impact(),
            'section_analysis': self._analyze_section_performance(),
            'question_analysis': self._analyze_key_questions(),
            'trend_analysis': self._analyze_rating_trends()
        }
        
        return results
    
    def _analyze_semester_comparison(self) -> Dict[str, Any]:
        """
        Compare evaluations across different semesters.
        
        Returns:
            Dictionary of semester comparison results
        """
        logger.info("Analyzing semester comparison")
        
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
                    'overall_metrics': eval_data.get('overall_metrics', {}),
                    'tool_version': eval_data.get('tool_version')
                }
        
        # Sort semesters chronologically
        sorted_semesters = sorted(semester_codes)
        
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
        logger.info("Analyzing tool impact")
        
        # Group evaluations by tool version
        version_data = defaultdict(list)
        
        for eval_data in self.evaluations:
            tool_version = eval_data.get('tool_version')
            if tool_version is None:
                tool_version = 'none'  # Standardize None values
                
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
        versions = ['none', 'v1', 'v2']  # Expected version progression
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
        logger.info("Analyzing section performance")
        
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
        logger.info("Analyzing key questions")
        
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
        logger.info("Analyzing rating trends")
        
        # Sort evaluations chronologically
        sorted_evals = sorted(
            self.evaluations,
            key=lambda x: x.get('semester', {}).get('code', '')
        )
        
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
                term_trend = self._calculate_trend([e.get('overall_avg') for e in term_evals])
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
    
    @staticmethod
    def _calculate_trend(values: List[float]) -> Dict[str, Any]:
        """
        Calculate a simple linear trend from a series of values.
        
        Args:
            values: List of numerical values
            
        Returns:
            Dictionary with trend metrics
        """
        if not values or len(values) < 2:
            return {
                'direction': 'unknown',
                'slope': None,
                'consistent': None
            }
        
        # Calculate simple slope between first and last value
        first = values[0]
        last = values[-1]
        total_change = last - first
        
        # Determine direction
        if total_change > 0:
            direction = 'increasing'
        elif total_change < 0:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        # Check if trend is consistent or fluctuating
        increasing_segments = 0
        decreasing_segments = 0
        
        for i in range(1, len(values)):
            diff = values[i] - values[i-1]
            if diff > 0:
                increasing_segments += 1
            elif diff < 0:
                decreasing_segments += 1
        
        # Calculate consistency
        total_segments = len(values) - 1
        if direction == 'increasing':
            consistency = increasing_segments / total_segments
        elif direction == 'decreasing':
            consistency = decreasing_segments / total_segments
        else:
            consistency = 1.0
        
        return {
            'direction': direction,
            'slope': total_change / (len(values) - 1),
            'consistent': consistency > 0.5,
            'consistency': consistency
        }