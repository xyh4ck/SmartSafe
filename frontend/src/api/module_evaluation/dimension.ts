import request from "@/utils/request";

export interface DimensionTable {
  id?: number;
  name?: string;
  code?: string | null;
  sort?: number;
  status?: boolean;
  description?: string | null;
  creator?: any;
  created_at?: string;
  updated_at?: string;
  categories?: CategoryTable[];
}

export interface CategoryTable {
  id?: number;
  dimension_id?: number;
  name?: string;
  code?: string | null;
  sort?: number;
  status?: boolean;
  description?: string | null;
  dimension?: DimensionTable;
}

export interface DimensionForm {
  id?: number;
  name: string;
  code?: string | null;
  sort?: number;
  status: boolean;
  description?: string | null;
}

export interface CategoryForm {
  id?: number;
  dimension_id: number;
  name: string;
  code?: string | null;
  sort?: number;
  status: boolean;
  description?: string | null;
}

export interface DimensionPageQuery extends PageQuery {
  /** 风险维度名称 */
  name?: string;
  /** 风险维度代码 */
  code?: string;
  /** 是否启用 */
  status?: string;
}

export interface CategoryPageQuery extends PageQuery {
  /** 所属风险维度ID */
  dimension_id?: number;
  /** 风险类别名称 */
  name?: string;
  /** 风险类别代码 */
  code?: string;
  /** 是否启用 */
  status?: string;
}

const API_PATH = "/evaluation/dimension";

export const DimensionAPI = {
  /** 分页查询 */
  page(query: DimensionPageQuery) {
    return request<ApiResponse<PageResult<DimensionTable[]>>>({
      url: `${API_PATH}/page`,
      method: "post",
      params: query,
    });
  },

  /** 获取列表 */
  list() {
    return request<ApiResponse<DimensionTable[]>>({
      url: `${API_PATH}/list`,
      method: "get",
    });
  },

  /** 获取所有启用的维度 */
  getAllActive() {
    return request<ApiResponse<DimensionTable[]>>({
      url: `${API_PATH}/all-active`,
      method: "get",
    });
  },

  /** 新增维度 */
  create(body: DimensionForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  /** 更新维度 */
  update(id: number, body: DimensionForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "post",
      data: body,
    });
  },

  /** 删除维度 */
  delete(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "post",
      data: ids,
    });
  },
};

export default DimensionAPI;

