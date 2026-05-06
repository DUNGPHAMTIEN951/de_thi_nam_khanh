import os
import json

# Paths
OUTPUT_DIR = r'd:\notebookllm\de_thi_nam_khanh\output'

def generate_html(exam_id):
    json_path = os.path.join(OUTPUT_DIR, f'data_{exam_id}.json')
    if not os.path.exists(json_path):
        print(f"Skipping Exam {exam_id}: data_{exam_id}.json not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Sidebar links generation
    sidebar_links = ""
    for i in range(1, 31):
        active_class = "bg-indigo-50 text-indigo-700 font-bold" if i == exam_id else "text-gray-600 hover:bg-gray-50"
        sidebar_links += f'<a href="de_{i}.html" class="block p-3 rounded-lg text-sm font-medium {active_class}">Đề số {i}</a>\n'

    # The HTML Template (using placeholders)
    template = r"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>English Practice {{EXAM_ID}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
        .glass-card { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); }
        .vocab-highlight { transition: all 0.2s; }
        .vocab-highlight:hover { background-color: #eef2ff; color: #4f46e5; }
        .perspective-1000 { perspective: 1000px; }
        .flip-card-inner { transition: transform 0.6s; transform-style: preserve-3d; }
        .flipped .flip-card-inner { transform: rotateY(180deg); }
        .backface-hidden { backface-visibility: hidden; }
        #noteSidebar { transition: width 0.3s ease-in-out, opacity 0.3s; width: 0; opacity: 0; }
        #noteSidebar.open { width: 350px; opacity: 1; }
        .no-scrollbar::-webkit-scrollbar { display: none; }
    </style>
</head>
<body class="text-gray-800 antialiased flex h-screen overflow-hidden bg-gray-100">
    <aside id="sidebar" class="w-72 bg-white shadow-2xl h-full flex flex-col z-30 fixed lg:relative transform -translate-x-full lg:translate-x-0 transition-transform">
        <div class="p-5 bg-indigo-700 text-white flex justify-between items-center shrink-0">
            <div class="flex items-center gap-3">
                <i class="fa-solid fa-graduation-cap text-3xl"></i>
                <h1 class="font-black text-lg leading-tight">Nam Khanh<br><span class="text-xs font-normal text-indigo-200 uppercase tracking-widest">Exam Portal</span></h1>
            </div>
        </div>
        <div class="flex-1 overflow-y-auto p-4" id="testList">
            <a href="../index.html" class="w-full block text-center py-3 bg-gray-100 hover:bg-gray-200 rounded-xl font-bold text-gray-700 mb-4 transition">
                <i class="fa-solid fa-house mr-2"></i> Trang chủ
            </a>
            <div class="space-y-1">
                {{SIDEBAR_LINKS}}
            </div>
        </div>
    </aside>

    <main class="flex-1 flex flex-col h-full relative overflow-hidden w-full bg-slate-50">
        <header class="bg-white shadow-sm z-10 shrink-0 border-b border-slate-200">
            <div class="px-6 py-4 flex justify-between items-center">
                <div class="flex items-center gap-4">
                    <button onclick="toggleSidebar()" class="lg:hidden text-gray-500 text-2xl"><i class="fa-solid fa-bars"></i></button>
                    <h2 class="text-xl font-black text-slate-800 uppercase tracking-tight">Practice Exam {{EXAM_ID}}</h2>
                </div>
                <div class="flex items-center gap-3">
                    <button onclick="toggleNotes()" class="bg-amber-50 text-amber-700 px-4 py-2 rounded-full text-sm font-bold border border-amber-200 hover:bg-amber-100 transition"><i class="fa-solid fa-note-sticky mr-2"></i>Ghi chú</button>
                    <div class="bg-indigo-100 text-indigo-700 px-4 py-2 rounded-full text-sm font-bold"><i class="fa-solid fa-list-check mr-2"></i><span id="qCountDisplay">0</span> Câu</div>
                </div>
            </div>
            <div class="flex px-6 bg-white overflow-x-auto no-scrollbar gap-8">
                <button onclick="switchTab('test')" id="tab-test" class="py-4 text-indigo-700 border-b-4 border-indigo-600 font-black text-sm uppercase tracking-wider whitespace-nowrap">Làm bài thi</button>
                <button onclick="switchTab('flashcard')" id="tab-flashcard" class="py-4 text-slate-400 hover:text-indigo-600 font-bold text-sm uppercase tracking-wider transition-colors whitespace-nowrap">Flashcards</button>
            </div>
        </header>

        <div class="flex-1 flex overflow-hidden">
            <div class="flex-1 overflow-y-auto relative p-6 md:p-10 no-scrollbar" id="mainScrollContainer">
                <div id="content-test" class="max-w-5xl mx-auto space-y-8 pb-20">
                    <div id="questionsContainer" class="space-y-6"></div>
                    <div class="text-center pt-10 border-t border-slate-200">
                        <button onclick="gradeTest()" class="bg-indigo-600 text-white px-12 py-4 rounded-full font-black text-xl shadow-xl shadow-indigo-200 hover:bg-indigo-700 transition transform hover:scale-105 active:scale-95">NỘP BÀI & XEM GIẢI THÍCH</button>
                    </div>
                    <div id="resultArea" class="hidden mt-8 p-10 bg-white rounded-[2.5rem] border-2 border-indigo-50 shadow-2xl text-center">
                        <h3 class="text-2xl font-black text-slate-800 mb-2">KẾT QUẢ CỦA BẠN</h3>
                        <div id="scoreDisplay" class="text-7xl font-black text-indigo-600 my-6">0/0</div>
                        <p id="messageDisplay" class="text-slate-500 font-medium"></p>
                    </div>
                </div>

                <div id="content-flashcard" class="hidden h-full flex flex-col items-center justify-center space-y-8">
                    <div class="perspective-1000 w-full max-w-md h-80" id="flashcardContainer" onclick="this.classList.toggle('flipped')">
                        <div class="flip-card-inner relative w-full h-full cursor-pointer">
                            <div class="backface-hidden absolute w-full h-full bg-white rounded-[2.5rem] shadow-2xl border border-slate-100 flex flex-col items-center justify-center p-10 text-center">
                                <h3 id="fc-word" class="text-5xl font-black text-indigo-600 mb-4">Word</h3>
                                <p id="fc-pron" class="text-slate-400 italic text-xl">/pron/</p>
                            </div>
                            <div class="backface-hidden absolute w-full h-full bg-indigo-600 text-white rounded-[2.5rem] shadow-2xl flex flex-col items-center justify-center p-10 text-center rotate-y-180" style="transform: rotateY(180deg)">
                                <span id="fc-type" class="bg-white/20 px-3 py-1 rounded-full text-xs font-black uppercase mb-4">Type</span>
                                <p id="fc-meaning" class="text-3xl font-bold mb-6">Meaning</p>
                                <p id="fc-example" class="text-lg italic opacity-90 font-light leading-relaxed">Example</p>
                            </div>
                        </div>
                    </div>
                    <div class="flex items-center gap-6">
                        <button onclick="prevCard()" class="w-12 h-12 bg-white rounded-full shadow-lg text-slate-400 hover:text-indigo-600 flex items-center justify-center transition"><i class="fa-solid fa-chevron-left"></i></button>
                        <span id="fc-counter" class="font-black text-slate-400 tracking-widest uppercase text-sm">1 / 1</span>
                        <button onclick="nextCard()" class="w-12 h-12 bg-white rounded-full shadow-lg text-slate-400 hover:text-indigo-600 flex items-center justify-center transition"><i class="fa-solid fa-chevron-right"></i></button>
                    </div>
                </div>
            </div>

            <aside id="noteSidebar" class="bg-amber-50/50 border-l border-amber-100 flex flex-col">
                <div class="p-6 border-b border-amber-100 flex justify-between items-center">
                    <h3 class="font-black text-amber-800 text-sm uppercase tracking-widest"><i class="fa-solid fa-pen-nib mr-2"></i>Ghi chú bài học</h3>
                    <button onclick="toggleNotes()"><i class="fa-solid fa-xmark text-amber-300 hover:text-amber-600 transition"></i></button>
                </div>
                <textarea id="notesArea" class="flex-1 bg-transparent p-6 outline-none text-slate-700 font-medium leading-relaxed resize-none" placeholder="Lưu lại những từ vựng mới hoặc kiến thức cần nhớ..."></textarea>
            </aside>
        </div>

        <div id="vocabTooltip" class="fixed z-50 hidden bg-white rounded-2xl shadow-2xl border border-slate-100 p-6 w-80 pointer-events-auto opacity-0 transition-opacity">
             <div class="flex justify-between items-start mb-4">
                <div>
                    <h4 id="tt-word" class="text-2xl font-black text-indigo-600">Word</h4>
                    <p id="tt-pron" class="text-sm text-slate-400 italic">/pron/</p>
                </div>
                <button onclick="speakWord()" class="w-10 h-10 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center hover:bg-indigo-100 transition"><i class="fa-solid fa-volume-high"></i></button>
             </div>
             <p id="tt-meaning" class="text-lg font-bold text-slate-800 mb-4">Meaning</p>
             <p id="tt-example" class="text-sm text-slate-500 italic bg-slate-50 p-3 rounded-xl border-l-4 border-indigo-400">Example</p>
        </div>
    </main>

    <script>
        const database = { "{{EXAM_ID}}": {{JSON_DATA}} };
        const currentTestId = "{{EXAM_ID}}";
        const testData = database[currentTestId];
        let vocabList = testData.vocab || [];
        let currentVocabIndex = 0;

        function highlightVocab(text) {
            if (!vocabList || vocabList.length === 0 || !text) return text;
            const parts = text.split(/(<[^>]+>)/g);
            return parts.map(part => {
                if (part.startsWith('<')) return part;
                let res = part;
                [...vocabList].sort((a,b) => b.word.length - a.word.length).forEach(v => {
                    const regex = new RegExp(`\\b(${v.word})\\b`, 'gi');
                    res = res.replace(regex, (m) => `<span class="vocab-highlight text-indigo-600 border-b-2 border-indigo-200 cursor-pointer hover:bg-indigo-50 px-0.5 rounded" onclick="showVocabTooltip('${v.word}', event)">${m}</span>`);
                });
                return res;
            }).join('');
        }

        function renderQuestions() {
            const container = document.getElementById('questionsContainer');
            let html = '';
            let i = 0;
            const qs = testData.questions;
            while(i < qs.length) {
                let q = qs[i];
                if (q.tag === 'Reading') {
                    let readingText = q.text.split('Question:')[0].trim();
                    let readingQuestions = [];
                    let j = i;
                    while(j < qs.length && qs[j].tag === 'Reading') {
                        readingQuestions.push(qs[j]);
                        j++;
                    }
                    html += `<div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
                        <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100 leading-relaxed text-slate-600 text-justify sticky top-0 max-h-[70vh] overflow-y-auto no-scrollbar">
                            <div class="flex items-center gap-2 mb-6 text-indigo-600 font-black uppercase tracking-widest text-xs"><i class="fa-solid fa-book-open"></i> Reading Passage</div>
                            ${highlightVocab(readingText.replace(/\n/g, '<br>'))}
                        </div>
                        <div class="space-y-6">
                            ${readingQuestions.map(rq => renderSingleQuestion(rq)).join('')}
                        </div>
                    </div>`;
                    i = j;
                } 
                else if (q.text.includes('(1)') || q.text.includes('(1-')) {
                    let passage = '';
                    let answers = [];
                    let j = i;
                    while(j < qs.length && (qs[j].text.includes('(' + (j-i+1) + ')') || j==i)) {
                        let cleaned = qs[j].text.replace(/\(\d+\)/g, (m) => `<input type="text" data-id="${qs[j].id}" class="w-24 px-2 py-0.5 border-b-2 border-indigo-200 outline-none focus:border-indigo-600 text-indigo-700 font-bold text-center bg-transparent" placeholder="${m}">`);
                        passage += cleaned + ' ';
                        if (qs[j].answer && qs[j].answer.length < 20) answers.push(qs[j].answer);
                        j++;
                    }
                    html += `<div class="glass-card p-10 rounded-[2.5rem] border border-indigo-100 shadow-xl mb-12">
                        <div class="text-xs font-black text-indigo-600 uppercase tracking-widest mb-6"><i class="fa-solid fa-pen-clip mr-2"></i> Cloze Test</div>
                        ${answers.length > 0 ? `<div class="mb-8 p-6 bg-slate-50 rounded-2xl flex flex-wrap gap-2 justify-center border-2 border-dashed border-slate-200">${answers.sort(()=>Math.random()-0.5).map(a => `<span class="bg-white px-3 py-1 rounded-lg shadow-sm text-sm font-bold text-slate-600">${a}</span>`).join('')}</div>` : ''}
                        <div class="text-lg leading-[2.5] text-slate-700 text-justify">${highlightVocab(passage)}</div>
                    </div>`;
                    i = j;
                }
                else {
                    html += renderSingleQuestion(q);
                    i++;
                }
            }
            container.innerHTML = html;
        }

        function renderSingleQuestion(q) {
            let content = '';
            if (q.type === 'mcq') {
                content = `<div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
                    ${Object.entries(q.options).map(([key, val]) => `
                        <label class="flex items-center p-4 bg-slate-50 rounded-2xl border-2 border-transparent hover:border-indigo-100 cursor-pointer transition-all group has-[:checked]:border-indigo-500 has-[:checked]:bg-indigo-50">
                            <input type="radio" name="q${q.id}" value="${key}" class="sr-only peer">
                            <span class="w-8 h-8 rounded-full border-2 border-slate-200 flex items-center justify-center mr-4 group-hover:bg-indigo-500 group-hover:text-white peer-checked:bg-indigo-600 peer-checked:text-white peer-checked:border-indigo-600 font-black transition-colors">${key}</span>
                            <span class="font-medium text-slate-600 peer-checked:text-indigo-900 peer-checked:font-bold">${val}</span>
                        </label>
                    `).join('')}
                </div>`;
            } else {
                content = `<input type="text" data-id="${q.id}" class="w-full mt-4 p-4 bg-slate-50 rounded-2xl border-2 border-transparent focus:border-indigo-500 outline-none font-bold text-indigo-700" placeholder="Nhập câu trả lời của bạn...">`;
            }
            return `<div class="glass-card p-8 rounded-[2.5rem] border border-slate-100 shadow-sm relative group hover:shadow-md transition-shadow" id="q-block-${q.id}">
                <div class="absolute -left-3 top-8 w-10 h-10 bg-indigo-600 text-white rounded-xl flex items-center justify-center font-black shadow-lg">${q.id}</div>
                <div class="pl-8">
                    <p class="text-lg font-bold text-slate-800 leading-relaxed">${highlightVocab(q.text.split('Question:').pop().trim())}</p>
                    ${content}
                    <div id="explanation-${q.id}" class="hidden mt-6 p-6 bg-emerald-50 rounded-2xl border border-emerald-100">
                        <p class="text-emerald-800 font-bold mb-2"><i class="fa-solid fa-circle-check mr-2"></i> Đáp án: ${q.answer}</p>
                        <p class="text-emerald-600 text-sm leading-relaxed">${q.explanation || ''}</p>
                    </div>
                </div>
            </div>`;
        }

        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('-translate-x-full'); }
        function toggleNotes() { document.getElementById('noteSidebar').classList.toggle('open'); }
        function switchTab(tab) {
            document.querySelectorAll('[id^="content-"]').forEach(c => c.classList.add('hidden'));
            document.getElementById('content-' + tab).classList.remove('hidden');
            document.querySelectorAll('[id^="tab-"]').forEach(t => t.className = "py-4 text-slate-400 hover:text-indigo-600 font-bold text-sm uppercase tracking-wider transition-colors whitespace-nowrap");
            document.getElementById('tab-' + tab).className = "py-4 text-indigo-700 border-b-4 border-indigo-600 font-black text-sm uppercase tracking-wider whitespace-nowrap";
        }

        function gradeTest() {
            testData.questions.forEach(q => {
                const block = document.getElementById('q-block-' + q.id);
                const expl = document.getElementById('explanation-' + q.id);
                if (expl) expl.classList.remove('hidden');
            });
            document.getElementById('resultArea').classList.remove('hidden');
            document.getElementById('scoreDisplay').textContent = "Đã Chấm Xong";
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
        }

        function updateFlashcardView() {
            const v = vocabList[currentVocabIndex];
            if(!v) return;
            document.getElementById('fc-word').textContent = v.word;
            document.getElementById('fc-pron').textContent = v.pron || '';
            document.getElementById('fc-type').textContent = v.type || 'Word';
            document.getElementById('fc-meaning').textContent = v.meaning || '';
            document.getElementById('fc-example').textContent = v.example || '';
            document.getElementById('fc-counter').textContent = `${currentVocabIndex + 1} / ${vocabList.length}`;
        }
        function nextCard() { currentVocabIndex = (currentVocabIndex + 1) % vocabList.length; updateFlashcardView(); }
        function prevCard() { currentVocabIndex = (currentVocabIndex - 1 + vocabList.length) % vocabList.length; updateFlashcardView(); }

        function showVocabTooltip(word, event) {
            const v = vocabList.find(i => i.word.toLowerCase() === word.toLowerCase());
            if(!v) return;
            const tt = document.getElementById('vocabTooltip');
            document.getElementById('tt-word').textContent = v.word;
            document.getElementById('tt-pron').textContent = v.pron || '';
            document.getElementById('tt-meaning').textContent = v.meaning || '';
            document.getElementById('tt-example').textContent = v.example || '';
            tt.style.left = Math.min(event.pageX, window.innerWidth - 350) + 'px';
            tt.style.top = (event.pageY + 20) + 'px';
            tt.classList.remove('hidden');
            setTimeout(() => tt.style.opacity = '1', 10);
        }
        
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.vocab-highlight') && !e.target.closest('#vocabTooltip')) {
                document.getElementById('vocabTooltip').classList.add('hidden');
                document.getElementById('vocabTooltip').style.opacity = '0';
            }
        });

        function speakWord() {
            const word = document.getElementById('tt-word').textContent;
            const msg = new SpeechSynthesisUtterance(word);
            msg.lang = 'en-US';
            window.speechSynthesis.speak(msg);
        }

        window.onload = () => {
            document.getElementById('qCountDisplay').textContent = testData.questions.length;
            renderQuestions();
            updateFlashcardView();
        };
    </script>
</body>
</html>"""
    
    # Replacement
    html_content = template.replace("{{EXAM_ID}}", str(exam_id))
    html_content = html_content.replace("{{JSON_DATA}}", json.dumps(data, ensure_ascii=False))
    html_content = html_content.replace("{{SIDEBAR_LINKS}}", sidebar_links)
    
    with open(os.path.join(OUTPUT_DIR, f'de_{exam_id}.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Successfully generated de_{exam_id}.html")

if __name__ == "__main__":
    for i in range(1, 31):
        generate_html(i)
