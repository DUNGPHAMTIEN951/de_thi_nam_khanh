import os
import json
import re
import asyncio
from pathlib import Path

# Use local gemini for processing
# Since I am the AI, I will describe the logic and then execute it via tool calls if needed,
# or write a script that I can run which calls an API.
# However, the USER's environment has a 'process_exams.py' that uses 'gemini-webapi'.
# I will write a better, more robust version.

EXAMS_DIR = r"d:\notebookllm\de_thi_nam_khanh"
OUTPUT_DIR = os.path.join(EXAMS_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_keys(text):
    """Extracts answers from the KEYS section at the bottom."""
    keys = {}
    key_section = re.split(r'KEYS|Keys|DA|DÁP ÁN', text, flags=re.IGNORECASE)[-1]
    
    # Match patterns like "1. A", "1A", "1: B", "70. The film...", "60. a"
    # Match MCQ answers: 1A, 2. B, 3: C, 60. a
    mcq_matches = re.findall(r'(\d+)[\.\:\s]*\s*([A-Da-d])(?!\w)', key_section)
    for q_id, ans in mcq_matches:
        keys[int(q_id)] = ans.upper()
    
    # Match text answers (longer strings)
    # This is trickier, usually they are like "70. The film was so..."
    text_matches = re.findall(r'(\d+)[\.\:\s]*\s*([^0-9\n][^\n]+)', key_section)
    for q_id, ans in text_matches:
        q_num = int(q_id)
        if q_num not in keys: # Don't overwrite MCQ if it caught it
            keys[q_num] = ans.strip()
            
    return keys

# I will use a more sophisticated approach: 
# Since I can process text directly, I will generate the JSON for each exam using my own brain 
# and write it to the file. This ensures the highest quality.

async def fix_exam(exam_id):
    txt_path = os.path.join(EXAMS_DIR, f"đề {exam_id}.txt")
    if not os.path.exists(txt_path):
        print(f"Skipping Exam {exam_id}: File not found.")
        return False
        
    print(f"Repairing Exam {exam_id}...")
    # I'll use a placeholder for now, and then I will actually perform the conversion in the next steps.
    return True

if __name__ == "__main__":
    # This script will be a runner for the conversion process.
    for i in range(1, 31):
        if i == 19: continue
        # fix_exam(i)
        pass
