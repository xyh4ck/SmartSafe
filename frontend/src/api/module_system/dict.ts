import request from "@/utils/request";

const API_PATH = "/system/dict";

const DictAPI = {
  getDictTypeList(query: DictPageQuery) {
    return request<ApiResponse<PageResult<DictTable[]>>>({
      url: `${API_PATH}/type/list`,
      method: "get",
      params: query,
    });
  },

  getDictTypeOptionselect() {
    return request<ApiResponse>({
      url: `${API_PATH}/type/optionselect`,
      method: "get",
    });
  },

  getDictTypeDetail(query: number) {
    return request<ApiResponse<DictTable>>({
      url: `${API_PATH}/type/detail/${query}`,
      method: "get",
    });
  },

  createDictType(body: DictForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/type/create`,
      method: "post",
      data: body,
    });
  },

  updateDictType(id: number, body: DictForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/type/update/${id}`,
      method: "put",
      data: body,
    });
  },

  deleteDictType(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/type/delete`,
      method: "delete",
      data: body,
    });
  },

  batchAvailableDict(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/type/available/setting`,
      method: "patch",
      data: body,
    });
  },

  exportDictType(body: DictPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/type/export`,
      method: "post",
      data: body,
      responseType: "blob",
    });
  },

  getDictDataList(query: DictDataPageQuery) {
    return request<ApiResponse<PageResult<DictDataTable[]>>>({
      url: `${API_PATH}/data/list`,
      method: "get",
      params: query,
    });
  },

  getDictDataDetail(query: number) {
    return request<ApiResponse<DictDataTable>>({
      url: `${API_PATH}/data/detail/${query}`,
      method: "get",
    });
  },

  createDictData(body: DictDataForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/data/create`,
      method: "post",
      data: body,
    });
  },

  updateDictData(id: number, body: DictDataForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/data/update/${id}`,
      method: "put",
      data: body,
    });
  },

  deleteDictData(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/data/delete`,
      method: "delete",
      data: body,
    });
  },

  batchAvailableDictData(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/data/available/setting`,
      method: "patch",
      data: body,
    });
  },

  exportDictData(body: DictDataPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/data/export`,
      method: "post",
      data: body,
      responseType: "blob",
    });
  },

  getInitDict(dict_type: string) {
    return request<ApiResponse>({
      url: `${API_PATH}/data/info/${dict_type}`,
      method: "get",
    });
  },
};

export default DictAPI;

export interface DictPageQuery extends PageQuery {
  /** 通知标题 */
  dict_name?: string;
  /** 通知类型 */
  dict_type?: string;
  /** 通知状态 */
  status?: boolean;
  /** 开始时间 */
  start_time?: string;
  /** 结束时间 */
  end_time?: string;
  // 创建人ID
  creator?: number;
}

export interface DictDataPageQuery extends PageQuery {
  dict_label?: string;
  dict_type?: string;
  status?: boolean;
  start_time?: string;
  end_time?: string;
  // 创建人ID
  creator?: number;
}

export interface DictTable {
  index?: number;
  id?: number;
  dict_name?: string;
  dict_type?: string;
  status?: boolean;
  description?: string;
  created_at?: string;
  updated_at?: string;
  creator?: creatorType;
}

export interface DictForm {
  id?: number;
  dict_name?: string;
  dict_type?: string;
  status?: boolean;
  description?: string;
}

export interface DictDataTable {
  index?: number;
  id?: number;
  dict_sort?: number;
  dict_label?: string;
  dict_value?: string;
  dict_type?: string;
  css_class?: string;
  list_class?: string;
  is_default?: boolean;
  status?: boolean;
  description?: string;
  created_at?: string;
  updated_at?: string;
  creator?: creatorType;
}

export interface DictDataForm {
  id?: number;
  dict_sort?: number;
  dict_label?: string;
  dict_value?: string;
  dict_type?: string;
  css_class?: string;
  list_class?: string;
  is_default?: boolean;
  status?: boolean;
  description?: string;
}
