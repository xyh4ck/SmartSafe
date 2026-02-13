import axios, {
  type InternalAxiosRequestConfig,
  type AxiosResponse,
  type AxiosInstance,
  type AxiosError,
} from "axios";
import qs from "qs";
import { useUserStoreHook } from "@/store/modules/user.store";
import { ResultEnum } from "@/enums/api/result.enum";
import { Auth } from "@/utils/auth";
import router from "@/router";

/**
 * 创建 HTTP 请求实例
 */
const httpRequest: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API,
  timeout: import.meta.env.VITE_TIMEOUT,
  headers: { "Content-Type": "application/json;charset=utf-8" },
  paramsSerializer: (params) => qs.stringify(params),
});

let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];
const onRefreshed = (token: string) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};
const addRefreshSubscriber = (cb: (token: string) => void) => {
  refreshSubscribers.push(cb);
};

/**
 * 请求拦截器 - 添加 Authorization 头
 */
httpRequest.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const accessToken = Auth.getAccessToken();
    const noAuth = config.headers.Authorization === "no-auth";
    if (noAuth) {
      delete config.headers.Authorization;
    } else if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    } else {
      delete config.headers.Authorization;
    }

    return config;
  },
  (error) => {
    ElMessage.error(error);
    return Promise.reject(error);
  }
);

/**
 * 响应拦截器 - 统一处理响应和错误
 */
httpRequest.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    // 如果响应是二进制流，则直接返回（用于文件下载、Excel 导出等）
    if (response.config.responseType === "blob") {
      return response;
    }

    const data = response.data;

    // 检查请求是否失败
    if (data.code !== ResultEnum.SUCCESS) {
      ElMessage.error(data.msg);
      return Promise.reject(response);
    }

    // 如果请求不是 GET 请求，请求成功时显示成功提示
    if (response.config.method?.toUpperCase() !== "GET") {
      ElMessage.success(data.msg);
    }

    return response;
  },
  async (error: AxiosError<ApiResponse>) => {
    // 处理 304 Not Modified 为成功（用于 ETag 缓存轻量校验）
    if (error.response?.status === 304) {
      return Promise.resolve(error.response as AxiosResponse<ApiResponse>);
    }
    const data = error.response?.data;
    const status = error.response?.status;
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // 处理blob类型的错误响应
    if (error.response?.config.responseType === "blob" && error.response.data instanceof Blob) {
      try {
        // 将blob转换为JSON
        const text = await new Response(error.response.data).text();
        const jsonData: ApiResponse = JSON.parse(text);

        if (jsonData.code === ResultEnum.ERROR) {
          ElMessage.error(jsonData.msg || "请求错误");
          return Promise.reject(new Error(jsonData.msg || "请求错误"));
        } else if (jsonData.code === ResultEnum.EXCEPTION) {
          ElMessage.error(jsonData.msg || "服务异常");
          return Promise.reject(new Error(jsonData.msg || "服务异常"));
        }
      } catch (e) {
        console.error("请求异常:", e);
        // 如果无法解析为JSON，则使用默认错误处理
        ElMessage.error(error.message || "请求异常");
        return Promise.reject(new Error(error.message || "请求异常"));
      }
    }

    if (data?.code === ResultEnum.TOKEN_EXPIRED) {
      try {
        if (originalRequest && originalRequest._retry) {
          await redirectToLogin("登录已过期，请重新登录");
          return Promise.reject(new Error(data.msg));
        }
        originalRequest._retry = true;
        if (isRefreshing) {
          return new Promise((resolve) => {
            addRefreshSubscriber((token: string) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              resolve(httpRequest(originalRequest));
            });
          });
        }
        isRefreshing = true;
        await useUserStoreHook().refreshToken();
        isRefreshing = false;
        const newToken = Auth.getAccessToken();
        onRefreshed(newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return httpRequest(originalRequest);
      } catch (e) {
        isRefreshing = false;
        await redirectToLogin("登录已过期，请重新登录");
        return Promise.reject(new Error(data?.msg || "登录过期"));
      }
    } else if (data?.code === ResultEnum.ERROR) {
      ElMessage.error(data.msg || "请求错误");
      return Promise.reject(new Error(data.msg || "请求错误"));
    } else if (data?.code === ResultEnum.UNAUTHORIZED) {
      try {
        if (originalRequest && originalRequest._retry) {
          ElMessage.error(data.msg || "暂无权限");
          return Promise.reject(new Error(data.msg || "请求错误"));
        }
        originalRequest._retry = true;
        if (isRefreshing) {
          return new Promise((resolve) => {
            addRefreshSubscriber((token: string) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              resolve(httpRequest(originalRequest));
            });
          });
        }
        isRefreshing = true;
        await useUserStoreHook().refreshToken();
        isRefreshing = false;
        const newToken = Auth.getAccessToken();
        onRefreshed(newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return httpRequest(originalRequest);
      } catch (e) {
        isRefreshing = false;
        await redirectToLogin("登录已过期，请重新登录");
        return Promise.reject(new Error(data?.msg || "暂无权限"));
      }
    } else if (data?.code === ResultEnum.EXCEPTION) {
      ElMessage.error(data.msg || "服务异常");
      return Promise.reject(new Error(data.msg || "服务异常"));
    } else if (status === 401 || status === 403) {
      try {
        if (originalRequest && originalRequest._retry) {
          return Promise.reject(new Error("未授权"));
        }
        originalRequest._retry = true;
        if (isRefreshing) {
          return new Promise((resolve) => {
            addRefreshSubscriber((token: string) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              resolve(httpRequest(originalRequest));
            });
          });
        }
        isRefreshing = true;
        await useUserStoreHook().refreshToken();
        isRefreshing = false;
        const newToken = Auth.getAccessToken();
        onRefreshed(newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return httpRequest(originalRequest);
      } catch (e) {
        isRefreshing = false;
        await redirectToLogin("登录已过期，请重新登录");
        return Promise.reject(new Error("未授权"));
      }
    } else {
      ElMessage.error(error.message || "请求异常");
      return Promise.reject(new Error(error.message || "请求异常"));
    }
  }
);

/**
 * 重定向到登录页面
 */
async function redirectToLogin(message: string = "请重新登录"): Promise<void> {
  try {
    ElNotification({
      title: "提示",
      message,
      type: "warning",
      duration: 3000,
    });

    await useUserStoreHook().resetAllState();

    // 跳转到登录页，保留当前路由用于登录后跳转
    const currentPath = router.currentRoute.value.fullPath;
    await router.push(`/login?redirect=${encodeURIComponent(currentPath)}`);
  } catch (error: any) {
    ElMessage.error(error.message);
  }
}

export default httpRequest;
