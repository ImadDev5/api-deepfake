// AWS Configuration
const AWS_CONFIG = {
    region: 'ap-south-1',
    cognito: {
        identityPoolId: 'ap-south-1:b5fbd414-5359-4da4-a422-63a74ed74e67',
        userPoolId: 'ap-south-1_KNfnHmJTs',
        userPoolWebClientId: '3taegk45pcnuf8n05jeooqbnm8'
    }
};

// Initialize AWS Amplify
window.aws_amplify.Amplify.configure({
    Auth: {
        identityPoolId: AWS_CONFIG.cognito.identityPoolId,
        userPoolId: AWS_CONFIG.cognito.userPoolId,
        userPoolWebClientId: AWS_CONFIG.cognito.userPoolWebClientId,
        region: AWS_CONFIG.region
    }
});

// Helper function to display alerts
function showAlert(message) {
    const alertBox = document.createElement('div');
    alertBox.className = 'alert';
    alertBox.textContent = message;
    document.body.appendChild(alertBox);
    setTimeout(() => alertBox.remove(), 3000);
}

// Initialize Liveness Check
async function startLivenessCheck() {
    try {
        // Fetch session ID from backend
        const sessionResponse = await fetch('/api/create-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!sessionResponse.ok) {
            throw new Error('Failed to create session');
        }
        const { session_id } = await sessionResponse.json();

        // Initialize FaceLivenessDetector
        const livenessDetector = new window.aws_amplify.FaceLivenessDetector({
            sessionId: session_id,
            region: AWS_CONFIG.region,
            onAnalysisComplete: async () => {
                const result = await verifySession(session_id);
                document.getElementById('result-text').innerHTML =
                    `Result: ${result.is_live ? '✅ LIVE' : '❌ FAKE'} | Confidence: ${result.confidence}%`;
            }
        });

        // Mount liveness detector
        livenessDetector.mount(document.getElementById('liveness-container'));
    } catch (error) {
        console.error('Liveness initialization failed:', error);
        showAlert('Error initializing liveness check');
    }
}

// Verify Session
async function verifySession(sessionId) {
    try {
        const response = await fetch('/api/verify-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
        if (!response.ok) {
            throw new Error('Session verification failed');
        }
        return await response.json();
    } catch (error) {
        console.error('Session verification failed:', error);
        showAlert('Error verifying session');
        return { is_live: false, confidence: 0 };
    }
}

// Submit Feedback
document.getElementById('report-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const userId = document.getElementById('user_id').value;
    const description = document.getElementById('description').value;

    try {
        const response = await fetch('/api/submit-feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, description: description })
        });
        const result = await response.json();
        alert(result.message);
    } catch (error) {
        console.error('Feedback submission failed:', error);
        alert('Error submitting feedback');
    }
});

// Initialize on page load
window.addEventListener('load', async () => {
    startLivenessCheck();
});