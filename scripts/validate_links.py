#!/usr/bin/env python3
"""
Link Validation Script for THEOS Repository

Validates all markdown links to ensure they point to existing files or valid URLs.
Generates a report of broken links and recommendations.
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from collections import defaultdict

class LinkValidator:
    def __init__(self, repo_root):
        self.repo_root = Path(repo_root)
        self.broken_links = []
        self.valid_links = []
        self.external_links = []
        self.files_checked = 0
        
    def is_external_url(self, link):
        """Check if link is an external URL"""
        return link.startswith('http://') or link.startswith('https://')
    
    def resolve_relative_path(self, current_file, link_target):
        """Resolve relative path from current file"""
        if link_target.startswith('/'):
            # Absolute path from repo root
            return self.repo_root / link_target.lstrip('/')
        else:
            # Relative path from current file
            current_dir = current_file.parent
            return (current_dir / link_target).resolve()
    
    def extract_links_from_markdown(self, content):
        """Extract all markdown links from content"""
        # Pattern for [text](url) and ![alt](url)
        pattern = r'\[([^\]]*)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)
        return matches
    
    def validate_file_link(self, link_target):
        """Check if file link exists"""
        # Remove anchor if present
        if '#' in link_target:
            link_target = link_target.split('#')[0]
        
        if not link_target:
            return False
        
        # Try to resolve the path
        try:
            resolved = self.resolve_relative_path(self.current_file, link_target)
            return resolved.exists()
        except:
            return False
    
    def validate_markdown_file(self, filepath):
        """Validate all links in a markdown file"""
        self.current_file = filepath
        self.files_checked += 1
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return
        
        links = self.extract_links_from_markdown(content)
        
        for text, link in links:
            # Skip empty links
            if not link:
                continue
            
            # Check if external URL
            if self.is_external_url(link):
                self.external_links.append({
                    'file': str(filepath.relative_to(self.repo_root)),
                    'text': text,
                    'url': link
                })
            else:
                # Check if file exists
                if self.validate_file_link(link):
                    self.valid_links.append({
                        'file': str(filepath.relative_to(self.repo_root)),
                        'text': text,
                        'link': link
                    })
                else:
                    self.broken_links.append({
                        'file': str(filepath.relative_to(self.repo_root)),
                        'text': text,
                        'link': link
                    })
    
    def validate_repository(self):
        """Validate all markdown files in repository"""
        markdown_files = self.repo_root.glob('**/*.md')
        
        for filepath in sorted(markdown_files):
            self.validate_markdown_file(filepath)
    
    def generate_report(self):
        """Generate validation report"""
        report = []
        report.append("=" * 80)
        report.append("THEOS Repository Link Validation Report")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Files checked: {self.files_checked}")
        report.append(f"Valid internal links: {len(self.valid_links)}")
        report.append(f"External links found: {len(self.external_links)}")
        report.append(f"Broken links found: {len(self.broken_links)}")
        report.append("")
        
        # Broken links
        if self.broken_links:
            report.append("BROKEN LINKS")
            report.append("-" * 80)
            for item in self.broken_links:
                report.append(f"File: {item['file']}")
                report.append(f"  Text: {item['text']}")
                report.append(f"  Link: {item['link']}")
                report.append("")
        else:
            report.append("✓ No broken links found!")
            report.append("")
        
        # External links
        if self.external_links:
            report.append("EXTERNAL LINKS (Not validated)")
            report.append("-" * 80)
            for item in self.external_links[:10]:  # Show first 10
                report.append(f"File: {item['file']}")
                report.append(f"  Text: {item['text']}")
                report.append(f"  URL: {item['url']}")
                report.append("")
            
            if len(self.external_links) > 10:
                report.append(f"... and {len(self.external_links) - 10} more external links")
                report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def print_report(self):
        """Print report to console"""
        print(self.generate_report())
        
        # Return exit code based on broken links
        return 0 if not self.broken_links else 1

def main():
    repo_root = Path(__file__).parent.parent
    
    validator = LinkValidator(repo_root)
    validator.validate_repository()
    exit_code = validator.print_report()
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
