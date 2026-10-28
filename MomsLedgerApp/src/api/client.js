import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const apiClient = axios.create({
    baseURL: 'http://YOUR_BACKEND_IP:8000/api/', 
    timeout: 10000,
});

// Request Interceptor: Attach Token
apiClient.interceptors.request.use(
    async (config) => {
        const token = await SecureStore.getItemAsync('user_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401 (Unauthorized)
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response && error.response.status === 401) {
            // Logic to trigger logout or refresh token would go here
            console.log("Session expired. Redirecting to login...");
        }
        return Promise.reject(error);
    }
);

export default apiClient;
