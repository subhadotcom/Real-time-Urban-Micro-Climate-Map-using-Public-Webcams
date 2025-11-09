/**
 * API service for HTTP requests
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

async function fetchAPI(endpoint) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function getWebcams() {
  return fetchAPI('/api/webcams');
}

export async function getLatestAnalysis() {
  return fetchAPI('/api/latest');
}

export async function getWebcamAnalysis(webcamId) {
  return fetchAPI(`/api/latest/${webcamId}`);
}

export async function getHealth() {
  return fetchAPI('/health');
}

