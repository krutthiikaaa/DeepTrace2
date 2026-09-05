import axios, { AxiosError } from 'axios';
import type { HealthStatus, ImageDetectionResult, VideoDetectionResult, AudioDetectionResult } from '../types/detection';

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 120000, // 2 minutes, inference can take some time
});

export const checkHealth = async (): Promise<HealthStatus> => {
  try {
    const response = await apiClient.get<HealthStatus>('/health');
    return response.data;
  } catch (error) {
    throw new Error('Backend is unavailable');
  }
};

const handleApiError = (error: unknown): never => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail: string }>;
    if (axiosError.response) {
      throw new Error(axiosError.response.data?.detail || `Server error: ${axiosError.response.status}`);
    } else if (axiosError.request) {
      throw new Error('No response from server. Backend might be down.');
    }
  }
  throw new Error(error instanceof Error ? error.message : 'An unexpected error occurred');
};

export const detectImage = async (file: File): Promise<ImageDetectionResult> => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await apiClient.post<ImageDetectionResult>('/detect/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

export const detectVideo = async (file: File): Promise<VideoDetectionResult> => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await apiClient.post<VideoDetectionResult>('/detect/video', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

export const detectAudio = async (file: File): Promise<AudioDetectionResult> => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await apiClient.post<AudioDetectionResult>('/detect/audio', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};
