import request from "@/utils/request";

const API_PATH = "/model/registry";

export const ModelRegistryAPI = {
  getList(query: ModelPageQuery) {
    return request<ApiResponse<PageResult<ModelItem[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  getDetail(id: number) {
    return request<ApiResponse<ModelItem>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  create(body: ModelForm) {
    return request<ApiResponse<ModelItem>>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  update(id: number, body: ModelForm) {
    return request<ApiResponse<ModelItem>>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  delete(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  test(id: number) {
    return request<ApiResponse<{ success: boolean; status: number; msg: string }>>({
      url: `${API_PATH}/connect/test/${id}`,
      method: "post",
    });
  },

  setAvailable(body: { ids: number[]; status: boolean }) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  updateVersion(id: number, body: { version: string }) {
    return request<ApiResponse<ModelItem>>({
      url: `${API_PATH}/version/${id}`,
      method: "put",
      data: body,
    });
  },

  updateQuota(id: number, body: { quota_limit?: number; quota_used?: number }) {
    return request<ApiResponse<ModelItem>>({
      url: `${API_PATH}/quota/${id}`,
      method: "put",
      data: body,
    });
  },
};

export default ModelRegistryAPI;

export interface ModelPageQuery extends PageQuery {
  name?: string;
  provider?: string;
  type?: string;
  available?: boolean;
}

export interface ModelItem {
  id?: number;
  name?: string;
  provider?: string;
  type?: string;
  api_base?: string;
  available?: boolean;
  version?: string;
  quota_limit?: number;
  quota_used?: number;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ModelForm {
  name?: string;
  provider?: string;
  type?: string;
  api_base?: string;
  api_key?: string;
  available?: boolean;
  version?: string;
  quota_limit?: number;
  description?: string;
}
