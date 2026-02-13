import request from "@/utils/request";

const API_PATH = "/system/position";

const PositionAPI = {
  getPositionList(query?: PositionPageQuery) {
    return request<ApiResponse<PageResult<PositionTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  getPositionDetail(query: number) {
    return request<ApiResponse<PositionTable>>({
      url: `${API_PATH}/detail/${query}`,
      method: "get",
    });
  },

  createPosition(body: PositionForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  updatePosition(id: number, body: PositionForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  deletePosition(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: body,
    });
  },

  batchAvailablePosition(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  exportPosition(body: PositionPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: body,
      responseType: "blob",
    });
  },
};

export default PositionAPI;

export interface PositionPageQuery extends PageQuery {
  name?: string;
  status?: boolean;
  /** 开始时间 */
  start_time?: string;
  /** 结束时间 */
  end_time?: string;
  // 创建人ID
  creator?: number;
}

export interface PositionTable {
  index?: number;
  id?: number;
  name?: string;
  order?: number;
  status?: boolean;
  description?: string;
  created_at?: string;
  updated_at?: string;
  creator?: creatorType;
}

export interface PositionForm {
  id?: number;
  name?: string;
  order?: number;
  status?: boolean;
  description?: string;
}
