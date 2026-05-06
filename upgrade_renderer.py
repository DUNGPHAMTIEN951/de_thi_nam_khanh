import os
import re

directory = r'd:\notebookllm\de_thi_nam_khanh\output'

# New Smart Renderer Logic
new_renderer_js = """
        function renderQuestions(containerId, questions) {
            const container = document.getElementById(containerId);
            if (!questions || questions.length === 0) return;

            let html = '';
            let i = 0;
            
            while (i < questions.length) {
                let q = questions[i];
                
                // Detect Cloze Test (Passage with (1), (2), (3)...)
                if (q.text.includes('(1') || q.text.includes('( 1')) {
                    let passageQuestions = [];
                    let passageText = '';
                    let j = i;
                    
                    // Group all sequential numbered questions
                    while (j < questions.length) {
                        let nextQ = questions[j];
                        let numMatch = nextQ.text.match(/\\((\\d+)[\\s\\-–]/);
                        if (numMatch || (j === i)) {
                            passageQuestions.push(nextQ);
                            // Clean up text for passage view
                            let cleanedText = nextQ.text.replace(/Write the correct form of verb for \\(\\d+\\):|Write the suitable word to fill in the blank \\(\\d+\\):|Complete the sentence:|\\.\\.\\.by|\\.\\.\\.to|Nowadays,/, '').trim();
                            
                            // Replace the number with an input placeholder
                            if (numMatch) {
                                let num = numMatch[1];
                                cleanedText = cleanedText.replace(numMatch[0], ` <span class="inline-block mx-1 w-24 relative"><input type="text" id="${containerId}-q${nextQ.id}" class="w-full px-2 py-1 bg-amber-50 border-b-2 border-amber-300 focus:border-indigo-600 focus:bg-white outline-none transition-all text-indigo-700 font-bold text-center" placeholder="(${num})"><div id="feedback-${containerId}-q${nextQ.id}" class="hidden absolute top-full left-0 z-10 w-48"></div></span> `);
                            }
                            
                            passageText += cleanedText + ' ';
                            j++;
                        } else {
                            break;
                        }
                    }
                    
                    // Render as a Passage Block
                    html += `
                        <div class="glass-card p-8 rounded-[2.5rem] border border-indigo-100 shadow-xl mb-12 bg-gradient-to-br from-white to-indigo-50/30">
                            <div class="flex items-center gap-3 mb-6 text-indigo-600 font-black text-xs uppercase tracking-widest">
                                <i class="fa-solid fa-file-lines"></i> Bài tập điền từ vào đoạn văn
                            </div>
                            <div class="leading-relaxed text-gray-700 text-lg font-medium space-y-4 text-justify">
                                ${passageText}
                            </div>
                        </div>
                    `;
                    i = j; // Skip processed questions
                } else if (q.text.length > 300) {
                     // Detect Reading Passage (Long text)
                     html += `
                        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
                            <div class="glass-card p-8 rounded-[2.5rem] bg-slate-50 border border-slate-200 sticky top-4 max-h-[80vh] overflow-y-auto custom-scrollbar">
                                <div class="text-xs font-black text-slate-400 uppercase tracking-widest mb-4">Văn bản đọc hiểu</div>
                                <div class="text-gray-800 leading-relaxed text-justify font-medium">${q.text}</div>
                            </div>
                            <div class="space-y-6">
                                ${renderSingleQuestion(q, containerId)}
                            </div>
                        </div>
                     `;
                     i++;
                } else {
                    // Standard Question
                    html += renderSingleQuestion(q, containerId);
                    i++;
                }
            }
            container.innerHTML = html;
            lucide.createIcons();
        }

        function renderSingleQuestion(q, containerId) {
            return `
                <div class="question-block p-6 md:p-8 rounded-[2rem] bg-white border border-slate-100 shadow-sm hover:shadow-xl hover:border-indigo-200 transition-all duration-300 group mb-6">
                    <div class="flex items-start gap-4 md:gap-6">
                        <div class="w-10 h-10 md:w-12 md:h-12 rounded-2xl bg-slate-50 flex items-center justify-center shrink-0 border border-slate-100 group-hover:bg-indigo-600 group-hover:text-white transition-all shadow-sm">
                            <span class="text-sm font-black">${q.id}</span>
                        </div>
                        <div class="flex-1 min-w-0">
                            <div class="flex items-center gap-2 mb-3">
                                <span class="px-3 py-1 rounded-full bg-slate-100 text-[10px] font-black text-slate-500 uppercase tracking-wider">
                                    ${q.type === 'mcq' ? 'Trắc nghiệm' : 'Điền từ'}
                                </span>
                            </div>
                            <h3 class="text-base md:text-lg font-bold text-slate-800 leading-relaxed mb-6">${q.text}</h3>
                            
                            <div class="ml-0 space-y-3">
                                ${q.type === 'mcq' ? 
                                    Object.entries(q.options || {}).map(([key, val]) => `
                                        <label class="flex items-center gap-4 p-4 rounded-2xl border-2 border-slate-50 hover:border-indigo-200 hover:bg-indigo-50/50 cursor-pointer transition-all group/opt">
                                            <input type="radio" name="${containerId}-q${q.id}" value="${key}" class="w-5 h-5 text-indigo-600 border-slate-300 focus:ring-indigo-500">
                                            <span class="flex-1 text-slate-700 font-medium group-hover/opt:text-indigo-900 transition-colors">
                                                <b class="mr-2 text-indigo-400 group-hover/opt:text-indigo-600">${key.toUpperCase()}.</b> ${val}
                                            </span>
                                        </label>
                                    `).join('')
                                : 
                                    `<div class="relative group/input max-w-md">
                                        <input type="text" id="${containerId}-q${q.id}" 
                                            class="w-full pl-6 pr-12 py-4 bg-slate-50 border-2 border-slate-100 rounded-2xl focus:border-indigo-500 focus:bg-white focus:ring-0 transition-all text-slate-800 font-bold placeholder:text-slate-300"
                                            placeholder="Nhập câu trả lời của bạn...">
                                        <i class="fa-solid fa-pen-field absolute right-5 top-1/2 -translate-y-1/2 text-slate-300 group-focus-within/input:text-indigo-500 transition-colors"></i>
                                    </div>`
                                }
                            </div>

                            <div id="feedback-${containerId}-q${q.id}" class="hidden mt-6"></div>
                            
                            <div class="mt-6 flex items-center gap-4">
                                <button type="button" onclick="askAiSimilar('${containerId}', '${q.id}')" 
                                    class="text-[10px] font-black text-indigo-600 hover:text-indigo-800 flex items-center gap-2 bg-indigo-50 px-4 py-2 rounded-xl transition-colors border border-indigo-100 uppercase tracking-tight">
                                    <i class="fa-solid fa-sparkles"></i> Xem bài tương tự
                                </button>
                            </div>
                            <div id="similar-area-${containerId}-${q.id}" class="hidden"></div>
                        </div>
                    </div>
                </div>
            `;
        }
"""

for filename in os.listdir(directory):
    if filename.endswith(".html") and filename.startswith("de_"):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the entire renderQuestions function
        # This regex looks for the start of function renderQuestions up to its closing brace
        # Since the function is complex, we use a simpler replacement if possible or replace the whole script part
        
        script_pattern = r'function renderQuestions\(containerId, questions\) \{.*?\}\n\n\s+function initApp\(\)'
        if re.search(script_pattern, content, re.DOTALL):
            new_content = re.sub(script_pattern, new_renderer_js + "\n\n        function initApp()", content, flags=re.DOTALL)
            
            # Update feedback positioning logic in gradeTest to handle inline feedback
            # Change feedbackDiv.className ... ml-14 to something more flexible
            new_content = new_content.replace('shadow-sm ml-14"', 'shadow-sm"')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Upgraded {filename} with Smart Renderer")
        else:
            print(f"Renderer pattern not found in {filename}")
