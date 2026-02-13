import request from "@/utils/request";

export interface TestCaseTable {
  id?: number;
  dimension_id?: number;
  category_id?: number;
  category?: string;
  subcategory?: string | null;
  prompt?: string;
  expected_behavior?: string | null;
  risk_level?: string;
  tags?: string[] | null;
  status?: boolean;
  version?: number;
  description?: string | null;
  refusal_expectation?: string | null;
  refusal_reason?: string | null;
  source?: string | null;
  updated_cycle?: string | null;
  creator?: any;
  created_at?: string;
  updated_at?: string;
}

export interface TestCaseForm {
  id?: number;
  dimension_id?: number;
  category_id?: number;
  prompt: string;
  expected_behavior?: string | null;
  risk_level: string;
  tags?: string[] | null;
  status: boolean;
  description?: string | null;
  refusal_expectation?: string | null;
  refusal_reason?: string | null;
  source?: string | null;
  updated_cycle?: string | null;
}

export interface TestCasePageQuery extends PageQuery {
  /** 维度ID（单个） */
  dimension_id?: number;
  /** 维度ID列表（逗号分隔） */
  dimension_ids?: string;
  /** 分类ID（单个） */
  category_id?: number;
  /** 分类ID列表（逗号分隔） */
  category_ids?: string;
  /** 类别 */
  category?: string;
  /** 风险等级 */
  risk_level?: string;
  /** 是否启用 */
  status?: string;
  /** 开始时间 */
  start_time?: string;
  /** 结束时间 */
  end_time?: string;
  /** 排序字段,格式:[{'field':'asc/desc'}] */
  order_by?: string;
  /** 创建人 */
  creator?: number;
  /** 拒答期望：should_refuse/should_not_refuse */
  refusal_expectation?: string;
}

const API_PATH = "/evaluation/testcase";

export const TestCaseAPI = {
  /** 分页查询（后端为 POST + query 依赖，使用 params 传参） */
  page(query: TestCasePageQuery) {
    return request<ApiResponse<PageResult<TestCaseTable[]>>>({
      url: `${API_PATH}/page`,
      method: "post",
      params: query,
    });
  },

  /** 新增用例 */
  create(body: TestCaseForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  /** 更新用例 */
  update(id: number, body: TestCaseForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "post",
      data: body,
    });
  },

  /** 删除用例 */
  delete(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "post",
      data: ids,
    });
  },

  /** 批量导入 */
  import(items: TestCaseForm[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: { items },
    });
  },

  /** 导出列表（返回Excel文件流） */
  export(query?: Partial<TestCasePageQuery>) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query ?? {},
      responseType: "blob",
    });
  },
};

export default TestCaseAPI;


