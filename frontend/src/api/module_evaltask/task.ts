import request from "@/utils/request";

const API_PATH = "/evaltask";

const EvalTaskAPI = {
  createTask(body: EvalTaskCreate) {
    return request<ApiResponse<{ task_id: number }>>({
      url: `${API_PATH}/tasks`,
      method: "post",
      data: body,
    });
  },

  getTasks(params?: { status?: string; name?: string; page_no?: number; page_size?: number, order_by?: string }) {
    return request<ApiResponse<PageResult<EvalTaskItem[]>>>({
      url: `${API_PATH}/tasks`,
      method: "get",
      params,
    });
  },

  getTaskDetail(taskId: number) {
    return request<ApiResponse<EvalTaskItem>>({
      url: `${API_PATH}/tasks/${taskId}`,
      method: "get",
    });
  },

  getTaskCases(taskId: number, params?: { page_no?: number; page_size?: number }, config?: { headers?: Record<string, string> }) {
    return request<ApiResponse<PageResult<EvalTaskCaseItem[]>>>({
      url: `${API_PATH}/tasks/${taskId}/cases`,
      method: "get",
      params,
      headers: config?.headers,
    });
  },

  getTaskResult(taskId: number) {
    return request<ApiResponse<EvalTaskResult>>({
      url: `${API_PATH}/tasks/${taskId}/result`,
      method: "get",
    });
  },

  getTaskLogs(
    taskId: number,
    params?: { page_no?: number; page_size?: number; stage?: string; level?: string; case_id?: number }
  ) {
    return request<ApiResponse<PageResult<EvalTaskLogItem[]>>>({
      url: `${API_PATH}/tasks/${taskId}/logs`,
      method: "get",
      params,
    });
  },

  getTaskProgress(taskId: number, config?: { headers?: Record<string, string> }) {
    return request<ApiResponse<EvalTaskProgress>>({
      url: `${API_PATH}/tasks/${taskId}/progress`,
      method: "get",
      headers: config?.headers,
    });
  },

  exportTaskCases(taskId: number) {
    return request<Blob>({
      url: `${API_PATH}/tasks/${taskId}/cases/export`,
      method: "get",
      responseType: "blob",
    });
  },

  exportTaskReport(taskId: number) {
    return request<Blob>({
      url: `${API_PATH}/tasks/${taskId}/report/export`,
      method: "get",
      responseType: "blob",
    });
  },

  deleteTasks(ids: number[]) {
    return request<ApiResponse<{ count: number }>>({
      url: `${API_PATH}/tasks`,
      method: "delete",
      data: ids,
    });
  },
};

export default EvalTaskAPI;

export interface EvalTaskCreate {
  name: string;
  cases: { prompt: string; llm_provider?: string; llm_params?: Record<string, any> }[];
}

export interface EvalTaskItem {
  id: number;
  name: string;
  status: string;
  llm_provider?: string | null;
  llm_params?: Record<string, any> | null;
  total_cases: number;
  finished_cases: number;
  risk_summary?: Record<string, any> | null;
  created_at?: string;
  started_at?: string | null;
  finished_at?: string | null;
}

export interface EvalTaskCaseItem {
  id: number;
  prompt: string;
  status: string;
  output_text?: string | null;
  llm_provider?: string | null;
  llm_params?: Record<string, unknown> | null;
  risk_scores?: Record<string, number> | null;
  risk_level?: string | null;
  risk_reason?: string | null;
  completion_tokens?: number | null;
  prompt_tokens?: number | null;
  total_tokens?: number | null;
  started_at?: string | null;
  finished_at?: string | null;
}

export interface EvalTaskLogItem {
  id: number;
  task_id: number;
  case_id?: number | null;
  stage: string;
  level: string;
  message: string;
  created_at?: string | null;
}

export interface EvalTaskProgress {
  task_id: number;
  status: string;
  finished: number;
  total: number;
  percent: number;
  polling?: boolean;
}

export interface EvalTaskResult {
  task_id: number;
  summary: Record<string, any>;
  metrics: Record<string, any>;
  top_risks: Record<string, any>[];
}