document.addEventListener("DOMContentLoaded", function () {
    setupJournalFlow();
    setupToggleNotes();
});

// ✅ Global object to persist selections
let journalData = {
    painLevel: "No Pain 😃",
    energyLevel: "Excellent – no fatigue 😃",
    breath: "None",
    chestPain: "No Pain 😃",
    physicalActivity: "None",
    stressLevel: "No stress 😃",
    swelling: "No swelling 🦶",
    emergency: "None",
    extraNote: ""
};

// ✅ Toggle functionality for the global text box
function setupToggleNotes() {
    const toggleButton = document.getElementById("toggleNotes");
    const extraNoteBox = document.getElementById("extraNote");

    toggleButton.addEventListener("click", function () {
        extraNoteBox.style.display = extraNoteBox.style.display === "block" ? "none" : "block";
        if (extraNoteBox.style.display === "block") {
            extraNoteBox.focus();
        }
    });
}

// ✅ Function to handle question navigation and form submission
function setupJournalFlow() {
    const questions = [
        `<p>Pain Level</p>
        <input type="range" min="0" max="10" value="0" class="ph-scale" id="painLevel" name="painLevel" oninput="updateValue(this)">
        <p class="slider-value" id="painLevel-value">No Pain 😃</p>`,

        `<p>Energy Levels</p>
        <input type="range" min="0" max="3" value="0" class="ph-scale" id="energyLevel" name="energyLevel" oninput="updateValue(this)">
        <p class="slider-value" id="energyLevel-value">Excellent – no fatigue 😃</p>`,

        `<p>Did you experience shortness of breath today?</p>
        <div class="button-group" data-question="breath">
            <button type="button" class="option-button" onclick="selectOption('breath', 'No, not at all', this)">No, not at all</button>
            <button type="button" class="option-button" onclick="selectOption('breath', 'Yes, during strenuous activity', this)">Strenuous activity</button>
            <button type="button" class="option-button" onclick="selectOption('breath', 'Yes, during mild activity', this)">Mild activity</button>
            <button type="button" class="option-button" onclick="selectOption('breath', 'Yes, even at rest', this)">Even at rest</button>
        </div>
        <p class="selected-value" id="breath-value">Selected: None</p>`,

        `<p>Did you experience chest pain or discomfort today?</p>
        <input type="range" min="0" max="3" value="0" class="ph-scale" id="chestPain" name="chestPain" oninput="updateValue(this)">
        <p class="slider-value" id="chestPain-value">No Pain 😃</p>`,

        `<p>How much physical activity were you able to do today?</p>
        <div class="button-group" data-question="physicalActivity">
            <button type="button" class="option-button" onclick="selectOption('physicalActivity', 'More than usual', this)">More than usual</button>
            <button type="button" class="option-button" onclick="selectOption('physicalActivity', 'As much as usual', this)">As much as usual</button>
            <button type="button" class="option-button" onclick="selectOption('physicalActivity', 'Less than usual', this)">Less than usual</button>
            <button type="button" class="option-button" onclick="selectOption('physicalActivity', 'None', this)">None</button>
        </div>
        <p class="selected-value" id="physicalActivity-value">Selected: None</p>`,

        `<p>How would you describe your stress levels today?</p>
        <input type="range" min="0" max="3" value="0" class="ph-scale" id="stressLevel" name="stressLevel" oninput="updateValue(this)">
        <p class="slider-value" id="stressLevel-value">No stress 😃</p>`,

        `<p>Did you notice swelling in your feet or ankles today?</p>
        <input type="range" min="0" max="3" value="0" class="ph-scale" id="swelling" name="swelling" oninput="updateValue(this)">
        <p class="slider-value" id="swelling-value">No swelling 🦶</p>`,

        `<p>Did you experience any emergency symptoms requiring immediate attention?</p>
        <div class="button-group" data-question="emergency">
            <button type="button" class="option-button" onclick="selectOption('emergency', 'No', this)">No</button>
            <button type="button" class="option-button" onclick="selectOption('emergency', 'Mild, manageable at home', this)">Mild, manageable at home</button>
            <button type="button" class="option-button" onclick="selectOption('emergency', 'Moderate, resolved with rest', this)">Moderate, resolved with rest</button>
            <button type="button" class="option-button" onclick="selectOption('emergency', 'Severe, required attention', this)">Severe, required attention</button>
        </div>
        <p class="selected-value" id="emergency-value">Selected: None</p>`
    ];

    let currentQuestionIndex = 0;
    const questionContainer = document.getElementById("question-container");
    const nextButton = document.getElementById("nextButton");
    const prevButton = document.getElementById("prevButton"); // New Previous button
    const progressBar = document.getElementById("progressBar");
    const form = document.getElementById("journalForm");
    const extraNoteBox = document.getElementById("extraNote");

    function loadQuestion(index) {
        questionContainer.classList.remove("active");
        setTimeout(() => {
            questionContainer.innerHTML = questions[index];
            questionContainer.classList.add("active");
            progressBar.style.width = `${((index + 1) / questions.length) * 100}%`;
            nextButton.textContent = index === questions.length - 1 ? "Submit" : "Next";
            // Show Previous button only if not on the first question
            prevButton.style.display = index === 0 ? "none" : "inline-block";
            setupSliders();
        }, 300);
    }

    nextButton.addEventListener("click", function (event) {
        if (currentQuestionIndex < questions.length - 1) {
            currentQuestionIndex++;
            loadQuestion(currentQuestionIndex);
        } else {
            event.preventDefault();
            journalData["extraNote"] = extraNoteBox.value; // ✅ Include the extra note
            captureAllValues();
            form.submit();
        }
    });

    // New event listener for the Previous button
    prevButton.addEventListener("click", function () {
        if (currentQuestionIndex > 0) {
            currentQuestionIndex--;
            loadQuestion(currentQuestionIndex);
        }
    });

    loadQuestion(currentQuestionIndex);
}


