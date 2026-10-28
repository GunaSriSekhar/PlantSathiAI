import axios, { AxiosError } from 'axios';
import {
  AnalysisResult,
  ScanSummary,
  ScanDetail,
  ChatResponse,
  ChatMessage,
  ModelStatus,
  SavedPlant,
} from '../types';

const API_BASE_URL = '/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60s for local ML inference
});

export class ApiError extends Error {
  status?: number;
  code?: string;
  constructor(message: string, status?: number, code?: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

function handleAxiosError(error: unknown): never {
  if (axios.isAxiosError(error)) {
    const axiosErr = error as AxiosError<{ message?: string; detail?: string | { message?: string } }>;
    const data = axiosErr.response?.data;
    let message = axiosErr.message;
    if (data) {
      if (typeof data.detail === 'string') {
        message = data.detail;
      } else if (data.detail && typeof data.detail === 'object' && data.detail.message) {
        message = data.detail.message;
      } else if (data.message) {
        message = data.message;
      }
    }
    throw new ApiError(message, axiosErr.response?.status);
  }
  throw new ApiError(error instanceof Error ? error.message : 'Unknown error occurred');
}

export async function analyzeImage(file: File, save: boolean = true): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append('file', file);
  try {
    const response = await client.post<AnalysisResult>(`/analyze?save=${save}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    handleAxiosError(error);
  }
}

export async function identifyPlant(file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  try {
    const response = await client.post(`/identify`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    handleAxiosError(error);
  }
}

export async function diagnoseDisease(file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  try {
    const response = await client.post(`/diagnose`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    handleAxiosError(error);
  }
}

export async function getScans(limit: number = 50, offset: number = 0): Promise<ScanSummary[]> {
  try {
    const response = await client.get<ScanSummary[]>(`/scans?limit=${limit}&offset=${offset}`);
    return response.data;
  } catch (error) {
    handleAxiosError(error);
  }
}

export async function getScan(scanId: string): Promise<ScanDetail> {
  try {
    const response = await client.get<ScanDetail>(`/scans/${scanId}`);
    return response.data;
  } catch (error) {
    handleAxiosError(error);
  }
}

export async function deleteScan(scanId: string): Promise<void> {
  try {
    await client.delete(`/scans/${scanId}`);
  } catch (error) {
    handleAxiosError(error);
  }
}

export async function chatWithDoctor(
  message: string,
  scanId?: string,
  conversationHistory: ChatMessage[] = []
): Promise<ChatResponse> {
  try {
    const response = await client.post<ChatResponse>('/chat', {
      message,
      scan_id: scanId || null,
      conversation_history: conversationHistory,
    });
    return response.data;
  } catch (error) {
    handleAxiosError(error);
  }
}

export async function getHealth(): Promise<{ status: string; version: string; environment: string }> {
  try {
    const response = await client.get('/health');
    return response.data;
  } catch (error) {
    handleAxiosError(error);
  }
}

export async function getModelStatus(): Promise<ModelStatus[]> {
  try {
    const response = await client.get<ModelStatus[]>('/models/status');
    return response.data;
  } catch (error) {
    handleAxiosError(error);
  }
}

export async function getSavedPlants(): Promise<SavedPlant[]> {
  try {
    const response = await client.get<SavedPlant[]>('/plants');
    return response.data;
  } catch (error) {
    handleAxiosError(error);
  }
}

export async function savePlant(data: {
  common_name: string;
  scientific_name?: string;
  notes?: string;
  scan_id?: string;
}): Promise<SavedPlant> {
  try {
    const response = await client.post<SavedPlant>('/plants', data);
    return response.data;
  } catch (error) {
    handleAxiosError(error);
  }
}

export async function deleteSavedPlant(id: string): Promise<void> {
  try {
    await client.delete(`/plants/${id}`);
  } catch (error) {
    handleAxiosError(error);
  }
}
