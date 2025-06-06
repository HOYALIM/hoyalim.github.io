#!/usr/bin/env python3
import json
import os

def extract_plots():
    # 노트북 경로 (필요시 수정)
    notebook_path = '/Users/ho/code/dsc80/dsc80-2025-sp/projects/project04/template.ipynb'
    
    # 노트북 로드
    print("📖 노트북 로딩 중...")
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    print(f"✅ 노트북 로드 완료: {len(nb['cells'])} 셀")
    
    plot_count = 0
    
    # 플롯 추출
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code' and cell.get('outputs'):
            for output in cell['outputs']:
                if (output.get('output_type') == 'display_data' and 
                    'text/html' in output.get('data', {})):
                    
                    html_content = ''.join(output['data']['text/html'])
                    if 'plotly' in html_content.lower():
                        plot_count += 1
                        
                        # 완전한 HTML 파일 생성
                        full_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Power Outage Plot {plot_count}</title>
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
    <h2>Power Outage Analysis - Plot {plot_count}</h2>
{html_content}
</body>
</html>'''
                        
                        # 파일 저장
                        filename = f'assets/plots/plot_{plot_count}.html'
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(full_html)
                        
                        print(f'✅ 저장완료: plot_{plot_count}.html')
    
    print(f'\n🎯 총 {plot_count}개의 플롯을 추출했습니다!')
    return plot_count

if __name__ == "__main__":
    # 폴더 확인/생성
    if not os.path.exists('assets/plots'):
        os.makedirs('assets/plots')
        print("📁 assets/plots 폴더 생성됨")
    
    # 플롯 추출 실행
    extract_plots()