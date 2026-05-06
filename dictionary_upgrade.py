import os

directory = r'd:\notebookllm\de_thi_nam_khanh\output'

# Universal Script Template V4.0 - Integrated Dictionary & Highlighting
universal_script_template = r"""
        const currentTestId = "{TEST_ID}";
        const testData = database[currentTestId];
        let vocabList = testData.vocab || [];
        let currentVocabIndex = 0;

        // Custom Highlighting Logic
        function highlightVocab(text) {
            if (!vocabList || vocabList.length === 0) return text;
            let highlighted = text;
            // Sort by length descending to match longer phrases first
            const sortedVocab = [...vocabList].sort((a, b) => b.word.length - a.word.length);
            
            sortedVocab.forEach(v => {
                if (v.word.length < 3) return; // Skip very short words
                const escapedWord = v.word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                const regex = new RegExp(`\\b(${escapedWord})\\b`, 'gi');
                highlighted = highlighted.replace(regex, (match) => {
                    return `<span class="vocab-highlight text-indigo-600 border-b-2 border-indigo-200 cursor-pointer hover:bg-indigo-50 px-0.5 rounded transition-colors" onclick="showVocabTooltip('${v.word.replace(/'/g, "\\'")}', event)">${match}</span>`;
                });
            });
            return highlighted;
        }

        function initApp() {
            try {
                if (document.getElementById('testList')) initTestList();
                if (testData) {
                    document.getElementById('qCountDisplay').textContent = (testData.questions || []).length;
                    renderQuestions('questionsContainer', testData.questions);
                    if (testData.exercises) renderQuestions('exercisesContainer', testData.exercises);
                }
                if (typeof loadNotes === 'function') loadNotes();
                if (vocabList.length > 0 && typeof updateFlashcardView === 'function') updateFlashcardView();
                
                setupSelectionLookup();
            } catch (e) { console.error("Init Error:", e); }
        }

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
                
                // CLOZE DETECTION
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
                            passageText += highlightVocab(cleanedText) + ' ';
                            j++;
                        } else { break; }
                    }
                    wordBox = [...new Set(wordBox)].sort(() => Math.random() - 0.5);
                    html += `<div class="glass-card p-8 md:p-10 rounded-[2.5rem] border border-indigo-100 shadow-xl mb-12 bg-gradient-to-br from-white to-indigo-50/20 relative overflow-hidden">
                        <div class="absolute top-0 right-0 p-8 opacity-10"><i class="fa-solid fa-feather-pointed text-6xl text-indigo-600"></i></div>
                        <div class="flex items-center gap-3 mb-8">
                            <span class="px-4 py-1.5 bg-indigo-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest shadow-lg shadow-indigo-200">Cloze Test</span>
                        </div>
                        ${wordBox.length > 0 ? `<div class="mb-8 p-6 bg-white/50 rounded-2xl border-2 border-dashed border-indigo-100 flex flex-wrap gap-3 justify-center">
                            ${wordBox.map(w => `<span class="px-4 py-1.5 bg-white shadow-sm border border-indigo-50 rounded-lg text-sm font-bold text-indigo-600 cursor-default hover:scale-105 transition-transform">${w}</span>`).join('')}
                        </div>` : ''}
                        <div class="leading-[2.2] text-gray-700 text-lg font-medium text-justify">${passageText}</div>
                    </div>`;
                    i = j;
                } else if (q.text.length > 500) {
                     html += `<div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12 items-start">
                        <div class="glass-card p-8 rounded-[2.5rem] bg-slate-50 border border-slate-200 lg:sticky lg:top-8 max-h-[85vh] overflow-y-auto shadow-inner">
                            <div class="text-gray-800 leading-relaxed text-justify font-medium text-lg italic pr-4">${highlightVocab(q.text)}</div>
                        </div>
                        <div class="space-y-6">${renderSingleQuestion(q, i + 1, containerId)}</div>
                    </div>`;
                    i++;
                } else {
                    html += renderSingleQuestion(q, i + 1, containerId);
                    i++;
                }
            }
            container.innerHTML = html;
        }

        function renderSingleQuestion(q, idx, containerId) {
            const qTypeIcon = q.type === 'mcq' ? 'fa-list-ul' : 'fa-keyboard';
            const qTypeText = q.type === 'mcq' ? 'Trắc nghiệm' : 'Điền từ';
            return `<div class="bg-white rounded-[2.5rem] shadow-sm border border-gray-100 overflow-hidden transition-all duration-300 hover:shadow-xl hover:border-indigo-100 group mb-6">
                <div class="p-6 md:p-8">
                    <div class="flex items-start gap-4 mb-6">
                        <div class="shrink-0 w-12 h-12 bg-slate-50 text-slate-400 rounded-2xl flex items-center justify-center font-black text-lg border border-slate-100 group-hover:bg-indigo-600 group-hover:text-white transition-all duration-300">${idx}</div>
                        <div class="flex-1 min-w-0">
                            <div class="flex items-center gap-3 mb-2">
                                <span class="px-3 py-1 bg-slate-50 text-slate-500 rounded-lg text-[10px] font-black uppercase tracking-wider border border-slate-100 group-hover:bg-indigo-50 group-hover:text-indigo-600 transition-colors">
                                    <i class="fa-solid ${qTypeIcon}"></i> ${qTypeText}
                                </span>
                            </div>
                            <h3 class="text-lg md:text-xl font-bold text-gray-800 leading-relaxed group-hover:text-indigo-900 transition-colors">${highlightVocab(q.text)}</h3>
                        </div>
                    </div>
                    <div class="ml-0 md:ml-16 space-y-3">
                        ${q.type === 'mcq' ? Object.entries(q.options || {}).map(([key, val]) => `
                            <label class="flex items-center gap-4 p-4 rounded-2xl border-2 border-slate-50 hover:border-indigo-200 hover:bg-indigo-50/50 cursor-pointer transition-all">
                                <input type="radio" name="${containerId}-q${q.id}" value="${key}" class="w-5 h-5 text-indigo-600 border-slate-300">
                                <span class="flex-1 text-slate-700 font-medium"><b>${key.toUpperCase()}.</b> ${highlightVocab(val)}</span>
                            </label>
                        `).join('') : `
                            <input type="text" id="${containerId}-q${q.id}" class="w-full px-6 py-4 bg-slate-50 border-2 border-slate-100 rounded-2xl focus:border-indigo-500 focus:bg-white outline-none text-slate-800 font-bold" placeholder="Nhập câu trả lời...">
                        `}
                    </div>
                    <div id="feedback-${containerId}-q${q.id}" class="hidden mt-6 ml-0 md:ml-16"></div>
                </div>
            </div>`;
        }

        function gradeTest(formId, dataKey) {
            const questions = testData[dataKey];
            let score = 0;
            const containerId = (dataKey === 'questions') ? 'questionsContainer' : 'exercisesContainer';
            questions.forEach(q => {
                const feedbackDiv = document.getElementById(`feedback-${containerId}-q${q.id}`);
                if (!feedbackDiv) return;
                feedbackDiv.classList.remove('hidden');
                let isCorrect = false;
                let userAns = '';
                if (q.type === 'mcq') {
                    const selected = document.querySelector(`input[name="${containerId}-q${q.id}"]:checked`);
                    userAns = selected ? selected.value : '';
                    isCorrect = userAns.toLowerCase() === (q.answer || "").toLowerCase();
                } else {
                    const input = document.getElementById(`${containerId}-q${q.id}`);
                    userAns = (input.value || '').trim().toLowerCase();
                    const validAnswers = Array.isArray(q.answer) ? q.answer.map(a => a.toLowerCase()) : [(q.answer || "").toLowerCase()];
                    isCorrect = validAnswers.some(ans => userAns === ans || ans.includes(userAns) && userAns.length > 2);
                }
                if (isCorrect) {
                    score++;
                    feedbackDiv.className = "mt-4 p-5 rounded-2xl bg-emerald-50 text-emerald-800 border-l-4 border-emerald-500 shadow-sm";
                    feedbackDiv.innerHTML = `<div class="font-black text-xs uppercase tracking-widest mb-1 text-emerald-600">Chính xác</div> <p class="text-sm">${q.explanation || ''}</p>`;
                } else {
                    feedbackDiv.className = "mt-4 p-5 rounded-2xl bg-rose-50 text-rose-800 border-l-4 border-rose-500 shadow-sm";
                    feedbackDiv.innerHTML = `<div class="font-black text-xs uppercase tracking-widest mb-1 text-rose-600">Chưa đúng</div> <p class="text-sm">Đáp án: ${Array.isArray(q.answer) ? q.answer[0] : q.answer}</p>`;
                }
            });
            const resultArea = document.getElementById(`resultArea-${dataKey}`);
            resultArea.classList.remove('hidden');
            resultArea.querySelector('.scoreDisplay').textContent = `${score}/${questions.length}`;
            resultArea.scrollIntoView({ behavior: 'smooth' });
            try {
                const finalScoreNum = (score / questions.length) * 10;
                const results = JSON.parse(localStorage.getItem('nam_khanh_results') || '{}');
                results[currentTestId] = Math.round(finalScoreNum * 10) / 10;
                localStorage.setItem('nam_khanh_results', JSON.stringify(results));
            } catch(e) {}
        }

        // TOOLTIP & LOOKUP LOGIC
        function showVocabTooltip(word, event) {
            const v = vocabList.find(item => item.word.toLowerCase() === word.toLowerCase());
            if (!v) return;
            
            let tooltip = document.getElementById('vocabTooltip');
            if (!tooltip) {
                tooltip = document.createElement('div');
                tooltip.id = 'vocabTooltip';
                tooltip.className = 'fixed z-[100] bg-white/90 backdrop-blur-xl border border-indigo-100 shadow-2xl p-6 rounded-3xl w-72 transition-all duration-300 opacity-0 scale-90 pointer-events-none';
                document.body.appendChild(tooltip);
            }
            
            tooltip.innerHTML = `
                <div class="flex justify-between items-start mb-3">
                    <div>
                        <h4 class="text-xl font-black text-indigo-600">${v.word}</h4>
                        <p class="text-xs text-slate-400 font-bold tracking-widest uppercase">${v.pron || ''} • ${v.type || ''}</p>
                    </div>
                    <button onclick="speakWord('${v.word.replace(/'/g, "\\'")}')" class="w-8 h-8 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center hover:bg-indigo-600 hover:text-white transition-colors">
                        <i class="fa-solid fa-volume-high text-xs"></i>
                    </button>
                </div>
                <div class="h-px bg-indigo-50 mb-4"></div>
                <p class="text-slate-800 font-bold text-sm mb-3">${v.meaning}</p>
                <p class="text-xs text-slate-500 italic bg-slate-50 p-3 rounded-xl border border-slate-100 leading-relaxed">"${v.example}"</p>
            `;
            
            const rect = event.target.getBoundingClientRect();
            let top = rect.top + window.scrollY - tooltip.offsetHeight - 15;
            let left = rect.left + window.scrollX + (rect.width / 2) - (tooltip.offsetWidth / 2);
            
            // Boundary checks
            if (left < 10) left = 10;
            if (left + tooltip.offsetWidth > window.innerWidth) left = window.innerWidth - tooltip.offsetWidth - 10;
            if (top < 10) top = rect.bottom + window.scrollY + 15;

            tooltip.style.top = `${top}px`;
            tooltip.style.left = `${left}px`;
            tooltip.classList.remove('opacity-0', 'scale-90', 'pointer-events-none');
            tooltip.classList.add('opacity-100', 'scale-100');
            
            // Close on click outside
            const closeHandler = (e) => {
                if (!tooltip.contains(e.target) && e.target !== event.target) {
                    tooltip.classList.add('opacity-0', 'scale-90', 'pointer-events-none');
                    document.removeEventListener('click', closeHandler);
                }
            };
            setTimeout(() => document.addEventListener('click', closeHandler), 10);
        }

        function setupSelectionLookup() {
            let searchBtn = document.getElementById('selectionSearchBtn');
            if (!searchBtn) {
                searchBtn = document.createElement('button');
                searchBtn.id = 'selectionSearchBtn';
                searchBtn.className = 'fixed z-[101] hidden w-10 h-10 bg-indigo-600 text-white rounded-full shadow-xl flex items-center justify-center hover:scale-110 transition-transform';
                searchBtn.innerHTML = '<i class="fa-solid fa-magnifying-glass text-sm"></i>';
                document.body.appendChild(searchBtn);
            }

            document.addEventListener('mouseup', (e) => {
                const selection = window.getSelection().toString().trim();
                if (selection && selection.length > 1 && selection.length < 50) {
                    const range = window.getSelection().getRangeAt(0);
                    const rect = range.getBoundingClientRect();
                    searchBtn.style.top = `${rect.top + window.scrollY - 50}px`;
                    searchBtn.style.left = `${rect.left + window.scrollX + (rect.width/2) - 20}px`;
                    searchBtn.classList.remove('hidden');
                    searchBtn.onmousedown = (ev) => {
                        ev.preventDefault();
                        showVocabTooltip(selection, { target: { getBoundingClientRect: () => rect } });
                        searchBtn.classList.add('hidden');
                    };
                } else {
                    if (!searchBtn.contains(e.target)) searchBtn.classList.add('hidden');
                }
            });
        }

        function speakWord(word) {
            const utterance = new SpeechSynthesisUtterance(word);
            utterance.lang = 'en-US';
            window.speechSynthesis.speak(utterance);
        }

        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('-translate-x-full'); }
        function flipCard() { document.getElementById('flashcardElement').classList.toggle('flipped'); }
        function nextCard() { if (currentVocabIndex < vocabList.length - 1) { currentVocabIndex++; updateFlashcardView(); } }
        function prevCard() { if (currentVocabIndex > 0) { currentVocabIndex--; updateFlashcardView(); } }
        function updateFlashcardView() {
            const v = vocabList[currentVocabIndex];
            if(!v) return;
            document.getElementById('fc-word').textContent = v.word;
            document.getElementById('fc-pron').textContent = v.pron || '';
            document.getElementById('fc-type').textContent = v.type || '';
            document.getElementById('fc-meaning').textContent = v.meaning;
            document.getElementById('fc-example').textContent = `"${v.example}"`;
            document.getElementById('fc-counter').textContent = `${currentVocabIndex + 1} / ${vocabList.length}`;
            document.getElementById('flashcardElement').classList.remove('flipped');
        }
        function switchTab(tab) {
            ['test', 'flashcard', 'quiz'].forEach(t => {
                const btn = document.getElementById(`tab-${t}`);
                const content = document.getElementById(`content-${t}`);
                if (btn) btn.className = "py-3 px-6 text-gray-500 hover:text-blue-600 font-semibold focus:outline-none flex items-center gap-2 transition-colors";
                if (content) content.classList.add('hidden');
            });
            const activeBtn = document.getElementById(`tab-${tab}`);
            const activeContent = document.getElementById(`content-${tab}`);
            if (activeBtn) activeBtn.className = "py-3 px-6 text-blue-700 border-b-2 border-blue-600 font-bold focus:outline-none flex items-center gap-2 bg-white";
            if (activeContent) activeContent.classList.remove('hidden');
            if (tab === 'flashcard') updateFlashcardView();
        }
        function initTestList() {
            const list = document.getElementById('testList');
            if (!list) return;
            list.innerHTML = `<a href="../index.html" class="w-full block text-center py-3 bg-gray-100 hover:bg-gray-200 rounded-lg font-bold text-gray-700 mb-4 transition">Quay lại trang chủ</a>`;
            for (let i = 1; i <= 30; i++) {
                const isActive = i == currentTestId;
                const link = document.createElement('a');
                link.href = `de_${i}.html`;
                link.className = `flex items-center gap-3 p-3 rounded-xl mb-2 border ${isActive ? 'bg-blue-50 border-blue-200 text-blue-700 font-bold' : 'bg-white border-gray-100 text-gray-600'}`;
                link.innerHTML = `<div class="w-8 h-8 rounded-lg ${isActive ? 'bg-blue-600 text-white' : 'bg-gray-100'} flex items-center justify-center text-xs font-black">${i}</div><span>Đề Thi Số ${i}</span>`;
                list.appendChild(link);
            }
        }
        window.onload = initApp;
"""

for filename in os.listdir(directory):
    if filename.endswith(".html") and filename.startswith("de_"):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        db_marker = "const database = "
        db_start = content.find(db_marker)
        if db_start == -1: continue
        
        json_start = db_start + len(db_marker)
        brace_count = 0
        json_end = -1
        for i in range(json_start, len(content)):
            if content[i] == '{': brace_count += 1
            elif content[i] == '}': brace_count -= 1
            if brace_count == 0 and i > json_start:
                json_end = i + 1
                break
        
        if json_end == -1: continue
        database_str = content[json_start:json_end]
        test_id = filename.replace('de_', '').replace('.html', '')
        new_script_code = f"const database = {database_str};\n" + universal_script_template.replace("{TEST_ID}", test_id)
        
        script_tag_start = content.find("<script>")
        script_tag_end = content.find("</script>", script_tag_start)
        
        if script_tag_start != -1 and script_tag_end != -1:
            new_content = content[:script_tag_start] + "<script>" + new_script_code + "</script>" + content[script_tag_end + 9:]
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Dictionary V4.0 Upgrade applied to {filename}")
