const AWS_CONFIG = {
    region: 'ap-south-1',
    cognito: {
        identityPoolId: process.env.COGNITO_IDENTITY_POOL_ID,
        userPoolId: process.env.COGNITO_USER_POOL_ID,
        userPoolWebClientId: process.env.COGNITO_CLIENT_ID
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

// WebSocket for real-time alerts
const ws = new WebSocket('ws://localhost:8000/realtime');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    showAlert(data.type);
};

// Initialize Liveness Check
async function startLivenessCheck() {
    try {
        const sessionResponse = await fetch('/api/create-session');
        const { session_id } = await sessionResponse.json();

        livenessDetector = new window.aws_amplify.FaceLivenessDetector({
            sessionId: session_id,
            region: AWS_CONFIG.region,
            onAnalysisComplete: async () => {
                const result = await verifySession(session_id);
                if (result.risk_score > 0.7) {
                    showAlert(result.is_live ? 'TRANSACTION' : 'DEEPFAKE');
                }
                document.getElementById('result-text').innerHTML =
                    `Result: ${result.is_live ? '✅ LIVE' : '❌ FAKE'} | Confidence: ${result.confidence}%`;
            }
        });

        livenessDetector.mount(document.getElementById('liveness-container'));
    } catch (error) {
        console.error('Liveness failed:', error);
        showAlert('DEEPFAKE');
    }
}

// Initialize on page load
window.addEventListener('load', async () => {
    await initializeAuth();
    startLivenessCheck();
});