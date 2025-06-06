#!/usr/bin/env python3
"""
Fix Plotly HTML files to work in GitHub Pages iframe
Replace require() calls with direct Plotly.newPlot calls
"""

import os
import re
import glob

def fix_plotly_html(file_path):
    """Fix a single Plotly HTML file"""
    print(f"Processing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the plot title
    title_match = re.search(r'<title>(.*?)</title>', content)
    title = title_match.group(1) if title_match else "Power Outage Plot"
    
    # Extract the div ID
    div_id_match = re.search(r'id="([^"]+)"[^>]*class="plotly-graph-div"', content)
    div_id = div_id_match.group(1) if div_id_match else "plotly-div"
    
    # Extract the Plotly.newPlot call content
    newplot_match = re.search(r'Plotly\.newPlot\(\s*"[^"]+",\s*(\[.*?\]),\s*(\{.*?\}),\s*(\{[^}]*\})\s*\)', content, re.DOTALL)
    
    if not newplot_match:
        print(f"Could not find Plotly.newPlot in {file_path}")
        return False
    
    data = newplot_match.group(1)
    layout = newplot_match.group(2)
    config = newplot_match.group(3)
    
    # Create new HTML content
    new_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
        }}
        .plotly-graph-div {{
            width: 100%;
            height: 600px;
        }}
    </style>
</head>
<body>
    <div id="{div_id}" class="plotly-graph-div"></div>
    
    <script type="text/javascript">
        var data = {data};
        var layout = {layout};
        var config = {config};
        
        Plotly.newPlot('{div_id}', data, layout, config);
    </script>
</body>
</html>'''
    
    # Write the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Fixed {file_path}")
    return True

def main():
    """Fix all plot HTML files"""
    plot_files = glob.glob('/Users/ho/hoyalim.github.io/assets/plots/plot_*.html')
    plot_files = [f for f in plot_files if 'test' not in f]  # Skip test file
    
    print(f"Found {len(plot_files)} plot files to fix...")
    
    for plot_file in sorted(plot_files):
        try:
            fix_plotly_html(plot_file)
        except Exception as e:
            print(f"Error fixing {plot_file}: {e}")
    
    print("Done!")

if __name__ == "__main__":
    main()