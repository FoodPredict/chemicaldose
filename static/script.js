
document.addEventListener('DOMContentLoaded', function() {
    const langButtons = document.querySelectorAll('.lang-button');
    const cropSelect = document.getElementById('crop-type');
    const pestDiseaseSelect = document.getElementById('pest-disease');
    const areaInput = document.getElementById('area');
    const areaUnitSelect = document.getElementById('area-unit');
    const outputUnitSelect = document.getElementById('output-unit');
    const calculateBtn = document.getElementById('calculate-btn');
    const chemicalNameSpan = document.getElementById('chemical-name');
    const calculatedDoseSpan = document.getElementById('calculated-dose');
    const doseUnitSpan = document.getElementById('dose-unit');
    const sourceSpan = document.getElementById('source');
    const errorMessagePara = document.getElementById('error-message');

    let currentLang = 'en'; // Default language

    const textElements = {
        'app-title': { 'en': 'Pesticide and Insecticide Dose Calculator', 'hi': 'कीटनाशक और कीटनाशक खुराक कैलकुलेटर' },
        'input-heading': { 'en': 'Input', 'hi': 'इनपुट' },
        'output-heading': { 'en': 'Output', 'hi': 'आउटपुट' },
        'crop-label': { 'en': 'Crop Type:', 'hi': 'फसल का प्रकार:' },
        'pest-disease-label': { 'en': 'Disease/Pest:', 'hi': 'रोग/कीट:' },
        'area-label': { 'en': 'Area:', 'hi': 'क्षेत्र:' },
        'area-unit-label': { 'en': 'Area Unit:', 'hi': 'क्षेत्र इकाई:' },
        'output-unit-label': { 'en': 'Desired Output Unit:', 'hi': 'वांछित आउटपुट इकाई:' },
        'calculate-button': { 'en': 'Calculate', 'hi': 'गणना करें' },
        'chemical-label': { 'en': 'Recommended Chemical:', 'hi': 'अनुशंसित रसायन:' },
        'dose-label': { 'en': 'Calculated Dose:', 'hi': 'गणना की गई खुराक:' },
        'source-label': { 'en': 'Source:', 'hi': 'स्रोत:' },
        'select-crop-option': { 'en': 'Select Crop', 'hi': 'फसल चुनें' },
        'select-pest-disease-option': { 'en': 'Select Disease/Pest', 'hi': 'रोग/कीट चुनें' },
        'acres-option': { 'en': 'Acres', 'hi': 'एकड़' },
        'hectares-option': { 'en': 'Hectares', 'hi': 'हेक्टेयर' }
        // Add more text elements as needed
    };

    function updateTextContent() {
        document.querySelector('header h1').textContent = textElements['app-title'][currentLang];
        document.querySelector('.input-section h2').textContent = textElements['input-heading'][currentLang];
        document.querySelector('.output-section h2').textContent = textElements['output-heading'][currentLang];
        document.querySelector('label[for="crop-type"]').textContent = textElements['crop-label'][currentLang];
        document.querySelector('label[for="pest-disease"]').textContent = textElements['pest-disease-label'][currentLang];
        document.querySelector('label[for="area"]').textContent = textElements['area-label'][currentLang];
        document.querySelector('label[for="area-unit"]').textContent = textElements['area-unit-label'][currentLang];
        document.querySelector('label[for="output-unit"]').textContent = textElements['output-unit-label'][currentLang];
        calculateBtn.textContent = textElements['calculate-button'][currentLang];
        document.querySelector('#results p:nth-of-type(1) strong').textContent = textElements['chemical-label'][currentLang];
        document.querySelector('#results p:nth-of-type(2) strong').textContent = textElements['dose-label'][currentLang];
        document.querySelector('#results p:nth-of-type(3) strong').textContent = textElements['source-label'][currentLang];

        // Update dropdown options
        populateCropDropdown(); // Repopulate to update language
        // Pest/Disease dropdown will be updated when a crop is selected
        updateAreaUnitOptions();
        updateOutputUnitOptions(); // Assuming output units don't need translation for now
    }

    function updateAreaUnitOptions() {
        const options = areaUnitSelect.options;
        for (let i = 0; i < options.length; i++) {
            if (options[i].value === 'acres') {
                options[i].textContent = textElements['acres-option'][currentLang];
            } else if (options[i].value === 'hectares') {
                options[i].textContent = textElements['hectares-option'][currentLang];
            }
        }
    }

    function updateOutputUnitOptions() {
        // Assuming output units like g/acre, ml/liter are standard and don't need translation
        // If translation is needed, add them to textElements and update here
    }


    langButtons.forEach(button => {
        button.addEventListener('click', function() {
            langButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            currentLang = this.id.replace('lang-', '');
            updateTextContent();
            // Trigger crop selection change to repopulate pest/disease dropdown in the new language
            const selectedCrop = cropSelect.value;
             if (selectedCrop) {
                fetchPestsDiseases(selectedCrop);
            } else {
                pestDiseaseSelect.innerHTML = `<option value="">${textElements['select-pest-disease-option'][currentLang]}</option>`;
            }
        });
    });

    function populateCropDropdown() {
        fetch('/get_crops')
            .then(response => response.json())
            .then(data => {
                cropSelect.innerHTML = `<option value="">${textElements['select-crop-option'][currentLang]}</option>`; // Clear and add default
                data.forEach(crop => {
                    const option = document.createElement('option');
                    option.value = crop.name_en; // Use English name for value to query backend
                    option.textContent = (currentLang === 'en' ? crop.name_en : crop.name_hi);
                    cropSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error fetching crops:', error);
                errorMessagePara.textContent = 'Error fetching crop data.';
            });
    }

    function fetchPestsDiseases(selectedCrop_en) {
         fetch(`/get_pests_diseases?crop_en=${selectedCrop_en}`)
            .then(response => response.json())
            .then(data => {
                pestDiseaseSelect.innerHTML = `<option value="">${textElements['select-pest-disease-option'][currentLang]}</option>`; // Clear and add default
                data.forEach(pd => {
                    const option = document.createElement('option');
                    option.value = pd.name_en; // Use English name for value
                    option.textContent = (currentLang === 'en' ? pd.name_en : pd.name_hi);
                    pestDiseaseSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error fetching pests/diseases:', error);
                errorMessagePara.textContent = 'Error fetching pest/disease data.';
            });
    }

    cropSelect.addEventListener('change', function() {
        const selectedCrop_en = this.value;
        if (selectedCrop_en) {
            fetchPestsDiseases(selectedCrop_en);
        } else {
            pestDiseaseSelect.innerHTML = `<option value="">${textElements['select-pest-disease-option'][currentLang]}</option>`; // Clear if no crop selected
        }
    });

    calculateBtn.addEventListener('click', function() {
        const crop_en = cropSelect.value;
        const pest_disease_en = pestDiseaseSelect.value;
        const area = areaInput.value;
        const areaUnit = areaUnitSelect.value;
        const desiredOutputUnit = outputUnitSelect.value;

        // Clear previous results and errors
        chemicalNameSpan.textContent = '';
        calculatedDoseSpan.textContent = '';
        doseUnitSpan.textContent = '';
        sourceSpan.textContent = '';
        errorMessagePara.textContent = '';

        if (!crop_en || !pest_disease_en || !area) {
            errorMessagePara.textContent = "Please select a crop, disease/pest, and enter the area.";
            return;
        }

        fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                crop_en: crop_en,
                pest_disease_en: pest_disease_en,
                area: parseFloat(area),
                area_unit: areaUnit,
                desired_output_unit: desiredOutputUnit,
                language: currentLang
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                errorMessagePara.textContent = data.error;
            } else {
                chemicalNameSpan.textContent = data.chemical;
                calculatedDoseSpan.textContent = data.calculated_dose !== null ? data.calculated_dose.toFixed(2) : 'N/A'; // Format for display
                doseUnitSpan.textContent = data.unit;
                sourceSpan.textContent = data.source || 'N/A'; // Display N/A if no source
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            errorMessagePara.textContent = 'An error occurred during calculation.';
        });
    });

    // Initial population of crop dropdown and text content on page load
    updateTextContent();
    populateCropDropdown();
});
