#!/usr/bin/env python3
"""
Fix all iframe references in Jekyll blog post to use improved styling
"""

import re

def fix_iframes(file_path):
    """Fix all iframe references in the Jekyll post"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define plot captions
    plot_captions = {
        'plot_3.html': 'Climate Region Analysis - Interactive Visualization',
        'plot_4.html': 'Duration vs Customer Impact Analysis',
        'plot_5.html': 'Seasonal Pattern Analysis - Interactive Timeline',
        'plot_6.html': 'Outage Cause Category Analysis',
        'plot_7.html': 'Missing Data Analysis - Interactive Heatmap',
        'plot_8.html': 'MAR Analysis Results - Interactive Charts',
        'plot_9.html': 'Hypothesis Testing Results - Statistical Visualization',
        'plot_10.html': 'Model Performance Comparison - Interactive Dashboard',
        'plot_11.html': 'Feature Importance Analysis - Interactive Bar Chart',
        'plot_12.html': 'Fairness Analysis Results - Comparative Visualization'
    }
    
    # Pattern to match old iframe format
    old_pattern = r'<iframe src="(/assets/plots/plot_\d+\.html)" width="100%" height="600" frameborder="0"></iframe>'
    
    def replace_iframe(match):
        plot_url = match.group(1)
        plot_file = plot_url.split('/')[-1]
        caption = plot_captions.get(plot_file, 'Interactive Visualization')
        
        return f'''<div class="plotly-container">
  <iframe src="{plot_url}" class="plotly-iframe"></iframe>
  <div class="viz-caption">{caption}</div>
</div>'''
    
    # Apply replacements
    new_content = re.sub(old_pattern, replace_iframe, content)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Fixed iframes in {file_path}")

if __name__ == "__main__":
    fix_iframes("_posts/2025-06-01-power-outages-anlaysis.md")