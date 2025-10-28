"""
Simple Log Analyzer for Loglytics AI
Provides basic log analysis without requiring external LLM services
"""

import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import Counter

logger = logging.getLogger(__name__)

class SimpleLogAnalyzer:
    """Simple log analyzer that provides basic insights without LLM"""
    
    def __init__(self):
        self.log_patterns = {
            'error': re.compile(r'(?i)(error|exception|failed|fatal|critical)'),
            'warning': re.compile(r'(?i)(warning|warn|caution)'),
            'info': re.compile(r'(?i)(info|information)'),
            'debug': re.compile(r'(?i)(debug|trace)'),
            'http_status': re.compile(r'HTTP/\d\.\d\s+(\d{3})'),
            'ip_address': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
            'timestamp': re.compile(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}'),
            'user_id': re.compile(r'(?i)(user[_-]?id|uid|user)\s*[:=]\s*(\w+)'),
            'session_id': re.compile(r'(?i)(session[_-]?id|sid|session)\s*[:=]\s*(\w+)'),
        }
    
    def analyze_log_content(self, content: str, filename: str) -> Dict[str, Any]:
        """Analyze log content and provide insights"""
        try:
            lines = content.split('\n')
            total_lines = len(lines)
            
            # Basic statistics
            analysis = {
                'filename': filename,
                'total_lines': total_lines,
                'total_size': len(content),
                'analysis_timestamp': datetime.now().isoformat(),
                'insights': []
            }
            
            # Count log levels
            level_counts = {'error': 0, 'warning': 0, 'info': 0, 'debug': 0}
            error_lines = []
            warning_lines = []
            http_statuses = []
            ip_addresses = set()
            timestamps = []
            
            for i, line in enumerate(lines[:1000]):  # Analyze first 1000 lines
                line_lower = line.lower()
                
                # Check log levels
                if self.log_patterns['error'].search(line):
                    level_counts['error'] += 1
                    error_lines.append(f"Line {i+1}: {line[:100]}...")
                elif self.log_patterns['warning'].search(line):
                    level_counts['warning'] += 1
                    warning_lines.append(f"Line {i+1}: {line[:100]}...")
                elif self.log_patterns['info'].search(line):
                    level_counts['info'] += 1
                elif self.log_patterns['debug'].search(line):
                    level_counts['debug'] += 1
                
                # Extract HTTP status codes
                http_match = self.log_patterns['http_status'].search(line)
                if http_match:
                    http_statuses.append(http_match.group(1))
                
                # Extract IP addresses
                ip_matches = self.log_patterns['ip_address'].findall(line)
                ip_addresses.update(ip_matches)
                
                # Extract timestamps
                timestamp_matches = self.log_patterns['timestamp'].findall(line)
                timestamps.extend(timestamp_matches)
            
            # Generate insights
            insights = []
            
            # Log level analysis
            if level_counts['error'] > 0:
                insights.append(f"🚨 **Error Analysis**: Found {level_counts['error']} error entries")
                if error_lines:
                    insights.append(f"Sample errors:\n" + "\n".join(error_lines[:3]))
            
            if level_counts['warning'] > 0:
                insights.append(f"⚠️ **Warning Analysis**: Found {level_counts['warning']} warning entries")
                if warning_lines:
                    insights.append(f"Sample warnings:\n" + "\n".join(warning_lines[:3]))
            
            # HTTP status analysis
            if http_statuses:
                status_counter = Counter(http_statuses)
                insights.append(f"🌐 **HTTP Status Analysis**:")
                for status, count in status_counter.most_common(5):
                    insights.append(f"  - {status}: {count} requests")
            
            # IP address analysis
            if ip_addresses:
                insights.append(f"🔍 **IP Address Analysis**: Found {len(ip_addresses)} unique IP addresses")
                insights.append(f"Sample IPs: {', '.join(list(ip_addresses)[:5])}")
            
            # Time analysis
            if timestamps:
                insights.append(f"⏰ **Time Analysis**: Found {len(timestamps)} timestamp entries")
                if len(timestamps) > 1:
                    insights.append(f"Time range: {timestamps[0]} to {timestamps[-1]}")
            
            # General statistics
            insights.append(f"📊 **File Statistics**:")
            insights.append(f"  - Total lines: {total_lines}")
            insights.append(f"  - File size: {len(content):,} bytes")
            insights.append(f"  - Log levels: Error({level_counts['error']}), Warning({level_counts['warning']}), Info({level_counts['info']}), Debug({level_counts['debug']})")
            
            analysis['insights'] = insights
            analysis['level_counts'] = level_counts
            analysis['http_statuses'] = dict(Counter(http_statuses))
            analysis['unique_ips'] = len(ip_addresses)
            analysis['timestamp_count'] = len(timestamps)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing log content: {e}")
            return {
                'filename': filename,
                'error': str(e),
                'insights': [f"❌ Error analyzing log file: {str(e)}"]
            }
    
    def generate_response(self, user_question: str, log_analysis: Dict[str, Any], project_name: str) -> str:
        """Generate a response based on log analysis and user question"""
        try:
            response_parts = []
            
            # Header
            response_parts.append(f"# Log Analysis Report for {project_name}")
            response_parts.append(f"**File**: {log_analysis.get('filename', 'Unknown')}")
            response_parts.append("")
            
            # Answer user's specific question
            question_lower = user_question.lower()
            
            if 'summary' in question_lower or 'overview' in question_lower:
                response_parts.append("## 📋 Summary")
                response_parts.append(f"This log file contains {log_analysis.get('total_lines', 0)} lines with the following breakdown:")
                
                level_counts = log_analysis.get('level_counts', {})
                if level_counts:
                    response_parts.append(f"- **Errors**: {level_counts.get('error', 0)}")
                    response_parts.append(f"- **Warnings**: {level_counts.get('warning', 0)}")
                    response_parts.append(f"- **Info**: {level_counts.get('info', 0)}")
                    response_parts.append(f"- **Debug**: {level_counts.get('debug', 0)}")
                
                response_parts.append("")
            
            if 'error' in question_lower:
                error_count = log_analysis.get('level_counts', {}).get('error', 0)
                if error_count > 0:
                    response_parts.append("## 🚨 Error Analysis")
                    response_parts.append(f"Found **{error_count} error entries** in the log file.")
                    response_parts.append("")
                else:
                    response_parts.append("## ✅ Error Analysis")
                    response_parts.append("No errors found in the log file.")
                    response_parts.append("")
            
            if 'pattern' in question_lower or 'anomaly' in question_lower:
                response_parts.append("## 🔍 Pattern Analysis")
                http_statuses = log_analysis.get('http_statuses', {})
                if http_statuses:
                    response_parts.append("**HTTP Status Code Distribution**:")
                    for status, count in sorted(http_statuses.items()):
                        response_parts.append(f"- {status}: {count} requests")
                    response_parts.append("")
            
            # Add insights
            insights = log_analysis.get('insights', [])
            if insights:
                response_parts.append("## 📊 Detailed Analysis")
                for insight in insights:
                    response_parts.append(insight)
                response_parts.append("")
            
            # Recommendations
            response_parts.append("## 💡 Recommendations")
            level_counts = log_analysis.get('level_counts', {})
            
            if level_counts.get('error', 0) > 10:
                response_parts.append("- **High Error Count**: Consider investigating the root cause of frequent errors")
            elif level_counts.get('error', 0) > 0:
                response_parts.append("- **Errors Detected**: Review error entries for potential issues")
            else:
                response_parts.append("- **No Errors**: Log file appears clean with no error entries")
            
            if level_counts.get('warning', 0) > 20:
                response_parts.append("- **Many Warnings**: Monitor warning patterns for potential issues")
            
            http_statuses = log_analysis.get('http_statuses', {})
            if http_statuses.get('500', 0) > 0:
                response_parts.append("- **Server Errors**: Investigate 500 status codes for server issues")
            if http_statuses.get('404', 0) > 10:
                response_parts.append("- **Not Found Errors**: High 404 count may indicate broken links or misconfigurations")
            
            response_parts.append("")
            response_parts.append("---")
            response_parts.append("*This analysis was generated by Loglytics AI's built-in log analyzer.*")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"# Log Analysis Report\n\n❌ Error generating analysis: {str(e)}\n\nPlease try again or contact support if the issue persists."

# Create singleton instance
simple_log_analyzer = SimpleLogAnalyzer()
