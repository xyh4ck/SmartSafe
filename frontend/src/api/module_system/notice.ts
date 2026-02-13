import request from "@/utils/request";

const API_PATH = "/system/notice";

const NoticeAPI = {
  getNoticeList(query: NoticePageQuery) {
    return request<ApiResponse<PageResult<NoticeTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  getNoticeListAvailable() {
    return request<ApiResponse<PageResult<NoticeTable[]>>>({
      url: `${API_PATH}/available`,
      method: "get",
    });
  },

  getNoticeDetail(query: number) {
    return request<ApiResponse<NoticeTable>>({
      url: `${API_PATH}/detail/${query}`,
      method: "get",
    });
  },

  createNotice(body: NoticeForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  updateNotice(id: number, body: NoticeForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  deleteNotice(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: body,
    });
  },

  batchAvailableNotice(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  exportNotice(body: NoticePageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: body,
      responseType: "blob",
    });
  },
};

export default NoticeAPI;

export interface NoticePageQuery extends PageQuery {
  /** 通知标题 */
  notice_title?: string;
  /** 通知类型 */
  notice_type?: string;
  /** 通知状态 */
  status?: boolean;
  /** 开始时间 */
  start_time?: string;
  /** 结束时间 */
  end_time?: string;
  // 创建人ID
  creator?: number;
}

export interface NoticeTable {
  index?: number;
  id?: number;
  notice_title?: string;
  notice_type?: string;
  notice_content?: string;
  status?: boolean;
  description?: string;
  created_at?: string;
  updated_at?: string;
  creator?: creatorType;
}

export interface NoticeForm {
  id?: number;
  notice_title?: string;
  notice_type?: string;
  notice_content?: string;
  status?: boolean;
  description?: string;
}
