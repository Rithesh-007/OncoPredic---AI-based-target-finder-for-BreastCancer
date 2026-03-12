const API_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? (window.location.port === "5000" ? "/api" : "http://127.0.0.1:5000/api")
    : "/api";
let scoreChart = null;
let allResults = []; // Global storage for full dataset

// DOM Elements
const resultsTable = document.getElementById("results-table").getElementsByTagName("tbody")[0];
const loader = document.getElementById("loader");
const backendStatus = document.getElementById("backend-status");
const statusText = document.getElementById("status-text");
const exportBtn = document.getElementById("export-csv");
const clearBtn = document.getElementById("clear-results");

// Page switching elements
const pageUpload = document.getElementById("page-upload");
const pageDashboard = document.getElementById("page-dashboard");
const backBtn = document.getElementById("back-btn");

function showDashboard() {
    if (pageUpload && pageDashboard) {
        pageUpload.classList.add("hidden");
        pageUpload.classList.remove("active");
        pageDashboard.classList.remove("hidden");
        pageDashboard.classList.add("active");
        document.body.classList.remove("upload-active");
        document.body.classList.add("dashboard-active");
    }
}

function showUpload() {
    if (pageUpload && pageDashboard) {
        pageDashboard.classList.add("hidden");
        pageDashboard.classList.remove("active");
        pageUpload.classList.remove("hidden");
        pageUpload.classList.add("active");
        document.body.classList.remove("dashboard-active");
        document.body.classList.add("upload-active");
    }
}

// Initial Status Check
async function checkHealth() {
    try {
        const response = await fetch(`${API_URL}/top-targets`);
        if (response.ok) {
            backendStatus.classList.add("online");
            statusText.innerText = "System Online";
            loadInitialData();
        }
    } catch (err) {
        statusText.innerText = "System Offline - Start Server";
    }
}

// Load top targets on start
async function loadInitialData() {
    try {
        const response = await fetch(`${API_URL}/top-targets`);
        const data = await response.json();
        
        if (data && data.length > 0) {
            allResults = data;
            // updateUI(data); // Pre-load in background optionally, but don't force show
        }
    } catch (err) {
        console.error("Scale check failed", err);
    }
}

function updateUI(data) {
    if (!resultsTable) return;
    resultsTable.innerHTML = "";

    const displayTable = data.slice(0, 100);

    displayTable.forEach((item, index) => {
        const row = resultsTable.insertRow();
        const score = parseFloat(item.target_score || 0).toFixed(4);
        const hr = parseFloat(item.hazard_ratio || 0).toFixed(2);
        const fdr = parseFloat(item.fdr || 0).toExponential(2);

        const isHigh = item.hazard_ratio > 1;

        row.style.animationDelay = `${Math.min(index, 20) * 0.05}s`;

        row.innerHTML = `
            <td><strong>${item.gene}</strong></td>
            <td class="target-score-val">${score}</td>
            <td>${hr}</td>
            <td>${fdr}</td>
            <td><span class="type-tag ${isHigh ? 'high' : 'low'}">${item.risk_type}</span></td>
        `;
    });

    if (data.length > 100) {
        const row = resultsTable.insertRow();
        row.innerHTML = `<td colspan="5" style="text-align:center; padding: 20px; color: #94a3b8; font-style: italic;">
            Showing Top 100 of ${data.length} results. Use 'Export' for the full list.
        </td>`;
    }

    updateChart(data);
}

function updateChart(data) {
    const chartEl = document.getElementById('scoreChart');
    if (!chartEl) return;
    const ctx = chartEl.getContext('2d');

    const displayData = data.slice(0, 30);
    const labels = displayData.map(i => i.gene);
    const scores = displayData.map(i => i.target_score);
    const colors = displayData.map(i => i.hazard_ratio > 1 ? '#ef4444' : '#10b981');

    if (scoreChart) {
        scoreChart.destroy();
    }

    scoreChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Prediction Target Score',
                data: scores,
                backgroundColor: colors,
                borderRadius: 8,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            },
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
}

// Export functionality
if (exportBtn) {
    exportBtn.addEventListener("click", () => {
        if (allResults.length === 0) return;

        const headers = ["Gene", "Target Score", "Risk Type", "Hazard Ratio", "FDR"];
        const csvContent = [
            headers.join(","),
            ...allResults.map(r => [
                r.gene,
                r.target_score,
                r.risk_type,
                r.hazard_ratio,
                r.fdr
            ].join(","))
        ].join("\n");

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.setAttribute('hidden', '');
        a.setAttribute('href', url);
        a.setAttribute('download', 'prioritized_targets.csv');
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    });
}

// Clear results
if (clearBtn) {
    clearBtn.addEventListener("click", () => {
        allResults = [];
        resultsTable.innerHTML = `<tr class="empty-row"><td colspan="5">Upload a gene list to see results...</td></tr>`;
        if (scoreChart) scoreChart.destroy();
        const fileInput = document.getElementById("gene-file");
        const info = document.getElementById("file-info");
        if (fileInput) fileInput.value = "";
        if (info) info.classList.add("hidden");
    });
}

// Bulk Upload Action
const uploadBtn = document.getElementById("upload-btn");
const geneFile = document.getElementById("gene-file");
const dropArea = document.getElementById("drop-area");
const fileInfo = document.getElementById("file-info");
const selectedFileName = document.getElementById("selected-file-name");
const removeFileBtn = document.getElementById("remove-file-btn");

function showFileSelected(file) {
    if (file) {
        selectedFileName.innerText = file.name;
        fileInfo.classList.remove("hidden");
        dropArea.classList.add("hidden"); // Hide drop area when file is selected
    }
}

function clearFileSelection() {
    geneFile.value = "";
    fileInfo.classList.add("hidden");
    dropArea.classList.remove("hidden"); // Show drop area back
}

if (uploadBtn && geneFile) {
    // File Selection Click
    dropArea.addEventListener("click", () => geneFile.click());

    // File Input Change
    geneFile.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) showFileSelected(file);
    });

    // Drag & Drop support
    dropArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropArea.classList.add("dragging");
    });

    dropArea.addEventListener("dragleave", () => {
        dropArea.classList.remove("dragging");
    });

    dropArea.addEventListener("drop", (e) => {
        e.preventDefault();
        dropArea.classList.remove("dragging");
        const file = e.dataTransfer.files[0];
        if (file && file.name.endsWith('.txt')) {
            geneFile.files = e.dataTransfer.files;
            showFileSelected(file);
        } else {
            alert("Please drop a .txt file.");
        }
    });

    // Remove file logic
    if (removeFileBtn) {
        removeFileBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            clearFileSelection();
        });
    }

    uploadBtn.addEventListener("click", async () => {
        const file = geneFile.files[0];
        if (!file) {
            alert("Please select a .txt file first.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        loader.classList.remove("hidden");

        try {
            const response = await fetch(`${API_URL}/upload-genes`, {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.error || `Server returned ${response.status}`);
            }

            const data = await response.json();
            if (data.length === 0) {
                alert("None of the genes in the file were found in our database.");
            } else {
                allResults = data;
                updateUI(data);
                showDashboard(); // Transition to the dashboard page upon success
            }
        } catch (err) {
            console.error("Upload Error:", err);
            alert(`Upload failed: ${err.message}`);
        } finally {
            loader.classList.add("hidden");
        }
    });
}

// Back Button Navigation
if (backBtn) {
    backBtn.addEventListener("click", () => {
        showUpload();
        // Optionally clear the previous selection via clearFileSelection()
        // clearFileSelection();
    });
}

checkHealth();
