# yaml-compare.py
# YAML/ConfigMap comparison tool with console and HTML output
#
# Usage:
# python3 yaml-compare.py file1.yaml file2.yaml [config_key] [start_key] [--html output.html]
#
# Examples:
# python3 yaml-compare.py file1.yaml file2.yaml ipo-config
# python3 yaml-compare.py file1.yaml file2.yaml ipo-config:ipo-config-prod
# python3 yaml-compare.py file1.yaml file2.yaml ipo-config ipo.robot.robot_prog_settings
# python3 yaml-compare.py file1.yaml file2.yaml ipo-config --html diff_report.html

import yaml
import sys
import os
from deepdiff import DeepDiff
from datetime import datetime

def extract_configmap_data(file_path, config_key=None, start_key=None):
    """Extract data from a ConfigMap, optionally from a specific config and starting key."""
    with open(file_path) as f:
        content = f.read()
    
    # Handle multi-document YAML (---)
    docs = list(yaml.safe_load_all(content))
    
    # Find ConfigMap
    data = None
    for doc in docs:
        if doc and doc.get('kind') == 'ConfigMap':
            data = doc.get('data', {})
            break
    
    # If not a ConfigMap, treat as regular YAML
    if data is None:
        data = docs[0] if docs else {}
        return navigate_to_key(data, start_key)
    
    # Parse embedded YAML in ConfigMap
    result = {}
    for key, value in data.items():
        if config_key and config_key not in key:
            continue
        if isinstance(value, str):
            try:
                parsed = yaml.safe_load(value)
                if parsed:
                    result.update(parsed)
            except:
                pass
    
    # Navigate to nested key if requested
    return navigate_to_key(result, start_key)

def navigate_to_key(data, key_path):
    """Navigate to a nested key using dot notation (e.g., 'ipo.robot.robot_prog_settings')"""
    if not key_path:
        return data
    
    keys = key_path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            print(f"Warning: Key '{key}' not found in path '{key_path}'")
            return data
    return current

def truncate(s, max_len=30):
    s = str(s)
    return s if len(s) <= max_len else s[:max_len-3] + "..."

def escape_html(s):
    """Escape HTML special characters."""
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def clean_path(path):
    """Clean up the path string for display."""
    return str(path).replace("root['", "").replace("']['", " → ").replace("']", "")

