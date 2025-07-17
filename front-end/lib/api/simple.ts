import { API_BASE_URL, ENDPOINTS } from './config';
import { User, TrafficData, HealthResponse } from './types';

// Helper function to make API calls easier
async function callAPI(url: string, options: any = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}

// ===== HEALTH CHECK =====
export async function checkHealth(): Promise<HealthResponse> {
  return callAPI(`${API_BASE_URL}${ENDPOINTS.HEALTH}`);
}

// ===== USER FUNCTIONS =====
export async function getUsers(): Promise<User[]> {
  return callAPI(`${API_BASE_URL}${ENDPOINTS.USERS}`);
}

export async function createUser(user: User) {
  return callAPI(`${API_BASE_URL}${ENDPOINTS.USERS}`, {
    method: 'POST',
    body: JSON.stringify(user),
  });
}

export async function getUser(userId: string): Promise<User> {
  return callAPI(`${API_BASE_URL}${ENDPOINTS.USERS}/${userId}`);
}

export async function updateUser(userId: string, userData: any) {
  return callAPI(`${API_BASE_URL}${ENDPOINTS.USERS}/${userId}`, {
    method: 'PUT',
    body: JSON.stringify(userData),
  });
}

export async function deleteUser(userId: string) {
  return callAPI(`${API_BASE_URL}${ENDPOINTS.USERS}/${userId}`, {
    method: 'DELETE',
  });
}

// ===== TRAFFIC FUNCTIONS =====
export async function getTrafficData(): Promise<TrafficData[]> {
  return callAPI(`${API_BASE_URL}${ENDPOINTS.TRAFFIC}`);
}

export async function createTrafficData(trafficData: TrafficData) {
  return callAPI(`${API_BASE_URL}${ENDPOINTS.TRAFFIC}`, {
    method: 'POST',
    body: JSON.stringify(trafficData),
  });
}

export async function getTrafficById(trafficId: string): Promise<TrafficData> {
  return callAPI(`${API_BASE_URL}${ENDPOINTS.TRAFFIC}/${trafficId}`);
}

export async function updateTrafficData(trafficId: string, trafficData: any) {
  return callAPI(`${API_BASE_URL}${ENDPOINTS.TRAFFIC}/${trafficId}`, {
    method: 'PUT',
    body: JSON.stringify(trafficData),
  });
}

export async function deleteTrafficData(trafficId: string) {
  return callAPI(`${API_BASE_URL}${ENDPOINTS.TRAFFIC}/${trafficId}`, {
    method: 'DELETE',
  });
}

// ===== FILTER FUNCTIONS =====
export async function getTrafficByLocation(location: string): Promise<TrafficData[]> {
  return callAPI(`${API_BASE_URL}${ENDPOINTS.TRAFFIC}?location=${location}`);
}

export async function getTrafficByStatus(status: string): Promise<TrafficData[]> {
  return callAPI(`${API_BASE_URL}${ENDPOINTS.TRAFFIC}?status=${status}`);
}