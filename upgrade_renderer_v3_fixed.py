import os
import re

directory = r'd:\notebookllm\de_thi_nam_khanh\output'

# New Smart Renderer Logic
new_renderer_js = r"""
        /* SMART RENDERER V3.0 - PASSAGE & CLOZE SUPPORT */
        function renderQuestions(containerId, data) {
            const container = document.getElementById(containerId);
            if (!data || data.length === 0) {
                container.innerHTML = '<div class="p-10 text-center text-gray-400 italic bg-gray-50 rounded-3xl border-2 border-dashed border-gray-200">Không có dữ liệu bài tập cho phần này.</div>';
                return;
            }

            let html = '';
            let i = 0;
            
            while (i < data.length) {
                let q = data[i];
                
                // 1. CLOZE TEST DETECTION (Sequence with (1), (2), (3)...)
                if (q.text.includes('(1)') || q.text.includes('(1-') || q.text.includes('(1 –')) {
                    let passageQuestions = [];
                    let passageText = '';
                    let wordBox = [];
                    let j = i;
                    
                    while (j < data.length) {
                        let nextQ = data[j];
                        let numMatch = nextQ.text.match(/\((\d+)[\s\-–)]/);
                        if (numMatch || (j === i)) {
                            passageQuestions.push(nextQ);
                            if (nextQ.answer) {
                                let ans = Array.isArray(nextQ.answer) ? nextQ.answer[0] : nextQ.answer;
                                if (ans.length < 25) wordBox.push(ans);
                            }

                            let cleanedText = nextQ.text.replace(/Write the correct form of verb for \(\d+\):|Write the suitable word to fill in the blank \(\d+\):|Complete the sentence:|Nowadays,/, '').trim();
                            
                            if (numMatch) {
                                let num = numMatch[1];
                                cleanedText = cleanedText.replace(numMatch[0], `
                                    <span class="inline-block relative group/cloze mx-1">
                                        <input type="text" id="${containerId}-q${nextQ.id}" 
                                            class="w-28 px-2 py-0.5 bg-amber-50/50 border-b-2 border-amber-300 focus:border-indigo-600 focus:bg-white outline-none transition-all text-indigo-700 font-bold text-center placeholder:text-amber-200" 
                                            placeholder="(${num})">
                                        <div id="feedback-${containerId}-q${nextQ.id}" class="hidden absolute top-full left-0 z-20 w-48 mt-1"></div>
                                    </span>
                                `);
                            }
                            passageText += cleanedText + ' ';
                            j++;
                        } else { break; }
                    }
                    
                    wordBox = [...new Set(wordBox)].sort(() => Math.random() - 0.5);
                    
                    html += `
                        <div class="glass-card p-8 md:p-10 rounded-[2.5rem] border border-indigo-100 shadow-xl mb-12 bg-gradient-to-br from-white to-indigo-50/20 relative overflow-hidden">
                            <div class="absolute top-0 right-0 p-8 opacity-10"><i class="fa-solid fa-feather-pointed text-6xl text-indigo-600"></i></div>
                            <div class="flex items-center gap-3 mb-8">
                                <span class="px-4 py-1.5 bg-indigo-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest shadow-lg shadow-indigo-200">Cloze Test</span>
                                <h4 class="text-sm font-bold text-indigo-900/50 uppercase tracking-tight">Điền từ vào đoạn văn</h4>
                            </div>
                            
                            ${wordBox.length > 0 ? `
                            <div class="mb-8 p-6 bg-white/50 rounded-2xl border-2 border-dashed border-indigo-100 flex flex-wrap gap-3 justify-center">
                                ${wordBox.map(w => `<span class="px-4 py-1.5 bg-white shadow-sm border border-indigo-50 rounded-lg text-sm font-bold text-indigo-600 cursor-default hover:scale-105 transition-transform">${w}</span>`).join('')}
                            </div>` : ''}

                            <div class="leading-[2.2] text-gray-700 text-lg font-medium text-justify">
                                ${passageText}
                            </div>
                        </div>
                    `;
                    i = j;
                } 
                else if (q.text.length > 500) {
                     html += `
                        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12 items-start">
                            <div class="glass-card p-8 rounded-[2.5rem] bg-slate-50 border border-slate-200 lg:sticky lg:top-8 max-h-[85vh] overflow-y-auto custom-scrollbar shadow-inner">
                                <div class="flex items-center gap-2 mb-6 text-slate-400">
                                    <i class="fa-solid fa-book-open-reader"></i>
                                    <span class="text-[10px] font-black uppercase tracking-widest">Reading Passage</span>
                                </div>
                                <div class="text-gray-800 leading-relaxed text-justify font-medium text-lg italic pr-4">${q.text}</div>
                            </div>
                            <div class="space-y-6">
                                ${renderSingleQuestion(q, i + 1, containerId)}
                            </div>
                        </div>
                     `;
                     i++;
                } 
                else {
                    html += renderSingleQuestion(q, i + 1, containerId);
                    i++;
                }
            }
            container.innerHTML = html;
        }

        function renderSingleQuestion(q, idx, containerId) {
            const qTypeIcon = q.type === 'mcq' ? 'fa-list-ul' : 'fa-keyboard';
            const qTypeText = q.type === 'mcq' ? 'Trắc nghiệm' : 'Điền từ';
            
            return `
            <div class="bg-white rounded-[2.5rem] shadow-sm border border-gray-100 overflow-hidden transition-all duration-300 hover:shadow-xl hover:border-indigo-100 group mb-6">
                <div class="p-6 md:p-8">
                    <div class="flex items-start gap-4 mb-6">
                        <div class="shrink-0 w-12 h-12 bg-slate-50 text-slate-400 rounded-2xl flex items-center justify-center font-black text-lg border border-slate-100 group-hover:bg-indigo-600 group-hover:text-white group-hover:border-indigo-500 transition-all duration-300">${idx}</div>
                        <div class="flex-1 min-w-0">
                            <div class="flex items-center gap-3 mb-2">
                                <span class="px-3 py-1 bg-slate-50 text-slate-500 rounded-lg text-[10px] font-black uppercase tracking-wider flex items-center gap-1.5 border border-slate-100 group-hover:bg-indigo-50 group-hover:text-indigo-600 group-hover:border-indigo-100 transition-colors">
                                    <i class="fa-solid ${qTypeIcon}"></i> ${qTypeText}
                                </span>
                                ${q.tag ? `<span class="px-3 py-1 bg-emerald-50 text-emerald-600 rounded-lg text-[10px] font-bold uppercase tracking-tight border border-emerald-100">${q.tag}</span>` : ''}
                            </div>
                            <h3 class="text-lg md:text-xl font-bold text-gray-800 leading-relaxed group-hover:text-indigo-900 transition-colors">${q.text}</h3>
                        </div>
                    </div>

                    <div class="ml-0 md:ml-16 space-y-3">
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

                    <div id="feedback-${containerId}-q${q.id}" class="hidden mt-6 ml-0 md:ml-16"></div>
                    
                    <div class="mt-6 flex items-center gap-4 ml-0 md:ml-16">
                        <button type="button" onclick="toggleSimilar('${containerId}-q${q.id}', '${q.id}', '${containerId}')" 
                            class="text-[10px] font-black text-indigo-600 hover:text-indigo-800 flex items-center gap-2 bg-indigo-50 px-4 py-2 rounded-xl transition-colors border border-indigo-100 uppercase tracking-widest">
                            <i class="fa-solid fa-sparkles"></i> Xem bài tương tự
                        </button>
                    </div>

                    <div id="similar-${containerId}-q${q.id}" class="hidden ml-0 md:ml-16 mt-4 animate-in fade-in slide-in-from-top-4 duration-300"></div>
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
        
        # Using string find and replace for robustness
        start_marker = "function renderQuestions(containerId, data) {"
        end_marker = "function initApp()"
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            # Replace everything from start_marker up to end_marker (leaving some space)
            new_content = content[:start_idx] + new_renderer_js + "\n\n        " + content[end_idx:]
            
            # Remove ml-14 classes in gradeTest
            new_content = new_content.replace('ml-14', '')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed & Upgraded {filename} to V3.0")
        else:
            print(f"Markers not found in {filename}")
