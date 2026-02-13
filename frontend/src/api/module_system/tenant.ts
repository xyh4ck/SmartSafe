import request from "@/utils/request";

const API_PATH = "/system/tenant";

const TenantAPI = {
  list(query: ObjPageQuery) {
    return request<ApiResponse<PageResult<ObjTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  detail(query: number) {
    return request<ApiResponse<ObjTable>>({
      url: `${API_PATH}/detail/${query}`,
      method: "get",
    });
  },

  create(body: ObjForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  update(id: number, body: ObjForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  delete(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: body,
    });
  },

  batch(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  export(body: ObjPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: body,
      responseType: "blob",
    });
  },

  download() {
    return request<ApiResponse>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  import(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },
};

export default TenantAPI;

export interface ObjPageQuery extends PageQuery {
  /** 示例标题 */
  name?: string;
  /** 示例状态 */
  status?: boolean;
  /** 开始时间 */
  start_time?: string;
  /** 结束时间 */
  end_time?: string;
  /** 创建人 */
  creator?: number;
}

export interface ObjTable {
  index?: number;
  id?: number;
  name?: string;
  code?: string;
  status?: boolean;
  description?: string;
  created_at?: string;
  updated_at?: string;
  // creator?: creatorType;
}

export interface ObjForm {
  id?: number;
  name?: string;
  code?: string;
  status?: boolean;
  description?: string;
}
