import request from "@/utils/request";

export interface TestCaseCandidateTable {
  id?: number;
  dimension_id?: number;
  category_id?: number;
  dimension_name?: string | null;
  category_name?: string | null;
  prompt?: string;
  expected_behavior?: string | null;
  risk_level?: string;
  tags?: string[] | null;
  refusal_expectation?: string | null;
  refusal_reason?: string | null;
  gen_batch_id?: string | null;
  status?: string;
  reviewer_id?: number | null;
  reviewed_at?: string | null;
  review_note?: string | null;
  description?: string | null;
  creator?: any;
  created_at?: string;
  updated_at?: string;
}

export interface TestCaseCandidateForm {
  dimension_id: number;
  category_id: number;
  prompt: string;
  expected_behavior?: string | null;
  risk_level: string;
  tags?: string[] | null;
  refusal_expectation?: string | null;
  refusal_reason?: string | null;
  description?: string | null;
}

export interface TestCaseCandidatePageQuery extends PageQuery {
  dimension_id?: number;
  category_id?: number;
  refusal_expectation?: string;
  status?: string;
  gen_batch_id?: string;
}

export interface BatchReviewRequest {
  ids: number[];
  action: "approve" | "reject";
  review_note?: string;
}

export interface BatchPublishRequest {
  ids: number[];
}

export interface GenerateCandidateRequest {
  refusal_expectation: string;
  category_ids?: number[];
  count_per_category?: number;
}

export interface CoverageResult {
  should_refuse: {
    total: number;
    by_category: Record<string, { category_id: number; count: number }>;
    gaps: Array<{
      category_id: number;
      category_name: string;
      current: number;
      required: number;
      gap: number;
    }>;
  };
  should_not_refuse: {
    total: number;
    by_aspect: Record<string, number>;
    gaps: Array<{
      aspect: string;
      current: number;
      required: number;
      gap: number;
    }>;
  };
}

const API_PATH = "/evaluation/testcase-candidate";

export const TestCaseCandidateAPI = {
  /** 分页查询 */
  page(query: TestCaseCandidatePageQuery) {
    return request<ApiResponse<PageResult<TestCaseCandidateTable[]>>>({
      url: `${API_PATH}/page`,
      method: "post",
      params: query,
    });
  },

  /** 新增候选题 */
  create(body: TestCaseCandidateForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  /** 批量审核 */
  review(body: BatchReviewRequest) {
    return request<ApiResponse>({
      url: `${API_PATH}/review`,
      method: "post",
      data: body,
    });
  },

  /** 发布到正式库 */
  publish(body: BatchPublishRequest) {
    return request<ApiResponse>({
      url: `${API_PATH}/publish`,
      method: "post",
      data: body,
    });
  },

  /** 自动生成候选题 */
  generate(body: GenerateCandidateRequest) {
    return request<ApiResponse>({
      url: `${API_PATH}/generate`,
      method: "post",
      data: body,
    });
  },

  /** 获取覆盖度统计 */
  coverage() {
    return request<ApiResponse<CoverageResult>>({
      url: `${API_PATH}/coverage`,
      method: "get",
    });
  },

  /** 删除候选题 */
  delete(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "post",
      data: ids,
    });
  },
};

export default TestCaseCandidateAPI;