// ✅ Store slider & MCQ values globally before form submission
function captureAllValues() {
    document.querySelectorAll("input[type=range]").forEach(slider => {
        const id = slider.id;
        const displayElement = document.getElementById(id + "-value");
        if (displayElement) journalData[id] = displayElement.innerText;
    });

    Object.keys(journalData).forEach((key) => {
        let hiddenField = document.createElement("input");
        hiddenField.type = "hidden";
        hiddenField.name = key;
        hiddenField.value = journalData[key];
        document.getElementById("journalForm").appendChild(hiddenField);
    });
}

// ✅ Dynamic slider descriptions
const descriptions = {
    painLevel: ["No Pain 😃", "Very Mild Pain 🙂", "Mild Pain 🙂", "Discomfort 😐",
        "Moderate Pain 😣", "Uncomfortable 😖", "Severe Pain 😢",
        "Very Severe Pain 😭", "Intense Pain 💀", "Extreme Pain 💀💀", "Worst Possible Pain 💀💀💀"
    ],
    energyLevel: ["Excellent – no fatigue 😃", "Good – mild fatigue 🙂", "Fair – moderate fatigue 😐", "Poor – severe fatigue 😞"],
    chestPain: ["No Pain 😃", "Mild discomfort 🙂", "Moderate pain 😣", "Severe pain 😖"],
    stressLevel: ["No stress 😃", "Mild stress 🙂", "Moderate stress 😐", "High stress 😖"],
    swelling: ["No swelling 🦶", "Mild swelling 🦶", "Moderate swelling 🦶", "Severe swelling 🦶"]
};

function updateValue(slider) {
    const id = slider.id;
    const value = parseInt(slider.value);
    if (descriptions[id]) {
        const displayElement = document.getElementById(id + "-value");
        displayElement.innerText = descriptions[id][value] || "Unknown";
        journalData[id] = descriptions[id][value];
    }
}

function selectOption(question, value, buttonElement) {
    document.querySelectorAll(`.button-group[data-question="${question}"] button`).forEach(btn => {
        btn.classList.remove("selected");
    });
    buttonElement.classList.add("selected");
    document.getElementById(question + "-value").innerText = "Selected: " + value;
    journalData[question] = value;
}

// ✅ Toggle functionality for the Personal Log
function setupToggleNotes() {
    const toggleButton = document.getElementById("toggleNotes");
    const extraNoteBox = document.getElementById("extraNote");

    toggleButton.addEventListener("click", function () {
        extraNoteBox.style.display = extraNoteBox.style.display === "block" ? "none" : "block";
        if (extraNoteBox.style.display === "block") {
            extraNoteBox.focus();
        }
    });
}