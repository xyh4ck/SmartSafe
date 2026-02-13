import request from "@/utils/request";

const API_PATH = "/system/dept";

const DeptAPI = {
  getDeptList(query?: DeptPageQuery) {
    return request<ApiResponse<DeptTable[]>>({
      url: `${API_PATH}/tree`,
      method: "get",
      params: query,
    });
  },

  getDeptDetail(query: number) {
    return request<ApiResponse<DeptTable>>({
      url: `${API_PATH}/detail/${query}`,
      method: "get",
    });
  },

  createDept(body: DeptForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  updateDept(id: number, body: DeptForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  deleteDept(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: body,
    });
  },

  batchAvailableDept(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },
};

export default DeptAPI;

export interface DeptPageQuery {
  name?: string;
  status?: boolean;
  /** 开始时间 */
  start_time?: string;
  /** 结束时间 */
  end_time?: string;
}

export interface DeptTable {
  index?: number;
  id?: number;
  name?: string;
  order?: number;
  code?: string;
  parent_id?: number;
  parent_name?: string;
  status?: boolean;
  description?: string;
  created_at?: string;
  updated_at?: string;
  children?: DeptTable[];
  creator?: creatorType;
}

export interface DeptForm {
  id?: number;
  name?: string;
  order?: number;
  code?: string;
  parent_id?: number;
  status?: boolean;
  description?: string;
}
