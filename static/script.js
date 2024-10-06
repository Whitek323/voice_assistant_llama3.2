// static/script.js

function uploadPDF() {
    const fileInput = document.getElementById('pdfFile');
    const file = fileInput.files[0];
    if (!file) {
        alert("Please select a PDF file to upload.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    fetch('/pdf', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const statusDiv = document.getElementById('uploadStatus');
        statusDiv.innerHTML = `File uploaded: ${data.filename}, Document Length: ${data.doc_len}, Chunks: ${data.chunks}`;
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function askQuestion() {
    const queryInput = document.getElementById('query');
    const query = queryInput.value;
    const askButton = document.getElementById('askButton');
    const micButton = document.getElementById('micButton');
    const loader = document.getElementById('loader');

    if (!query) {
        alert("กรุณาใส่คำถาม");
        return;
    }

    // แสดง loader และปิดการใช้งานปุ่ม
    loader.style.display = 'block';
    askButton.disabled = true;
    micButton.disabled = true;

    const requestBody = { query: query };

    fetch('/ask_pdf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
    })
    .then(response => response.json())
    .then(data => {
        const answerDiv = document.getElementById('answer');
        answerDiv.innerHTML = `คำตอบ: ${data.answer}`;

        // เรียกใช้ speak_answer
        return fetch('/speak_answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ answer: data.answer })
        });
    })
    .then(audioResponse => audioResponse.json())
    .then(audioData => {
        // เพิ่ม query string แบบสุ่มเพื่อหลีกเลี่ยงการ cache
        const audioUrl = audioData.audio_url + '?t=' + new Date().getTime();
        
        // สร้างและเล่นเสียงจาก URL
        const audio = new Audio(audioUrl);
        audio.play();
    })
    .catch(error => {
        console.error("เกิดข้อผิดพลาด:", error);
    })
    .finally(() => {
        // ซ่อน loader และเปิดใช้งานปุ่ม
        loader.style.display = 'none';
        askButton.disabled = false;
        micButton.disabled = false;
    });
}


// ตั้งค่า voice recognition ให้เป็นภาษาไทย
function startVoiceRecognition() {
    const queryInput = document.getElementById('query');
    const answerDiv = document.getElementById('answer');

    if ('webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'th-TH'; // ตั้งค่าให้เป็นภาษาไทย

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            queryInput.value = transcript;
            askQuestion(); // ส่งคำถามอัตโนมัติหลังจากพูด
        };

        recognition.onerror = function(event) {
            console.error("Error occurred in recognition: " + event.error);
        };

        recognition.start();
    } else {
        alert("ขออภัย เบราว์เซอร์ของคุณไม่รองรับการรู้จำเสียง");
    }
}
// Function to convert text to speech
function speakResponse(text) {
    const speech = new SpeechSynthesisUtterance(text); // Create a new SpeechSynthesisUtterance
    // speech.lang = 'en-US'; // Set language (optional)
    speech.lang = 'th-TH'; // ตั้งค่าภาษาเป็นไทย
    window.speechSynthesis.speak(speech); // Speak the text
}
