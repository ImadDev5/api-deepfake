// Configuration
const AWS_CONFIG = {
    region: 'ap-south-1', // Mumbai
    cognito: {
        identityPoolId: 'YOUR_COGNITO_IDENTITY_POOL_ID', // Replace with your ID
        userPoolId: 'ap-south-1_KNfnHmJTs', // Replace with your User Pool ID
        userPoolWebClientId: '3taegk45pcnuf8n05jeooqbnm8' // Replace with your App Client ID
    },
    s3: {
        bucketName: 'voice-fraud-detection1' // Your S3 bucket
    }
};

// Alert System
const ALERT_TYPES = {
    DEEPFAKE: { color: '#ff4444', icon: '🎭', text: 'Deepfake Detected!' },
    PHISHING: { color: '#ffbb33', icon: '🎣', text: 'Phishing Attempt!' },
    TRANSACTION: { color: '#00C851', icon: '💰', text: 'Suspicious Transaction!' }
};

function showAlert(type) {
    const alertDiv = document.createElement('div');
    alertDiv.style = `position:fixed; top:20px; right:20px; padding:15px;
                     background:${ALERT_TYPES[type].color}; color:white;
                     border-radius:5px; z-index:1000;`;
    alertDiv.innerHTML = `${ALERT_TYPES[type].icon} ${ALERT_TYPES[type].text}`;
    
    document.body.appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 5000);
}

// Initialize AWS Amplify
window.aws_amplify.Amplify.configure({
    Auth: {
        identityPoolId: AWS_CONFIG.cognito.identityPoolId,
        userPoolId: AWS_CONFIG.cognito.userPoolId,
        userPoolWebClientId: AWS_CONFIG.cognito.userPoolWebClientId,
        region: AWS_CONFIG.region
    },
    Storage: {
        bucket: AWS_CONFIG.s3.bucketName,
        region: AWS_CONFIG.region
    }
});

let livenessDetector = null;

// Authentication
async function initializeAuth() {
    try {
        const user = await window.aws_amplify.Auth.currentAuthenticatedUser();
        document.getElementById('signOut').style.display = 'block';
        document.getElementById('userEmail').textContent = `Logged in as: ${user.attributes.email}`;
        return user;
    } catch (error) {
        window.location.href = '/login';
    }
}

// Liveness Check
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

// Verify Session
async function verifySession(sessionId) {
    const response = await fetch('/api/verify-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
    });
    return await response.json();
}

// Logout
async function signOut() {
    await window.aws_amplify.Auth.signOut();
    window.location.reload();
}

// Initialize on page load
window.addEventListener('load', async () => {
    await initializeAuth();
    startLivenessCheck();
    
    document.getElementById('signOut').addEventListener('click', signOut);
});