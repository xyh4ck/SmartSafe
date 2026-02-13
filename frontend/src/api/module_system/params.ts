import request from "@/utils/request";

const API_PATH = "/system/param";

const ParamsAPI = {
  uploadFile(body: any) {
    return request<ApiResponse<UploadFilePath>>({
      url: `${API_PATH}/upload`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  getInitConfig() {
    return request<ApiResponse<ConfigTable[]>>({
      url: `${API_PATH}/info`,
      method: "get",
    });
  },

  getConfigList(query: ConfigPageQuery) {
    return request<ApiResponse<PageResult<ConfigTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  getConfigDetail(query: number) {
    return request<ApiResponse<ConfigTable>>({
      url: `${API_PATH}/detail/${query}`,
      method: "get",
    });
  },

  createConfig(body: ConfigForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  updateConfig(id: number, body: ConfigForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  deleteConfig(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: body,
    });
  },

  exportConfig(body: ConfigPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: body,
      responseType: "blob",
    });
  },
};

export default ParamsAPI;

export interface ConfigPageQuery extends PageQuery {
  /** 配置名称 */
  config_name?: string;
  /** 配置键 */
  config_key?: string;
  /** 配置类型 */
  config_type?: boolean;
  /** 开始时间 */
  start_time?: string;
  /** 结束时间 */
  end_time?: string;
  // 创建人ID
  creator?: number;
}

export interface ConfigTable {
  id?: number;
  config_name?: string;
  config_key?: string;
  config_value?: string;
  config_type?: boolean;
  description?: string;
  created_at?: string;
  updated_at?: string;
  creator?: creatorType;
}

export interface ConfigForm {
  id?: number;
  config_name?: string;
  config_key?: string;
  config_value?: string;
  config_type?: boolean;
  description?: string;
}
