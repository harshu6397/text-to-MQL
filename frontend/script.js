// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const queryInput = document.getElementById('queryInput');
const submitBtn = document.getElementById('submitBtn');
const buttonText = document.getElementById('buttonText');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');

// Result elements
const formattedAnswer = document.getElementById('formattedAnswer');
const generatedQuery = document.getElementById('generatedQuery');
const rawResults = document.getElementById('rawResults');
const workflowSteps = document.getElementById('workflowSteps');
const executionTime = document.getElementById('executionTime');
const collectionsFound = document.getElementById('collectionsFound');
const schemasRetrieved = document.getElementById('schemasRetrieved');
const errorMessage = document.getElementById('errorMessage');

// Demo query buttons
const demoButtons = document.querySelectorAll('.demo-btn');

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Add click listeners to demo buttons
    demoButtons.forEach(button => {
        button.addEventListener('click', function() {
            const query = this.getAttribute('data-query');
            queryInput.value = query;
            
            // Scroll to input
            queryInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Focus and submit
            queryInput.focus();
            setTimeout(() => submitQuery(), 300);
        });
    });

    // Add enter key listener to textarea
    queryInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            submitQuery();
        }
    });
});

// Submit query function
async function submitQuery() {
    const query = queryInput.value.trim();
    
    if (!query) {
        alert('Please enter a question!');
        return;
    }

    // Show loading state
    setLoadingState(true);
    hideResults();

    try {
        const response = await fetch(`${API_BASE_URL}/api/structured/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            displayError(data.error || 'Query failed');
        }

    } catch (error) {
        console.error('Error:', error);
        displayError(`Failed to connect to API: ${error.message}`);
    } finally {
        setLoadingState(false);
    }
}

// Set loading state
function setLoadingState(isLoading) {
    submitBtn.disabled = isLoading;
    
    if (isLoading) {
        buttonText.style.display = 'none';
        loadingSpinner.style.display = 'block';
    } else {
        buttonText.style.display = 'block';
        loadingSpinner.style.display = 'none';
    }
}

// Display results
function displayResults(data) {
    hideError();
    
    // Natural language answer
    formattedAnswer.textContent = data.formatted_answer || 'No formatted answer available';
    
    // Generated query
    generatedQuery.textContent = data.generated_mql || 'No query generated';
    
    // Raw results
    rawResults.textContent = JSON.stringify(data.results, null, 2);
    
    // Workflow steps
    displayWorkflowSteps(data.workflow_steps || []);
    
    // Execution info
    executionTime.textContent = `${(data.execution_time || 0).toFixed(2)}s`;
    collectionsFound.textContent = data.collections_found || 0;
    schemasRetrieved.textContent = data.schema_retrieved || 0;
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Display workflow steps
function displayWorkflowSteps(steps) {
    workflowSteps.innerHTML = '';
    
    steps.forEach(step => {
        const stepElement = document.createElement('div');
        stepElement.className = `workflow-step ${step.status}`;
        
        const icon = getStatusIcon(step.status);
        stepElement.innerHTML = `${icon} ${step.step}`;
        
        workflowSteps.appendChild(stepElement);
    });
}

// Get status icon
function getStatusIcon(status) {
    switch (status) {
        case 'success':
            return '✅';
        case 'failed':
            return '❌';
        case 'pending':
            return '⏳';
        default:
            return '⚪';
    }
}

// Display error
function displayError(message) {
    hideResults();
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    
    // Scroll to error
    errorSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Hide results
function hideResults() {
    resultsSection.style.display = 'none';
}

// Hide error
function hideError() {
    errorSection.style.display = 'none';
}

// Demo queries data (for reference)
const demoQueries = {
    students: [
        "How many students are enrolled in total?",
        "What is the average GPA of all students?",
        "List all students in Computer Science department",
        "How many students are in their final year?",
        "Show me students with GPA above 3.5"
    ],
    departments: [
        "How many departments do we have?",
        "What are the names of all departments?",
        "Which department was established first?",
        "Show me all department heads",
        "List departments with their descriptions"
    ],
    courses: [
        "How many courses are offered this semester?",
        "Which course has most students enrolled?, give me the course name and number of students enrolled",
        "What courses have 3 or more credits?",
        "Show me all Spring semester courses",
        "Which courses are taught by Professor Smith?"
    ],
    teachers: [
        "How many teachers work at the university?",
        "List all teachers in Physics department",
        "What is the average salary of teachers?",
        "Show me teachers hired after 2020",
        "Who are the highest paid teachers?"
    ]
};

// Additional utility functions
function formatJSON(obj) {
    return JSON.stringify(obj, null, 2);
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Could add a toast notification here
        console.log('Copied to clipboard');
    });
}

// Add some interactive features
document.addEventListener('click', function(e) {
    // Add click-to-copy functionality for code blocks
    if (e.target.classList.contains('code-block')) {
        copyToClipboard(e.target.textContent);
        
        // Visual feedback
        const originalBg = e.target.style.backgroundColor;
        e.target.style.backgroundColor = '#4facfe';
        setTimeout(() => {
            e.target.style.backgroundColor = originalBg;
        }, 200);
    }
});

// Performance monitoring
function logPerformance(data) {
    console.log('Query Performance:', {
        execution_time: data.execution_time,
        collections_found: data.collections_found,
        schema_retrieved: data.schema_retrieved,
        workflow_steps: data.workflow_steps?.length || 0
    });
}

// Auto-save query history (optional feature)
function saveQueryHistory(query, result) {
    const history = JSON.parse(localStorage.getItem('queryHistory') || '[]');
    history.push({
        timestamp: new Date().toISOString(),
        query: query,
        success: result.success,
        execution_time: result.execution_time
    });
    
    // Keep only last 50 queries
    if (history.length > 50) {
        history.shift();
    }
    
    localStorage.setItem('queryHistory', JSON.stringify(history));
}
