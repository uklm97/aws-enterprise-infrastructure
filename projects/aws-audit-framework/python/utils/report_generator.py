import json
import os
from pathlib import Path
from typing import Dict, Any

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape  # type: ignore
    _JINJA_AVAILABLE = True
except Exception:
    # Jinja2 is optional; fallback to plain HTML/JSON/CSV
    Environment = None  # type: ignore
    FileSystemLoader = None  # type: ignore
    select_autoescape = None  # type: ignore
    _JINJA_AVAILABLE = False

try:
    from weasyprint import HTML  # type: ignore
except Exception:
    HTML = None  # PDF generation optional

import csv

class ReportGenerator:
    """
    Generates reports (HTML, PDF, JSON, CSV) for audit results.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}
        self.output_dir = Path(self.config.get('reporting', {}).get('output_dir', 'reports'))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Setup a minimal Jinja environment; templates can be extended later
        templates_dir = self.config.get('reporting', {}).get('templates_dir')
        if _JINJA_AVAILABLE and templates_dir and Path(templates_dir).exists():
            try:
                self.env = Environment(
                    loader=FileSystemLoader(templates_dir),
                    autoescape=select_autoescape()
                )
            except Exception:
                self.env = None
        else:
            self.env = None

    def generate_html_report(self, reports: Dict[str, Any]) -> Path:
        html_path = self.output_dir / 'audit_report.html'
        if self.env:
            try:
                template = self.env.get_template('report.html')
                rendered = template.render(reports=reports)
                html_path.write_text(rendered)
                return html_path
            except Exception:
                pass
        # Fallback: simple HTML
        html_content = [
            '<html><head><meta charset="utf-8"><title>AWS Audit Report</title></head><body>',
            '<h1>AWS Audit Report</h1>'
        ]
        for section, data in (reports or {}).items():
            html_content.append(f'<h2>{section.capitalize()}</h2>')
            html_content.append('<pre>')
            html_content.append(json.dumps(data, indent=2, default=str))
            html_content.append('</pre>')
        html_content.append('</body></html>')
        html_path.write_text('\n'.join(html_content))
        return html_path

    def generate_pdf_report(self, reports: Dict[str, Any]) -> Path:
        pdf_path = self.output_dir / 'audit_report.pdf'
        if HTML is None:
            # Skip if WeasyPrint not available
            return pdf_path
        html_path = self.generate_html_report(reports)
        try:
            HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        except Exception:
            # Non-fatal
            pass
        return pdf_path

    def generate_json_report(self, reports: Dict[str, Any]) -> Path:
        json_path = self.output_dir / 'audit_results.json'
        try:
            json_path.write_text(json.dumps(reports or {}, indent=2, default=str))
        except Exception:
            pass
        return json_path

    def generate_csv_report(self, reports: Dict[str, Any]) -> Path:
        csv_path = self.output_dir / 'audit_summary.csv'
        # Flatten a minimal summary if available
        summary = (reports or {}).get('summary') or {}
        try:
            with csv_path.open('w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['metric', 'value'])
                for k, v in summary.items():
                    writer.writerow([k, v])
        except Exception:
            pass
        return csv_path
