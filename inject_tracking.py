import os
import re

directory = r'd:\notebookllm\de_thi_nam_khanh\output'
tracking_code = """
            // Auto-Tracking for Portal
            try {
                const examId = (typeof currentTestId !== 'undefined') ? currentTestId : window.location.pathname.split('/').pop().replace('.html', '').replace('de_', '');
                const finalScoreNum = (score / questions.length) * 10;
                const existingResults = JSON.parse(localStorage.getItem('nam_khanh_results') || '{}');
                existingResults[examId] = Math.round(finalScoreNum * 10) / 10;
                localStorage.setItem('nam_khanh_results', JSON.stringify(existingResults));
                console.log("Portal Tracking: Saved score", existingResults[examId], "for Exam", examId);
            } catch(e) { console.error("Tracking Error:", e); }
"""

for filename in os.listdir(directory):
    if filename.endswith(".html") and filename.startswith("de_"):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Insert tracking code at the end of gradeTest function
        # Search for resultArea.scrollIntoView({ behavior: 'smooth' });
        pattern = r"resultArea\.scrollIntoView\(\{ behavior: 'smooth' \}\);"
        if re.search(pattern, content):
            new_content = re.sub(pattern, f"resultArea.scrollIntoView({{ behavior: 'smooth' }});\n{tracking_code}", content)
            
            # Also fix the Home link
            new_content = new_content.replace('href="index.html"', 'href="../index.html"')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filename}")
        else:
            print(f"Pattern not found in {filename}")
