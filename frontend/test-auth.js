// Test authentication flow
async function testAuth() {
    console.log('Testing authentication flow...');
    
    try {
        // Step 1: Create test user
        console.log('1. Creating test user...');
        const createUserResponse = await fetch('http://localhost:8000/test/create-user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const createUserData = await createUserResponse.json();
        console.log('Create user result:', createUserData);
        
        if (createUserData.status === 'success') {
            // Step 2: Create JWT token
            console.log('2. Creating JWT token...');
            const createTokenResponse = await fetch('http://localhost:8000/test/create-token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const tokenData = await createTokenResponse.json();
            console.log('Token creation result:', tokenData);
            
            if (tokenData.status === 'success') {
                // Step 3: Store token in localStorage
                console.log('3. Storing token in localStorage...');
                localStorage.setItem('access_token', tokenData.access_token);
                localStorage.setItem('user', JSON.stringify({
                    id: tokenData.user_id,
                    email: tokenData.user_email,
                    full_name: 'Test User'
                }));
                
                console.log('Token stored:', tokenData.access_token);
                console.log('User stored:', JSON.parse(localStorage.getItem('user')));
                
                // Step 4: Test project creation
                console.log('4. Testing project creation...');
                const projectResponse = await fetch('http://localhost:8000/api/v1/projects', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${tokenData.access_token}`
                    },
                    body: JSON.stringify({
                        name: 'Test Project',
                        description: 'Test project description'
                    })
                });
                
                if (projectResponse.ok) {
                    const projectData = await projectResponse.json();
                    console.log('Project created successfully:', projectData);
                } else {
                    const errorData = await projectResponse.json();
                    console.error('Project creation failed:', errorData);
                }
            }
        }
    } catch (error) {
        console.error('Test failed:', error);
    }
}

// Run the test
testAuth();