def generate_html_report(diff, file1_name, file2_name, config_key1, config_key2, start_key):
    """Generate an HTML report of the differences."""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YAML Comparison Report</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        
        /* ========== THEME VARIABLES ========== */
        :root {{
            /* Light Mode (Default) */
            --bg-primary: #f8f9fa;
            --bg-secondary: #ffffff;
            --bg-tertiary: #e9ecef;
            --text-primary: #212529;
            --text-secondary: #495057;
            --text-muted: #6c757d;
            --border-color: #dee2e6;
            --border-light: #e9ecef;
            
            --header-bg: linear-gradient(135deg, #4a90a4 0%, #2d6a7a 100%);
            --header-text: #ffffff;
            
            --accent-changed: #e67e22;
            --accent-changed-bg: #fef5e7;
            --accent-file1: #3498db;
            --accent-file1-bg: #ebf5fb;
            --accent-file2: #27ae60;
            --accent-file2-bg: #e9f7ef;
            
            --section-changed-bg: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
            --section-file1-bg: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            --section-file2-bg: linear-gradient(135deg, #27ae60 0%, #1e8449 100%);
            --section-list1-bg: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
            --section-list2-bg: linear-gradient(135deg, #1abc9c 0%, #16a085 100%);
            
            --value-old-bg: #fdecea;
            --value-old-border: #e74c3c;
            --value-old-text: #c0392b;
            --value-new-bg: #e8f8f0;
            --value-new-border: #27ae60;
            --value-new-text: #1e8449;
            
            --row-number-bg: #3498db;
            --row-number-text: #ffffff;
            
            --button-bg: #e9ecef;
            --button-text: #495057;
            --button-hover-bg: #dee2e6;
            
            --success-bg: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
            
            --shadow-sm: 0 2px 8px rgba(0,0,0,0.08);
            --shadow-md: 0 4px 16px rgba(0,0,0,0.1);
            --shadow-lg: 0 8px 32px rgba(0,0,0,0.12);
        }}
        
        /* Night Mode */
        [data-theme="night"] {{
            --bg-primary: #1a1d23;
            --bg-secondary: #22262e;
            --bg-tertiary: #2a2f38;
            --text-primary: #e4e6eb;
            --text-secondary: #b0b3b8;
            --text-muted: #8a8d91;
            --border-color: #3a3f47;
            --border-light: #2a2f38;
            
            --header-bg: linear-gradient(135deg, #2d5a6a 0%, #1e3d4a 100%);
            --header-text: #e4e6eb;
            
            --accent-changed: #f5a623;
            --accent-changed-bg: #3d3520;
            --accent-file1: #5dade2;
            --accent-file1-bg: #1e3a4a;
            --accent-file2: #58d68d;
            --accent-file2-bg: #1e3a2a;
            
            --section-changed-bg: linear-gradient(135deg, #b8860b 0%, #996600 100%);
            --section-file1-bg: linear-gradient(135deg, #2874a6 0%, #1b4f72 100%);
            --section-file2-bg: linear-gradient(135deg, #1e8449 0%, #145a32 100%);
            --section-list1-bg: linear-gradient(135deg, #7d3c98 0%, #5b2c6f 100%);
            --section-list2-bg: linear-gradient(135deg, #148f77 0%, #0e6655 100%);
            
            --value-old-bg: #3d2a2a;
            --value-old-border: #c0392b;
            --value-old-text: #f1948a;
            --value-new-bg: #2a3d2a;
            --value-new-border: #27ae60;
            --value-new-text: #82e0aa;
            
            --row-number-bg: #2874a6;
            --row-number-text: #e4e6eb;
            
            --button-bg: #2a2f38;
            --button-text: #b0b3b8;
            --button-hover-bg: #3a3f47;
            
            --success-bg: linear-gradient(135deg, #1e8449 0%, #27ae60 100%);
            
            --shadow-sm: 0 2px 8px rgba(0,0,0,0.3);
            --shadow-md: 0 4px 16px rgba(0,0,0,0.4);
            --shadow-lg: 0 8px 32px rgba(0,0,0,0.5);
        }}
        
        /* High Contrast Mode - Maximum Readability */
        [data-theme="contrast"] {{
            --bg-primary: #ffffff;
            --bg-secondary: #ffffff;
            --bg-tertiary: #f0f0f0;
            --text-primary: #000000;
            --text-secondary: #1a1a1a;
            --text-muted: #333333;
            --border-color: #000000;
            --border-light: #666666;
            
            --header-bg: #000000;
            --header-text: #ffffff;
            
            --accent-changed: #b35900;
            --accent-changed-bg: #fff2e6;
            --accent-file1: #0047ab;
            --accent-file1-bg: #e6f0ff;
            --accent-file2: #006400;
            --accent-file2-bg: #e6ffe6;
            
            --section-changed-bg: #b35900;
            --section-file1-bg: #0047ab;
            --section-file2-bg: #006400;
            --section-list1-bg: #4b0082;
            --section-list2-bg: #008080;
            
            --value-old-bg: #ffe6e6;
            --value-old-border: #cc0000;
            --value-old-text: #990000;
            --value-new-bg: #e6ffe6;
            --value-new-border: #006400;
            --value-new-text: #004d00;
            
            --row-number-bg: #000000;
            --row-number-text: #ffffff;
            
            --button-bg: #f0f0f0;
            --button-text: #000000;
            --button-hover-bg: #e0e0e0;
            
            --success-bg: #006400;
            
            --shadow-sm: 0 2px 4px rgba(0,0,0,0.2);
            --shadow-md: 0 4px 8px rgba(0,0,0,0.25);
            --shadow-lg: 0 6px 12px rgba(0,0,0,0.3);
        }}
        
        /* ========== BASE STYLES ========== */
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            font-size: 18px;
            font-weight: 500;
            background: var(--bg-primary);
            color: var(--text-primary);
            margin: 0;
            padding: 28px;
            min-height: 100vh;
            line-height: 1.7;
            transition: background 0.3s ease, color 0.3s ease;
        }}
        .container {{
            max-width: 1500px;
            margin: 0 auto;
        }}
        
        /* ========== THEME SWITCHER ========== */
        .theme-switcher {{
            position: fixed;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 8px;
            background: var(--bg-secondary);
            padding: 8px 12px;
            border-radius: 12px;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-color);
            z-index: 1000;
        }}
        .theme-btn {{
            padding: 10px 16px;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 700;
            background: var(--button-bg);
            color: var(--button-text);
            transition: all 0.2s ease;
        }}
        .theme-btn:hover {{
            background: var(--button-hover-bg);
        }}
        .theme-btn.active {{
            background: var(--row-number-bg);
            color: var(--row-number-text);
            border-color: var(--row-number-bg);
        }}
        
        /* ========== HEADER ========== */
        header {{
            background: var(--header-bg);
            padding: 40px 52px;
            border-radius: 18px;
            margin-bottom: 36px;
            box-shadow: var(--shadow-lg);
        }}
        h1 {{
            margin: 0 0 24px 0;
            font-size: 2.8em;
            font-weight: 800;
            color: var(--header-text);
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .meta-info {{
            display: flex;
            flex-wrap: wrap;
            gap: 28px;
            color: var(--header-text);
            font-size: 1.2em;
            font-weight: 600;
        }}
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .meta-label {{
            font-weight: 700;
            opacity: 0.85;
        }}
        .file-badge {{
            background: rgba(255,255,255,0.2);
            padding: 8px 18px;
            border-radius: 22px;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 1.05em;
            font-weight: 700;
        }}
        
        /* ========== SUCCESS BANNER ========== */
        .success-banner {{
            background: var(--success-bg);
            padding: 60px;
            border-radius: 18px;
            text-align: center;
            box-shadow: var(--shadow-lg);
        }}
        .success-banner h2 {{
            margin: 0;
            font-size: 2.4em;
            font-weight: 800;
            color: #ffffff;
        }}
        .success-icon {{
            font-size: 5em;
            margin-bottom: 24px;
        }}
        
        /* ========== SECTIONS ========== */
        .section {{
            background: var(--bg-secondary);
            border-radius: 18px;
            margin-bottom: 32px;
            overflow: hidden;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-color);
        }}
        .section-header {{
            padding: 24px 32px;
            font-weight: 800;
            font-size: 1.4em;
            display: flex;
            align-items: center;
            gap: 16px;
            cursor: pointer;
            user-select: none;
            transition: filter 0.2s ease;
            color: #ffffff;
        }}
        .section-header:hover {{
            filter: brightness(1.1);
        }}
        .section-header.changed {{
            background: var(--section-changed-bg);
        }}
        .section-header.file1-only {{
            background: var(--section-file1-bg);
        }}
        .section-header.file2-only {{
            background: var(--section-file2-bg);
        }}
        .section-header.list-file1 {{
            background: var(--section-list1-bg);
        }}
        .section-header.list-file2 {{
            background: var(--section-list2-bg);
        }}
        .section-icon {{
            font-size: 1.5em;
        }}
        .section-number {{
            background: rgba(0,0,0,0.25);
            width: 42px;
            height: 42px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1em;
            font-weight: 900;
            flex-shrink: 0;
        }}
        .toggle-icon {{
            margin-left: auto;
            font-size: 1.3em;
            font-weight: 800;
            transition: transform 0.3s ease;
        }}
        .section.collapsed .toggle-icon {{
            transform: rotate(-90deg);
        }}
        .section.collapsed .section-content {{
            display: none;
        }}
        .count-badge {{
            background: rgba(255,255,255,0.25);
            padding: 8px 18px;
            border-radius: 22px;
            font-size: 1em;
            font-weight: 700;
        }}
        .section-content {{
            transition: max-height 0.3s ease;
        }}
        
        /* ========== TABLES ========== */
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background: var(--bg-tertiary);
            padding: 20px 28px;
            text-align: left;
            font-weight: 800;
            color: var(--text-primary);
            text-transform: uppercase;
            font-size: 1.05em;
            letter-spacing: 0.5px;
            border-bottom: 2px solid var(--border-color);
        }}
        th:first-child {{
            width: 60px;
            text-align: center;
        }}
        td {{
            padding: 22px 28px;
            border-bottom: 1px solid var(--border-light);
            vertical-align: top;
            font-size: 1.15em;
            font-weight: 600;
            color: var(--text-primary);
        }}
        tr:hover td {{
            background: var(--bg-tertiary);
        }}
        tr:last-child td {{
            border-bottom: none;
        }}
        .row-number {{
            text-align: center;
            font-weight: 900;
            color: var(--row-number-text);
            font-size: 1.2em;
            background: var(--row-number-bg);
            border-radius: 8px;
            padding: 8px 12px;
            display: inline-block;
            min-width: 36px;
        }}
        .path-cell {{
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 1.1em;
            font-weight: 700;
            color: var(--text-primary);
            word-break: break-all;
            max-width: 420px;
        }}
        .path-segment {{
            color: var(--text-primary);
            font-weight: 700;
        }}
        .path-arrow {{
            color: var(--text-muted);
            margin: 0 6px;
            font-weight: 800;
        }}
        .value-cell {{
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 1.1em;
            font-weight: 700;
            word-break: break-all;
            max-width: 380px;
            padding: 14px 20px;
            border-radius: 10px;
        }}
        .value-old {{
            background: var(--value-old-bg);
            border-left: 5px solid var(--value-old-border);
            color: var(--value-old-text);
        }}
        .value-new {{
            background: var(--value-new-bg);
            border-left: 5px solid var(--value-new-border);
            color: var(--value-new-text);
        }}
        
        /* ========== ITEM LISTS ========== */
        .item-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .item-list li {{
            padding: 22px 32px;
            border-bottom: 1px solid var(--border-light);
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 1.15em;
            font-weight: 700;
            display: flex;
            align-items: flex-start;
            gap: 16px;
            color: var(--text-primary);
        }}
        .item-list li:last-child {{
            border-bottom: none;
        }}
        .item-list li:hover {{
            background: var(--bg-tertiary);
        }}
        .item-number {{
            flex-shrink: 0;
            min-width: 44px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1em;
            font-weight: 900;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        .item-number.remove {{
            background: var(--accent-file1-bg);
            color: var(--accent-file1);
            border: 2px solid var(--accent-file1);
        }}
        .item-number.add {{
            background: var(--accent-file2-bg);
            color: var(--accent-file2);
            border: 2px solid var(--accent-file2);
        }}
        .item-path {{
            color: var(--text-primary);
            word-break: break-all;
            font-weight: 700;
        }}
        .item-value {{
            color: var(--text-secondary);
            margin-left: auto;
            text-align: right;
            max-width: 320px;
            word-break: break-all;
            font-weight: 700;
            background: var(--bg-tertiary);
            padding: 6px 12px;
            border-radius: 6px;
        }}
        
        /* ========== SUMMARY CARDS ========== */
        .summary {{
            display: flex;
            gap: 22px;
            flex-wrap: wrap;
            margin-bottom: 36px;
        }}
        .summary-card {{
            background: var(--bg-secondary);
            padding: 28px 42px;
            border-radius: 14px;
            flex: 1;
            min-width: 180px;
            text-align: center;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border-color);
        }}
        .summary-number {{
            font-size: 3.5em;
            font-weight: 900;
            margin-bottom: 10px;
            color: var(--text-primary);
        }}
        .summary-label {{
            color: var(--text-secondary);
            font-size: 1.1em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .summary-card.changed .summary-number {{ color: var(--accent-changed); }}
        .summary-card.file1 .summary-number {{ color: var(--accent-file1); }}
        .summary-card.file2 .summary-number {{ color: var(--accent-file2); }}
        
        /* ========== LEGEND ========== */
        .legend {{
            display: flex;
            gap: 32px;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 36px;
            padding: 28px;
            background: var(--bg-secondary);
            border-radius: 14px;
            font-size: 1.15em;
            font-weight: 700;
            border: 1px solid var(--border-color);
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            color: var(--text-primary);
        }}
        .legend-color {{
            width: 24px;
            height: 24px;
            border-radius: 6px;
        }}
        .legend-color.changed {{ background: var(--section-changed-bg); }}
        .legend-color.file1 {{ background: var(--accent-file1); }}
        .legend-color.file2 {{ background: var(--accent-file2); }}
        
        /* ========== CONTROLS ========== */
        .controls {{
            display: flex;
            gap: 14px;
            margin-bottom: 28px;
            justify-content: flex-end;
        }}
        .control-btn {{
            background: var(--button-bg);
            color: var(--button-text);
            border: 1px solid var(--border-color);
            padding: 14px 26px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: 700;
            transition: all 0.2s ease;
        }}
        .control-btn:hover {{
            background: var(--button-hover-bg);
        }}
        
        /* ========== FOOTER ========== */
        footer {{
            text-align: center;
            padding: 40px;
            color: var(--text-muted);
            font-size: 1.1em;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="theme-switcher">
        <button class="theme-btn active" onclick="setTheme('light')" id="btn-light">☀️ Light</button>
        <button class="theme-btn" onclick="setTheme('night')" id="btn-night">🌙 Night</button>
        <button class="theme-btn" onclick="setTheme('contrast')" id="btn-contrast">👁️ High Contrast</button>
    </div>
    
    <div class="container">
        <header>
            <h1>📊 YAML Comparison Report</h1>
            <div class="meta-info">
                <div class="meta-item">
                    <span class="meta-label">File 1:</span>
                    <span class="file-badge">{escape_html(file1_name)}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">File 2:</span>
                    <span class="file-badge">{escape_html(file2_name)}</span>
                </div>
"""
    
    if config_key1 and config_key2:
        if config_key1 == config_key2:
            html += f"""
                <div class="meta-item">
                    <span class="meta-label">Config Key:</span>
                    <span class="file-badge">{escape_html(config_key1)}</span>
                </div>
"""
        else:
            html += f"""
                <div class="meta-item">
                    <span class="meta-label">Config Keys:</span>
                    <span class="file-badge">{escape_html(config_key1)} vs {escape_html(config_key2)}</span>
                </div>
"""
    
    if start_key:
        html += f"""
                <div class="meta-item">
                    <span class="meta-label">Path:</span>
                    <span class="file-badge">{escape_html(start_key)}</span>
                </div>
"""
    
    html += f"""
                <div class="meta-item">
                    <span class="meta-label">Generated:</span>
                    <span>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
            </div>
        </header>
"""
    
    if not diff:
        html += """
        <div class="success-banner">
            <div class="success-icon">✅</div>
            <h2>Files are semantically equal!</h2>
        </div>
"""
    else:
        # Calculate summary counts
        changed_count = len(diff.get('values_changed', {}))
        file1_only_count = len(diff.get('dictionary_item_removed', []))
        file2_only_count = len(diff.get('dictionary_item_added', []))
        list_file1_count = len(diff.get('iterable_item_removed', {}))
        list_file2_count = len(diff.get('iterable_item_added', {}))
        total_diffs = changed_count + file1_only_count + file2_only_count + list_file1_count + list_file2_count
        
        html += f"""
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color changed"></div>
                <span>Values Changed</span>
            </div>
            <div class="legend-item">
                <div class="legend-color file1"></div>
                <span>Only in {escape_html(file1_name)}</span>
            </div>
            <div class="legend-item">
                <div class="legend-color file2"></div>
                <span>Only in {escape_html(file2_name)}</span>
            </div>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <div class="summary-number">{total_diffs}</div>
                <div class="summary-label">Total Differences</div>
            </div>
            <div class="summary-card changed">
                <div class="summary-number">{changed_count}</div>
                <div class="summary-label">Values Changed</div>
            </div>
            <div class="summary-card file1">
                <div class="summary-number">{file1_only_count + list_file1_count}</div>
                <div class="summary-label">Only in File 1</div>
            </div>
            <div class="summary-card file2">
                <div class="summary-number">{file2_only_count + list_file2_count}</div>
                <div class="summary-label">Only in File 2</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="control-btn" onclick="expandAll()">▼ Expand All</button>
            <button class="control-btn" onclick="collapseAll()">▲ Collapse All</button>
        </div>
"""
        
        section_num = 1
        
        # Values Changed section
        if 'values_changed' in diff:
            html += f"""
        <div class="section" id="section-changed">
            <div class="section-header changed" onclick="toggleSection('section-changed')">
                <span class="section-number">{section_num}</span>
                <span class="section-icon">🔄</span>
                Values Changed
                <span class="count-badge">{len(diff['values_changed'])} items</span>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="section-content">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th style="width: 38%;">Path</th>
                            <th style="width: 28%;">{escape_html(file1_name)}</th>
                            <th style="width: 28%;">{escape_html(file2_name)}</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            row_num = 1
            for path, change in diff['values_changed'].items():
                path_clean = clean_path(path)
                # Format path with arrows
                path_parts = path_clean.split(' → ')
                path_formatted = '<span class="path-arrow">→</span>'.join(
                    [f'<span class="path-segment">{escape_html(p)}</span>' for p in path_parts]
                )
                old_val = escape_html(str(change['old_value']))
                new_val = escape_html(str(change['new_value']))
                html += f"""
                        <tr>
                            <td><span class="row-number">{row_num}</span></td>
                            <td class="path-cell">{path_formatted}</td>
                            <td><div class="value-cell value-old">{old_val}</div></td>
                            <td><div class="value-cell value-new">{new_val}</div></td>
                        </tr>
"""
                row_num += 1
            html += """
                    </tbody>
                </table>
            </div>
        </div>
"""
            section_num += 1
        
        # Only in File 1 (dictionary_item_removed)
        if 'dictionary_item_removed' in diff:
            html += f"""
        <div class="section" id="section-file1">
            <div class="section-header file1-only" onclick="toggleSection('section-file1')">
                <span class="section-number">{section_num}</span>
                <span class="section-icon">➖</span>
                Only in {escape_html(file1_name)}
                <span class="count-badge">{len(diff['dictionary_item_removed'])} items</span>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="section-content">
                <ul class="item-list">
"""
            item_num = 1
            for item in diff['dictionary_item_removed']:
                path_clean = clean_path(str(item))
                html += f"""
                    <li>
                        <span class="item-number remove">{item_num}</span>
                        <span class="item-path">{escape_html(path_clean)}</span>
                    </li>
"""
                item_num += 1
            html += """
                </ul>
            </div>
        </div>
"""
            section_num += 1
        
        # Only in File 2 (dictionary_item_added)
        if 'dictionary_item_added' in diff:
            html += f"""
        <div class="section" id="section-file2">
            <div class="section-header file2-only" onclick="toggleSection('section-file2')">
                <span class="section-number">{section_num}</span>
                <span class="section-icon">➕</span>
                Only in {escape_html(file2_name)}
                <span class="count-badge">{len(diff['dictionary_item_added'])} items</span>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="section-content">
                <ul class="item-list">
"""
            item_num = 1
            for item in diff['dictionary_item_added']:
                path_clean = clean_path(str(item))
                html += f"""
                    <li>
                        <span class="item-number add">{item_num}</span>
                        <span class="item-path">{escape_html(path_clean)}</span>
                    </li>
"""
                item_num += 1
            html += """
                </ul>
            </div>
        </div>
"""
            section_num += 1
        
        # List items only in File 1
        if 'iterable_item_removed' in diff:
            html += f"""
        <div class="section" id="section-list-file1">
            <div class="section-header list-file1" onclick="toggleSection('section-list-file1')">
                <span class="section-number">{section_num}</span>
                <span class="section-icon">📋</span>
                List Items Only in {escape_html(file1_name)}
                <span class="count-badge">{len(diff['iterable_item_removed'])} items</span>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="section-content">
                <ul class="item-list">
"""
            item_num = 1
            for path, value in diff['iterable_item_removed'].items():
                path_clean = clean_path(path)
                html += f"""
                    <li>
                        <span class="item-number remove">{item_num}</span>
                        <span class="item-path">{escape_html(path_clean)}</span>
                        <span class="item-value">{escape_html(str(value))}</span>
                    </li>
"""
                item_num += 1
            html += """
                </ul>
            </div>
        </div>
"""
            section_num += 1
        
        # List items only in File 2
        if 'iterable_item_added' in diff:
            html += f"""
        <div class="section" id="section-list-file2">
            <div class="section-header list-file2" onclick="toggleSection('section-list-file2')">
                <span class="section-number">{section_num}</span>
                <span class="section-icon">📋</span>
                List Items Only in {escape_html(file2_name)}
                <span class="count-badge">{len(diff['iterable_item_added'])} items</span>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="section-content">
                <ul class="item-list">
"""
            item_num = 1
            for path, value in diff['iterable_item_added'].items():
                path_clean = clean_path(path)
                html += f"""
                    <li>
                        <span class="item-number add">{item_num}</span>
                        <span class="item-path">{escape_html(path_clean)}</span>
                        <span class="item-value">{escape_html(str(value))}</span>
                    </li>
"""
                item_num += 1
            html += """
                </ul>
            </div>
        </div>
"""
    
    html += """
        <footer>
            Generated by yaml-compare.py | YAML Configuration Comparison Tool
        </footer>
    </div>
    
    <script>
        function setTheme(theme) {
            if (theme === 'light') {
                document.documentElement.removeAttribute('data-theme');
            } else {
                document.documentElement.setAttribute('data-theme', theme);
            }
            
            // Update button states
            document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById('btn-' + theme).classList.add('active');
            
            // Save preference
            localStorage.setItem('yaml-compare-theme', theme);
        }
        
        function toggleSection(sectionId) {
            const section = document.getElementById(sectionId);
            section.classList.toggle('collapsed');
        }
        
        function expandAll() {
            document.querySelectorAll('.section').forEach(section => {
                section.classList.remove('collapsed');
            });
        }
        
        function collapseAll() {
            document.querySelectorAll('.section').forEach(section => {
                section.classList.add('collapsed');
            });
        }
        
        // Load saved theme preference
        document.addEventListener('DOMContentLoaded', function() {
            const savedTheme = localStorage.getItem('yaml-compare-theme') || 'light';
            setTheme(savedTheme);
        });
    </script>
</body>
</html>
"""
    return html

def print_diff(diff, file1_name, file2_name):
    if not diff:
        print("✅ Files are semantically equal!")
        return
    
    print("❌ Differences found:\n")
    
    if 'values_changed' in diff:
        print("═══ VALUES CHANGED ═══\n")
        
        # Collect all data first
        rows = []
        for path, change in diff['values_changed'].items():
            path_clean = clean_path(path)
            rows.append((path_clean, str(change['old_value']), str(change['new_value'])))
        
        # Calculate column widths based on content
        num_width = len(str(len(rows)))
        path_width = max(max(len(r[0]) for r in rows), len("Path"))
        old_width = max(max(len(r[1]) for r in rows), len(file1_name))
        new_width = max(max(len(r[2]) for r in rows), len(file2_name))
        
        # Cap value widths but not path width
        old_width = min(old_width, 40)
        new_width = min(new_width, 40)
        
        # Table borders
        top_border    = f"┌{'─' * (num_width + 2)}┬{'─' * (path_width + 2)}┬{'─' * (old_width + 2)}┬{'─' * (new_width + 2)}┐"
        header_sep    = f"├{'─' * (num_width + 2)}┼{'─' * (path_width + 2)}┼{'─' * (old_width + 2)}┼{'─' * (new_width + 2)}┤"
        row_sep       = f"├{'─' * (num_width + 2)}┼{'─' * (path_width + 2)}┼{'─' * (old_width + 2)}┼{'─' * (new_width + 2)}┤"
        bottom_border = f"└{'─' * (num_width + 2)}┴{'─' * (path_width + 2)}┴{'─' * (old_width + 2)}┴{'─' * (new_width + 2)}┘"
        
        # Print table
        print(top_border)
        print(f"│ {'#':<{num_width}} │ {'Path':<{path_width}} │ {file1_name:<{old_width}} │ {file2_name:<{new_width}} │")
        print(header_sep)
        
        for i, (path_clean, old_val, new_val) in enumerate(rows, 1):
            old_val = truncate(old_val, old_width)
            new_val = truncate(new_val, new_width)
            print(f"│ {i:<{num_width}} │ {path_clean:<{path_width}} │ {old_val:<{old_width}} │ {new_val:<{new_width}} │")
            if i < len(rows):
                print(row_sep)
        
        print(bottom_border)
        print()
    
    # SWAPPED: dictionary_item_removed = only in file1
    if 'dictionary_item_removed' in diff:
        print(f"═══ ONLY IN {file1_name} ═══")
        for i, item in enumerate(diff['dictionary_item_removed'], 1):
            path_clean = clean_path(str(item))
            print(f"  {i}. {path_clean}")
        print()
    
    # SWAPPED: dictionary_item_added = only in file2
    if 'dictionary_item_added' in diff:
        print(f"═══ ONLY IN {file2_name} ═══")
        for i, item in enumerate(diff['dictionary_item_added'], 1):
            path_clean = clean_path(str(item))
            print(f"  {i}. {path_clean}")
        print()
    
    # SWAPPED: iterable_item_removed = only in file1
    if 'iterable_item_removed' in diff:
        print(f"═══ LIST ITEMS ONLY IN {file1_name} ═══")
        for i, (path, value) in enumerate(diff['iterable_item_removed'].items(), 1):
            path_clean = clean_path(path)
            print(f"  {i}. {path_clean}: {value}")
        print()
    
    # SWAPPED: iterable_item_added = only in file2
    if 'iterable_item_added' in diff:
        print(f"═══ LIST ITEMS ONLY IN {file2_name} ═══")
        for i, (path, value) in enumerate(diff['iterable_item_added'].items(), 1):
            path_clean = clean_path(path)
            print(f"  {i}. {path_clean}: {value}")

def parse_config_keys(config_key_arg):
    """Parse config key argument. Supports 'key' or 'key1:key2' format."""
    if not config_key_arg:
        return None, None
    if ':' in config_key_arg:
        parts = config_key_arg.split(':', 1)
        return parts[0], parts[1]
    return config_key_arg, config_key_arg

def parse_args(argv):
    """Parse command line arguments."""
    args = {
        'file1': None,
        'file2': None,
        'config_key': None,
        'start_key': None,
        'html_output': None
    }
    
    positional = []
    i = 1
    while i < len(argv):
        if argv[i] == '--html':
            if i + 1 < len(argv):
                args['html_output'] = argv[i + 1]
                i += 2
            else:
                print("Error: --html requires an output file path")
                sys.exit(1)
        else:
            positional.append(argv[i])
            i += 1
    
    if len(positional) >= 2:
        args['file1'] = positional[0]
        args['file2'] = positional[1]
    if len(positional) >= 3:
        args['config_key'] = positional[2]
    if len(positional) >= 4:
        args['start_key'] = positional[3]
    
    return args

if __name__ == "__main__":
    args = parse_args(sys.argv)
    
    if not args['file1'] or not args['file2']:
        print("Usage: python3 yaml-compare.py file1.yaml file2.yaml [config_key] [start_key] [--html output.html]")
        print("")
        print("Options:")
        print("  config_key    - Key name in ConfigMap data (use 'key1:key2' for different keys per file)")
        print("  start_key     - Dot-notation path to compare (e.g., 'ipo.robot.robot_prog_settings')")
        print("  --html FILE   - Generate HTML report to specified file")
        print("")
        print("Examples:")
        print("  python3 yaml-compare.py file1.yaml file2.yaml")
        print("  python3 yaml-compare.py file1.yaml file2.yaml ipo-config")
        print("  python3 yaml-compare.py file1.yaml file2.yaml ipo-config:ipo-config-prod")
        print("  python3 yaml-compare.py file1.yaml file2.yaml ipo-config ipo.robot.robot_prog_settings")
        print("  python3 yaml-compare.py file1.yaml file2.yaml --html diff_report.html")
        print("  python3 yaml-compare.py file1.yaml file2.yaml ipo-config --html diff_report.html")
        sys.exit(1)
    
    file1_path = args['file1']
    file2_path = args['file2']
    file1_name = os.path.basename(file1_path)
    file2_name = os.path.basename(file2_path)
    
    config_key1, config_key2 = parse_config_keys(args['config_key'])
    start_key = args['start_key']
    
    a = extract_configmap_data(file1_path, config_key1, start_key)
    b = extract_configmap_data(file2_path, config_key2, start_key)
    
    print(f"Comparing: {file1_name} vs {file2_name}")
    if config_key1 and config_key2:
        if config_key1 == config_key2:
            print(f"Config key: {config_key1}")
        else:
            print(f"Config keys: {config_key1} vs {config_key2}")
    if start_key:
        print(f"Starting from: {start_key}")
    print("-" * 50)
    
    diff = DeepDiff(a, b, ignore_order=True, ignore_type_in_groups=[(str, int, float), (bool, str)])
    
    # Console output
    print_diff(diff, file1_name, file2_name)
    
    # HTML output if requested
    if args['html_output']:
        html_content = generate_html_report(diff, file1_name, file2_name, config_key1, config_key2, start_key)
        with open(args['html_output'], 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\n📄 HTML report saved to: {args['html_output']}")
