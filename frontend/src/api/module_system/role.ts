import request from "@/utils/request";

const API_PATH = "/system/role";

const RoleAPI = {
  getRoleList(query?: TablePageQuery) {
    return request<ApiResponse<PageResult<RoleTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  getRoleDetail(query: number) {
    return request<ApiResponse<RoleTable>>({
      url: `${API_PATH}/detail/${query}`,
      method: "get",
    });
  },

  createRole(body: RoleForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  updateRole(id: number, body: RoleForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  deleteRole(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: body,
    });
  },

  batchAvailableRole(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  setPermission(body: permissionDataType) {
    return request<ApiResponse>({
      url: `${API_PATH}/permission/setting`,
      method: "patch",
      data: body,
    });
  },

  exportRole(body: TablePageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: body,
      responseType: "blob",
    });
  },
};

export default RoleAPI;

export interface TablePageQuery extends PageQuery {
  name?: string;
  status?: boolean;
  /** 开始时间 */
  start_time?: string;
  /** 结束时间 */
  end_time?: string;
  // 创建人ID
  creator?: number;
}

export interface RoleTable {
  index?: number;
  id: number;
  name: string;
  order?: number;
  code?: string;
  data_scope?: number;
  status?: boolean;
  menus?: permissionMenuType[];
  depts?: permissionDeptType[];
  description?: string;
  created_at?: string;
  updated_at?: string;
  creator?: creatorType;
}

export interface RoleForm {
  id?: number;
  name?: string;
  order?: number;
  code?: string;
  status?: boolean;
  description?: string;
  created_at?: string;
  updated_at?: string;
  creator?: creatorType;
  menus?: permissionMenuType[];
  depts?: permissionDeptType[];
}

export interface permissionDataType {
  role_ids: RoleTable["id"][];
  menu_ids: permissionMenuType["id"][];
  data_scope: number;
  dept_ids: permissionDeptType["id"][];
}

export interface permissionDeptType {
  id: number;
  name: string;
  parent_id: number;
  children: permissionDeptType[];
}

export interface permissionMenuType {
  id: number;
  name: string;
  type: number;
  permission: string;
  parent_id?: number;
  status: boolean;
  description?: string;
  children?: permissionMenuType[];
}
