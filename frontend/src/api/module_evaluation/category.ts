import request from "@/utils/request";

export interface CategoryTable {
  id?: number;
  dimension_id?: number;
  name?: string;
  code?: string | null;
  sort?: number;
  status?: boolean;
  description?: string | null;
  dimension?: any;
  created_at?: string;
  updated_at?: string;
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

export interface CategoryPageQuery extends PageQuery {
  /** 维度ID */
  dimension_id?: number;
  /** 分类名称 */
  name?: string;
  /** 是否启用 */
  status?: string;
}

export interface DimensionCategoryTree {
  dimension_id: number;
  dimension_name: string;
  dimension_code?: string;
  dimension_status: boolean;
  categories: CategoryTable[];
}

const API_PATH = "/evaluation/category";

export const CategoryAPI = {
  /** 分页查询 */
  page(query: CategoryPageQuery) {
    return request<ApiResponse<PageResult<CategoryTable[]>>>({
      url: `${API_PATH}/page`,
      method: "post",
      params: query,
    });
  },

  /** 获取列表 */
  list() {
    return request<ApiResponse<CategoryTable[]>>({
      url: `${API_PATH}/list`,
      method: "get",
    });
  },

  /** 根据维度获取分类 */
  getByDimension(dimension_id: number, only_active: boolean = false) {
    return request<ApiResponse<CategoryTable[]>>({
      url: `${API_PATH}/by-dimension`,
      method: "get",
      params: { dimension_id, only_active },
    });
  },

  /** 获取维度-分类树形结构（优化性能，一次请求获取所有数据） */
  getTree(only_active: boolean = false) {
    return request<ApiResponse<DimensionCategoryTree[]>>({
      url: `${API_PATH}/tree`,
      method: "get",
      params: { only_active },
    });
  },

  /** 新增分类 */
  create(body: CategoryForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  /** 更新分类 */
  update(id: number, body: CategoryForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "post",
      data: body,
    });
  },

  /** 删除分类 */
  delete(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "post",
      data: ids,
    });
  },

  /** 导出导入模板 */
  exportTemplate() {
    return request<Blob>({
      url: `${API_PATH}/export-template`,
      method: "get",
      responseType: "blob",
    });
  },

  /** 导出分类数据 */
  export() {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      responseType: "blob",
    });
  },

  /** 导入分类数据 */
  import(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: formData,
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },
};

export default CategoryAPI;

