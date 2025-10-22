"""
Log Format Detector for Loglytics AI
Automatically detects log format from sample lines
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class LogFormat(str, Enum):
    """Supported log formats"""
    JSON = "json"
    SYSLOG = "syslog"
    APACHE_ACCESS = "apache_access"
    APACHE_ERROR = "apache_error"
    NGINX_ACCESS = "nginx_access"
    NGINX_ERROR = "nginx_error"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    AWS_CLOUDWATCH = "aws_cloudwatch"
    AZURE_MONITOR = "azure_monitor"
    GCP_CLOUD_LOGGING = "gcp_cloud_logging"
    WINDOWS_EVENT = "windows_event"
    GENERIC = "generic"

@dataclass
class FormatDetectionResult:
    """Result of format detection"""
    format: LogFormat
    confidence: float
    sample_matches: int
    total_samples: int
    metadata: Dict[str, Any]

class LogFormatDetector:
    """Detects log format from sample lines"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.min_confidence = 0.6
        self.sample_size = 100
    
    def _initialize_patterns(self) -> Dict[LogFormat, Dict[str, Any]]:
        """Initialize detection patterns for each format"""
        return {
            LogFormat.JSON: {
                "pattern": re.compile(r'^\s*\{.*\}\s*$', re.DOTALL),
                "required_fields": ["timestamp", "level", "message"],
                "optional_fields": ["service", "source", "logger"]
            },
            
            LogFormat.SYSLOG: {
                "pattern": re.compile(r'^<(\d+)>(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+(\S+)\s+(.+)$'),
                "priority_levels": range(0, 24),
                "timestamp_formats": ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S.%fZ"]
            },
            
            LogFormat.APACHE_ACCESS: {
                "pattern": re.compile(r'^(\d+\.\d+\.\d+\.\d+)\s+-\s+-\s+\[([^\]]+)\]\s+"([^"]+)"\s+(\d+)\s+(\d+)(?:\s+"([^"]+)"\s+"([^"]+)")?'),
                "status_codes": range(100, 600),
                "timestamp_format": "%d/%b/%Y:%H:%M:%S %z"
            },
            
            LogFormat.APACHE_ERROR: {
                "pattern": re.compile(r'^\[([^\]]+)\]\s+\[([^\]]+)\]\s+\[([^\]]+)\]\s+(.+)$'),
                "log_levels": ["emerg", "alert", "crit", "error", "warn", "notice", "info", "debug"]
            },
            
            LogFormat.NGINX_ACCESS: {
                "pattern": re.compile(r'^(\d+\.\d+\.\d+\.\d+)\s+-\s+-\s+\[([^\]]+)\]\s+"([^"]+)"\s+(\d+)\s+(\d+)\s+"([^"]+)"\s+"([^"]+)"\s+"([^"]+)"'),
                "status_codes": range(100, 600),
                "timestamp_format": "%d/%b/%Y:%H:%M:%S %z"
            },
            
            LogFormat.NGINX_ERROR: {
                "pattern": re.compile(r'^(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})\s+\[([^\]]+)\]\s+(\d+)#(\d+):\s+(.+)$'),
                "log_levels": ["emerg", "alert", "crit", "error", "warn", "notice", "info", "debug"]
            },
            
            LogFormat.DOCKER: {
                "pattern": re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+(\S+)\s+(.+)$'),
                "container_indicators": ["container", "docker", "pod"]
            },
            
            LogFormat.KUBERNETES: {
                "pattern": re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+(\S+)\s+(\S+)\s+(.+)$'),
                "k8s_indicators": ["pod", "namespace", "container", "kubernetes"]
            },
            
            LogFormat.AWS_CLOUDWATCH: {
                "pattern": re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+(\S+)\s+(\S+)\s+(.+)$'),
                "aws_indicators": ["aws", "cloudwatch", "lambda", "ec2", "rds"]
            },
            
            LogFormat.AZURE_MONITOR: {
                "pattern": re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+(\S+)\s+(.+)$'),
                "azure_indicators": ["azure", "monitor", "appservice", "function"]
            },
            
            LogFormat.GCP_CLOUD_LOGGING: {
                "pattern": re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+(\S+)\s+(.+)$'),
                "gcp_indicators": ["gcp", "google", "cloud", "gke", "cloudrun"]
            },
            
            LogFormat.WINDOWS_EVENT: {
                "pattern": re.compile(r'^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+)\s+(.+)$'),
                "event_levels": ["critical", "error", "warning", "information", "verbose"]
            },
            
            LogFormat.GENERIC: {
                "pattern": re.compile(r'^(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+(\w+)\s+(.+)$'),
                "fallback": True
            }
        }
    
    def detect_format(self, lines: List[str]) -> FormatDetectionResult:
        """
        Detect log format from sample lines
        
        Args:
            lines: Sample log lines
            
        Returns:
            Format detection result
        """
        try:
            if not lines:
                return FormatDetectionResult(
                    format=LogFormat.GENERIC,
                    confidence=0.0,
                    sample_matches=0,
                    total_samples=0,
                    metadata={}
                )
            
            # Limit sample size for performance
            sample_lines = lines[:self.sample_size]
            total_samples = len(sample_lines)
            
            # Test each format
            format_scores = {}
            
            for log_format, config in self.patterns.items():
                score = self._calculate_format_score(sample_lines, log_format, config)
                format_scores[log_format] = score
            
            # Find best match
            best_format = max(format_scores.items(), key=lambda x: x[1])
            format_name, confidence = best_format
            
            # Count matches for best format
            matches = self._count_matches(sample_lines, format_name, self.patterns[format_name])
            
            # Extract metadata
            metadata = self._extract_metadata(sample_lines, format_name, self.patterns[format_name])
            
            return FormatDetectionResult(
                format=format_name,
                confidence=confidence,
                sample_matches=matches,
                total_samples=total_samples,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error detecting log format: {e}")
            return FormatDetectionResult(
                format=LogFormat.GENERIC,
                confidence=0.0,
                sample_matches=0,
                total_samples=len(lines) if lines else 0,
                metadata={"error": str(e)}
            )
    
    def _calculate_format_score(self, lines: List[str], log_format: LogFormat, config: Dict[str, Any]) -> float:
        """Calculate confidence score for a specific format"""
        try:
            matches = 0
            total = len(lines)
            
            if total == 0:
                return 0.0
            
            for line in lines:
                if self._matches_format(line, log_format, config):
                    matches += 1
            
            # Base score from match ratio
            base_score = matches / total
            
            # Apply format-specific scoring
            if log_format == LogFormat.JSON:
                return self._score_json_format(lines, base_score)
            elif log_format == LogFormat.SYSLOG:
                return self._score_syslog_format(lines, base_score, config)
            elif log_format in [LogFormat.APACHE_ACCESS, LogFormat.NGINX_ACCESS]:
                return self._score_web_server_format(lines, base_score, config)
            elif log_format in [LogFormat.APACHE_ERROR, LogFormat.NGINX_ERROR]:
                return self._score_error_log_format(lines, base_score, config)
            elif log_format == LogFormat.DOCKER:
                return self._score_docker_format(lines, base_score, config)
            elif log_format == LogFormat.KUBERNETES:
                return self._score_kubernetes_format(lines, base_score, config)
            elif log_format in [LogFormat.AWS_CLOUDWATCH, LogFormat.AZURE_MONITOR, LogFormat.GCP_CLOUD_LOGGING]:
                return self._score_cloud_format(lines, base_score, config)
            elif log_format == LogFormat.WINDOWS_EVENT:
                return self._score_windows_format(lines, base_score, config)
            else:
                return base_score
                
        except Exception as e:
            logger.error(f"Error calculating format score for {log_format}: {e}")
            return 0.0
    
    def _matches_format(self, line: str, log_format: LogFormat, config: Dict[str, Any]) -> bool:
        """Check if a line matches a specific format"""
        try:
            if not line.strip():
                return False
            
            # Basic pattern matching
            if "pattern" in config:
                if not config["pattern"].match(line.strip()):
                    return False
            
            # Format-specific validation
            if log_format == LogFormat.JSON:
                return self._validate_json_line(line)
            elif log_format == LogFormat.SYSLOG:
                return self._validate_syslog_line(line, config)
            elif log_format in [LogFormat.APACHE_ACCESS, LogFormat.NGINX_ACCESS]:
                return self._validate_web_server_line(line, config)
            elif log_format in [LogFormat.APACHE_ERROR, LogFormat.NGINX_ERROR]:
                return self._validate_error_log_line(line, config)
            elif log_format == LogFormat.DOCKER:
                return self._validate_docker_line(line, config)
            elif log_format == LogFormat.KUBERNETES:
                return self._validate_kubernetes_line(line, config)
            elif log_format in [LogFormat.AWS_CLOUDWATCH, LogFormat.AZURE_MONITOR, LogFormat.GCP_CLOUD_LOGGING]:
                return self._validate_cloud_line(line, config)
            elif log_format == LogFormat.WINDOWS_EVENT:
                return self._validate_windows_line(line, config)
            
            return True
            
        except Exception as e:
            logger.debug(f"Error validating line for {log_format}: {e}")
            return False
    
    def _validate_json_line(self, line: str) -> bool:
        """Validate JSON log line"""
        try:
            data = json.loads(line.strip())
            return isinstance(data, dict)
        except (json.JSONDecodeError, TypeError):
            return False
    
    def _validate_syslog_line(self, line: str, config: Dict[str, Any]) -> bool:
        """Validate syslog line"""
        try:
            match = config["pattern"].match(line.strip())
            if not match:
                return False
            
            priority = int(match.group(1))
            return priority in config.get("priority_levels", range(0, 24))
        except (ValueError, IndexError):
            return False
    
    def _validate_web_server_line(self, line: str, config: Dict[str, Any]) -> bool:
        """Validate web server access log line"""
        try:
            match = config["pattern"].match(line.strip())
            if not match:
                return False
            
            status_code = int(match.group(4))
            return status_code in config.get("status_codes", range(100, 600))
        except (ValueError, IndexError):
            return False
    
    def _validate_error_log_line(self, line: str, config: Dict[str, Any]) -> bool:
        """Validate error log line"""
        try:
            match = config["pattern"].match(line.strip())
            if not match:
                return False
            
            # Check if log level is valid
            if "log_levels" in config:
                log_level = match.group(2).lower()
                return log_level in config["log_levels"]
            
            return True
        except (ValueError, IndexError):
            return False
    
    def _validate_docker_line(self, line: str, config: Dict[str, Any]) -> bool:
        """Validate Docker log line"""
        try:
            match = config["pattern"].match(line.strip())
            if not match:
                return False
            
            # Check for container indicators
            content = line.lower()
            return any(indicator in content for indicator in config.get("container_indicators", []))
        except (ValueError, IndexError):
            return False
    
    def _validate_kubernetes_line(self, line: str, config: Dict[str, Any]) -> bool:
        """Validate Kubernetes log line"""
        try:
            match = config["pattern"].match(line.strip())
            if not match:
                return False
            
            # Check for Kubernetes indicators
            content = line.lower()
            return any(indicator in content for indicator in config.get("k8s_indicators", []))
        except (ValueError, IndexError):
            return False
    
    def _validate_cloud_line(self, line: str, config: Dict[str, Any]) -> bool:
        """Validate cloud log line"""
        try:
            match = config["pattern"].match(line.strip())
            if not match:
                return False
            
            # Check for cloud indicators
            content = line.lower()
            return any(indicator in content for indicator in config.get("aws_indicators", []))
        except (ValueError, IndexError):
            return False
    
    def _validate_windows_line(self, line: str, config: Dict[str, Any]) -> bool:
        """Validate Windows event log line"""
        try:
            match = config["pattern"].match(line.strip())
            if not match:
                return False
            
            # Check if event level is valid
            if "event_levels" in config:
                event_level = match.group(2).lower()
                return event_level in config["event_levels"]
            
            return True
        except (ValueError, IndexError):
            return False
    
    def _score_json_format(self, lines: List[str], base_score: float) -> float:
        """Score JSON format with additional validation"""
        try:
            if base_score < 0.5:
                return base_score
            
            # Check for common JSON log fields
            field_scores = []
            for line in lines[:10]:  # Check first 10 lines
                try:
                    data = json.loads(line.strip())
                    if isinstance(data, dict):
                        score = 0.0
                        if "timestamp" in data or "time" in data or "@timestamp" in data:
                            score += 0.3
                        if "level" in data or "severity" in data or "log_level" in data:
                            score += 0.3
                        if "message" in data or "msg" in data:
                            score += 0.2
                        if "service" in data or "logger" in data:
                            score += 0.2
                        field_scores.append(score)
                except (json.JSONDecodeError, TypeError):
                    continue
            
            if field_scores:
                avg_field_score = sum(field_scores) / len(field_scores)
                return (base_score + avg_field_score) / 2
            
            return base_score
            
        except Exception as e:
            logger.error(f"Error scoring JSON format: {e}")
            return base_score
    
    def _score_syslog_format(self, lines: List[str], base_score: float, config: Dict[str, Any]) -> float:
        """Score syslog format with additional validation"""
        try:
            if base_score < 0.5:
                return base_score
            
            # Check timestamp formats
            timestamp_matches = 0
            for line in lines[:10]:
                try:
                    match = config["pattern"].match(line.strip())
                    if match:
                        timestamp_str = match.group(2)
                        for fmt in config.get("timestamp_formats", []):
                            try:
                                from datetime import datetime
                                datetime.strptime(timestamp_str, fmt)
                                timestamp_matches += 1
                                break
                            except ValueError:
                                continue
                except (IndexError, AttributeError):
                    continue
            
            timestamp_score = timestamp_matches / min(10, len(lines))
            return (base_score + timestamp_score) / 2
            
        except Exception as e:
            logger.error(f"Error scoring syslog format: {e}")
            return base_score
    
    def _score_web_server_format(self, lines: List[str], base_score: float, config: Dict[str, Any]) -> float:
        """Score web server format with additional validation"""
        try:
            if base_score < 0.5:
                return base_score
            
            # Check for valid status codes
            status_matches = 0
            for line in lines[:10]:
                try:
                    match = config["pattern"].match(line.strip())
                    if match:
                        status_code = int(match.group(4))
                        if status_code in config.get("status_codes", range(100, 600)):
                            status_matches += 1
                except (ValueError, IndexError):
                    continue
            
            status_score = status_matches / min(10, len(lines))
            return (base_score + status_score) / 2
            
        except Exception as e:
            logger.error(f"Error scoring web server format: {e}")
            return base_score
    
    def _score_error_log_format(self, lines: List[str], base_score: float, config: Dict[str, Any]) -> float:
        """Score error log format with additional validation"""
        try:
            if base_score < 0.5:
                return base_score
            
            # Check for valid log levels
            level_matches = 0
            for line in lines[:10]:
                try:
                    match = config["pattern"].match(line.strip())
                    if match:
                        log_level = match.group(2).lower()
                        if log_level in config.get("log_levels", []):
                            level_matches += 1
                except (IndexError, AttributeError):
                    continue
            
            level_score = level_matches / min(10, len(lines))
            return (base_score + level_score) / 2
            
        except Exception as e:
            logger.error(f"Error scoring error log format: {e}")
            return base_score
    
    def _score_docker_format(self, lines: List[str], base_score: float, config: Dict[str, Any]) -> float:
        """Score Docker format with additional validation"""
        try:
            if base_score < 0.5:
                return base_score
            
            # Check for container indicators
            indicator_matches = 0
            for line in lines[:10]:
                content = line.lower()
                if any(indicator in content for indicator in config.get("container_indicators", [])):
                    indicator_matches += 1
            
            indicator_score = indicator_matches / min(10, len(lines))
            return (base_score + indicator_score) / 2
            
        except Exception as e:
            logger.error(f"Error scoring Docker format: {e}")
            return base_score
    
    def _score_kubernetes_format(self, lines: List[str], base_score: float, config: Dict[str, Any]) -> float:
        """Score Kubernetes format with additional validation"""
        try:
            if base_score < 0.5:
                return base_score
            
            # Check for Kubernetes indicators
            indicator_matches = 0
            for line in lines[:10]:
                content = line.lower()
                if any(indicator in content for indicator in config.get("k8s_indicators", [])):
                    indicator_matches += 1
            
            indicator_score = indicator_matches / min(10, len(lines))
            return (base_score + indicator_score) / 2
            
        except Exception as e:
            logger.error(f"Error scoring Kubernetes format: {e}")
            return base_score
    
    def _score_cloud_format(self, lines: List[str], base_score: float, config: Dict[str, Any]) -> float:
        """Score cloud format with additional validation"""
        try:
            if base_score < 0.5:
                return base_score
            
            # Check for cloud indicators
            indicator_matches = 0
            for line in lines[:10]:
                content = line.lower()
                if any(indicator in content for indicator in config.get("aws_indicators", [])):
                    indicator_matches += 1
            
            indicator_score = indicator_matches / min(10, len(lines))
            return (base_score + indicator_score) / 2
            
        except Exception as e:
            logger.error(f"Error scoring cloud format: {e}")
            return base_score
    
    def _score_windows_format(self, lines: List[str], base_score: float, config: Dict[str, Any]) -> float:
        """Score Windows format with additional validation"""
        try:
            if base_score < 0.5:
                return base_score
            
            # Check for valid event levels
            level_matches = 0
            for line in lines[:10]:
                try:
                    match = config["pattern"].match(line.strip())
                    if match:
                        event_level = match.group(2).lower()
                        if event_level in config.get("event_levels", []):
                            level_matches += 1
                except (IndexError, AttributeError):
                    continue
            
            level_score = level_matches / min(10, len(lines))
            return (base_score + level_score) / 2
            
        except Exception as e:
            logger.error(f"Error scoring Windows format: {e}")
            return base_score
    
    def _count_matches(self, lines: List[str], log_format: LogFormat, config: Dict[str, Any]) -> int:
        """Count matches for a specific format"""
        matches = 0
        for line in lines:
            if self._matches_format(line, log_format, config):
                matches += 1
        return matches
    
    def _extract_metadata(self, lines: List[str], log_format: LogFormat, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from sample lines"""
        try:
            metadata = {
                "format": log_format.value,
                "sample_size": len(lines),
                "patterns_found": []
            }
            
            # Extract format-specific metadata
            if log_format == LogFormat.JSON:
                metadata.update(self._extract_json_metadata(lines))
            elif log_format == LogFormat.SYSLOG:
                metadata.update(self._extract_syslog_metadata(lines, config))
            elif log_format in [LogFormat.APACHE_ACCESS, LogFormat.NGINX_ACCESS]:
                metadata.update(self._extract_web_server_metadata(lines, config))
            elif log_format in [LogFormat.APACHE_ERROR, LogFormat.NGINX_ERROR]:
                metadata.update(self._extract_error_log_metadata(lines, config))
            elif log_format == LogFormat.DOCKER:
                metadata.update(self._extract_docker_metadata(lines, config))
            elif log_format == LogFormat.KUBERNETES:
                metadata.update(self._extract_kubernetes_metadata(lines, config))
            elif log_format in [LogFormat.AWS_CLOUDWATCH, LogFormat.AZURE_MONITOR, LogFormat.GCP_CLOUD_LOGGING]:
                metadata.update(self._extract_cloud_metadata(lines, config))
            elif log_format == LogFormat.WINDOWS_EVENT:
                metadata.update(self._extract_windows_metadata(lines, config))
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {"error": str(e)}
    
    def _extract_json_metadata(self, lines: List[str]) -> Dict[str, Any]:
        """Extract metadata from JSON logs"""
        try:
            fields = set()
            for line in lines[:10]:
                try:
                    data = json.loads(line.strip())
                    if isinstance(data, dict):
                        fields.update(data.keys())
                except (json.JSONDecodeError, TypeError):
                    continue
            
            return {
                "fields_found": list(fields),
                "field_count": len(fields)
            }
        except Exception as e:
            logger.error(f"Error extracting JSON metadata: {e}")
            return {}
    
    def _extract_syslog_metadata(self, lines: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from syslog"""
        try:
            priorities = set()
            hosts = set()
            
            for line in lines[:10]:
                try:
                    match = config["pattern"].match(line.strip())
                    if match:
                        priority = int(match.group(1))
                        host = match.group(3)
                        priorities.add(priority)
                        hosts.add(host)
                except (ValueError, IndexError):
                    continue
            
            return {
                "priorities_found": list(priorities),
                "hosts_found": list(hosts),
                "priority_count": len(priorities)
            }
        except Exception as e:
            logger.error(f"Error extracting syslog metadata: {e}")
            return {}
    
    def _extract_web_server_metadata(self, lines: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from web server logs"""
        try:
            status_codes = set()
            ips = set()
            
            for line in lines[:10]:
                try:
                    match = config["pattern"].match(line.strip())
                    if match:
                        ip = match.group(1)
                        status_code = int(match.group(4))
                        ips.add(ip)
                        status_codes.add(status_code)
                except (ValueError, IndexError):
                    continue
            
            return {
                "status_codes_found": list(status_codes),
                "ips_found": list(ips),
                "status_code_count": len(status_codes)
            }
        except Exception as e:
            logger.error(f"Error extracting web server metadata: {e}")
            return {}
    
    def _extract_error_log_metadata(self, lines: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from error logs"""
        try:
            log_levels = set()
            
            for line in lines[:10]:
                try:
                    match = config["pattern"].match(line.strip())
                    if match:
                        log_level = match.group(2).lower()
                        log_levels.add(log_level)
                except (IndexError, AttributeError):
                    continue
            
            return {
                "log_levels_found": list(log_levels),
                "log_level_count": len(log_levels)
            }
        except Exception as e:
            logger.error(f"Error extracting error log metadata: {e}")
            return {}
    
    def _extract_docker_metadata(self, lines: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from Docker logs"""
        try:
            containers = set()
            
            for line in lines[:10]:
                try:
                    match = config["pattern"].match(line.strip())
                    if match:
                        container = match.group(2)
                        containers.add(container)
                except (IndexError, AttributeError):
                    continue
            
            return {
                "containers_found": list(containers),
                "container_count": len(containers)
            }
        except Exception as e:
            logger.error(f"Error extracting Docker metadata: {e}")
            return {}
    
    def _extract_kubernetes_metadata(self, lines: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from Kubernetes logs"""
        try:
            pods = set()
            namespaces = set()
            
            for line in lines[:10]:
                try:
                    match = config["pattern"].match(line.strip())
                    if match:
                        pod = match.group(2)
                        namespace = match.group(3)
                        pods.add(pod)
                        namespaces.add(namespace)
                except (IndexError, AttributeError):
                    continue
            
            return {
                "pods_found": list(pods),
                "namespaces_found": list(namespaces),
                "pod_count": len(pods)
            }
        except Exception as e:
            logger.error(f"Error extracting Kubernetes metadata: {e}")
            return {}
    
    def _extract_cloud_metadata(self, lines: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from cloud logs"""
        try:
            services = set()
            
            for line in lines[:10]:
                try:
                    match = config["pattern"].match(line.strip())
                    if match:
                        service = match.group(2)
                        services.add(service)
                except (IndexError, AttributeError):
                    continue
            
            return {
                "services_found": list(services),
                "service_count": len(services)
            }
        except Exception as e:
            logger.error(f"Error extracting cloud metadata: {e}")
            return {}
    
    def _extract_windows_metadata(self, lines: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from Windows event logs"""
        try:
            event_levels = set()
            sources = set()
            
            for line in lines[:10]:
                try:
                    match = config["pattern"].match(line.strip())
                    if match:
                        event_level = match.group(2).lower()
                        source = match.group(3)
                        event_levels.add(event_level)
                        sources.add(source)
                except (IndexError, AttributeError):
                    continue
            
            return {
                "event_levels_found": list(event_levels),
                "sources_found": list(sources),
                "event_level_count": len(event_levels)
            }
        except Exception as e:
            logger.error(f"Error extracting Windows metadata: {e}")
            return {}
