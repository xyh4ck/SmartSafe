import request from "@/utils/request";

// ==================== 关键词类型定义 ====================

export interface KeywordTable {
  id?: number;
  category_id?: number;
  category_name?: string;
  word?: string;
  match_type?: string;
  risk_level?: string;
  weight?: number;
  synonyms?: string[] | null;
  tags?: string[] | null;
  status?: boolean;
  hit_count?: number;
  description?: string | null;
  creator?: any;
  created_at?: string;
  updated_at?: string;
}

export interface KeywordForm {
  id?: number;
  category_id: number;
  word: string;
  match_type?: string;
  risk_level?: string;
  weight?: number;
  synonyms?: string[] | null;
  tags?: string[] | null;
  status?: boolean;
  description?: string | null;
}

export interface KeywordPageQuery extends PageQuery {
  category_id?: number;
  category_ids?: string;
  word?: string;
  match_type?: string;
  risk_level?: string;
  status?: boolean;
  start_time?: string;
  end_time?: string;
  creator?: number;
}

// ==================== 匹配相关类型 ====================

export interface KeywordMatchRequest {
  text: string;
  category_ids?: number[];
  match_types?: string[];
  min_risk_level?: string;
}

export interface KeywordMatchResult {
  keyword_id: number;
  word: string;
  match_type: string;
  risk_level: string;
  category_id: number;
  category_name: string;
  weight: number;
  position?: number;
  matched_text?: string;
}

export interface KeywordMatchResponse {
  total_matches: number;
  risk_score: number;
  highest_risk_level: string;
  matches: KeywordMatchResult[];
}

// ==================== API 路径 ====================

const KEYWORD_API_PATH = "/evaluation/keyword-questionbank/keyword";

// ==================== 关键词 API ====================

export const KeywordAPI = {
  /** 分页查询 */
  page(query: KeywordPageQuery) {
    return request<ApiResponse<PageResult<KeywordTable[]>>>({
      url: `${KEYWORD_API_PATH}/page`,
      method: "post",
      params: query,
    });
  },

  /** 获取列表 */
  list(query?: Partial<KeywordPageQuery>) {
    return request<ApiResponse<KeywordTable[]>>({
      url: `${KEYWORD_API_PATH}/list`,
      method: "post",
      params: query,
    });
  },

  /** 获取某类别下的关键词 */
  getByCategory(categoryId: number, status?: boolean) {
    return request<ApiResponse<KeywordTable[]>>({
      url: `${KEYWORD_API_PATH}/by-category/${categoryId}`,
      method: "get",
      params: { status },
    });
  },

  /** 新增 */
  create(body: KeywordForm) {
    return request<ApiResponse>({
      url: `${KEYWORD_API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  /** 更新 */
  update(id: number, body: KeywordForm) {
    return request<ApiResponse>({
      url: `${KEYWORD_API_PATH}/update/${id}`,
      method: "post",
      data: body,
    });
  },

  /** 删除 */
  delete(ids: number[]) {
    return request<ApiResponse>({
      url: `${KEYWORD_API_PATH}/delete`,
      method: "post",
      data: ids,
    });
  },

  /** 批量导入 */
  import(items: KeywordForm[]) {
    return request<ApiResponse>({
      url: `${KEYWORD_API_PATH}/import`,
      method: "post",
      data: { items },
    });
  },

  /** 导出 */
  export(query?: Partial<KeywordPageQuery>) {
    return request<Blob>({
      url: `${KEYWORD_API_PATH}/export`,
      method: "post",
      params: query,
      responseType: "blob",
    });
  },

  /** 关键词匹配 */
  match(matchRequest: KeywordMatchRequest) {
    return request<ApiResponse<KeywordMatchResponse>>({
      url: `${KEYWORD_API_PATH}/match`,
      method: "post",
      data: matchRequest,
    });
  },
};

export default KeywordAPI;
