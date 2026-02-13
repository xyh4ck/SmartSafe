import request from "@/utils/request";

const API_PATH = "/system/log";

const LogAPI = {
  getLogList(query: LogPageQuery) {
    return request<ApiResponse<PageResult<LogTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  getLogDetail(query: number) {
    return request<ApiResponse<LogTable>>({
      url: `${API_PATH}/detail/${query}`,
      method: "get",
    });
  },

  deleteLog(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: body,
    });
  },

  exportLog(body: LogPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: body,
      responseType: "blob",
    });
  },
};

export default LogAPI;

export interface LogPageQuery extends PageQuery {
  type?: number;
  request_path?: string;
  creator_name?: string;
  /** 开始时间 */
  start_time?: string;
  /** 结束时间 */
  end_time?: string;
  // 创建人ID
  creator?: number;
}

export interface LogTable {
  id?: number;
  type?: number; // 1 登录日志 2 操作日志
  request_path?: string;
  request_method?: string;
  request_ip?: string;
  login_location?: string;
  request_browser?: string;
  request_os?: string;
  response_code?: number;
  request_payload?: string;
  response_json?: string;
  process_time?: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
  creator?: creatorType;
}
