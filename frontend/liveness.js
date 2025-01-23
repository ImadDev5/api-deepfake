// Configuration (UPDATE THESE VALUES!)
const AWS_CONFIG = {
    region: 'ap-south-1', // Mumbai
    cognito: {
        identityPoolId: 'YOUR_COGNITO_IDENTITY_POOL_ID', // From Cognito Identity Pool
        userPoolId: 'ap-south-1_KNfnHmJTs', // Your User Pool ID
        userPoolWebClientId: '3taegk45pcnuf8n05jeooqbnm8' // Your App Client ID
    },
    s3: {
        bucketName: 'voice-fraud-detection1' // Your created bucket
    }
};

// Initialize Amplify
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

async function startLivenessCheck() {
    try {
        const sessionResponse = await fetch('/api/create-session');
        const { session_id } = await sessionResponse.json();
        
        livenessDetector = new window.aws_amplify.FaceLivenessDetector({
            sessionId: session_id,
            region: AWS_CONFIG.region,
            onAnalysisComplete: async () => {
                const result = await verifySession(session_id);
                alert(`Result: ${result.is_live ? 'LIVE ✅' : 'FAKE ❌'}\nConfidence: ${result.confidence}%`);
            }
        });
        
        livenessDetector.mount(document.getElementById('liveness-container'));
    } catch (error) {
        console.error('Liveness failed:', error);
        alert('Liveness check error! Check console');
    }
}

async function verifySession(sessionId) {
    const response = await fetch('/api/verify-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
    });
    return await response.json();
}

// Init
window.addEventListener('load', async () => {
    await initializeAuth();
    startLivenessCheck();
    
    document.getElementById('signOut').addEventListener('click', async () => {
        await window.aws_amplify.Auth.signOut();
        window.location.reload();
    });
});