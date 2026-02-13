<template>
  <div class="p-4">
    <el-card shadow="never" class="mb-4">
      <template #header>
        <div class="flex-x-between">
          <div class="flex items-center">
            <span>任务详情</span>
            <el-tag :type="statusTagType(progress?.status || '')" class="ml-3" effect="dark">
              {{ progress?.status || "未知状态" }}
            </el-tag>
          </div>
          <div>
            <el-button :icon="Refresh" @click="refresh(false)" :loading="manualLoading">
              刷新
            </el-button>
            <el-button
              type="primary"
              :icon="DataAnalysis"
              @click="goReport"
              :disabled="!canViewReport"
            >
              查看报告
            </el-button>
          </div>
        </div>
      </template>

      <!-- 任务进度概览 -->
      <div class="flex items-center justify-between py-2">
        <div class="flex flex-col flex-1 mr-8">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-700">执行进度</span>
            <div class="flex items-center text-sm">
              <span
                class="font-bold mr-1"
                :class="progress?.status === 'failed' ? 'text-red-500' : 'text-primary'"
              >
                {{ progress?.percent || 0 }}%
              </span>
              <span class="text-gray-400">
                ({{ progress?.finished || 0 }}/{{ progress?.total || 0 }})
              </span>
            </div>
          </div>
          <el-progress
            :percentage="progress?.percent || 0"
            :status="
              progress?.status === 'failed'
                ? 'exception'
                : progress?.status === 'completed'
                  ? 'success'
                  : ''
            "
            :stroke-width="10"
            :show-text="false"
            class="progress-custom"
          />
        </div>

        <el-descriptions :column="3" border class="flex-1">
          <el-descriptions-item label="任务ID">{{ taskId }}</el-descriptions-item>
          <el-descriptions-item label="总用例数">{{ progress?.total || 0 }}</el-descriptions-item>
          <el-descriptions-item label="已完成">{{ progress?.finished || 0 }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <div v-if="progress?.status === 'completed'" class="mt-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <!-- 总数卡片 -->
          <div class="bg-blue-50 rounded-lg p-4 flex items-center border border-blue-100">
            <el-icon class="text-blue-500 text-2xl mr-3 bg-blue-100 p-2 rounded-full w-10 h-10 box-content">
              <Tickets />
            </el-icon>
            <div>
              <div class="text-gray-500 text-xs mb-1">测试用例总数</div>
              <div class="text-2xl font-bold text-gray-800">
                {{ resultSummary?.total_cases ?? progress?.total ?? 0 }}
              </div>
            </div>
          </div>

          <!-- 执行状态卡片 -->
          <div class="bg-gray-50 rounded-lg p-4 flex flex-col justify-center border border-gray-200">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center">
                <el-icon class="text-green-500 mr-1"><CircleCheckFilled /></el-icon>
                <span class="text-gray-600 text-sm">成功</span>
              </div>
              <span class="font-bold text-gray-800">{{ resultSummary?.succeeded_cases ?? '-' }}</span>
            </div>
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <el-icon class="text-red-500 mr-1"><CircleCloseFilled /></el-icon>
                <span class="text-gray-600 text-sm">失败</span>
              </div>
              <span class="font-bold text-gray-800">{{ resultSummary?.failed_cases ?? '-' }}</span>
            </div>
          </div>

          <!-- 合格率卡片 -->
          <div class="bg-purple-50 rounded-lg p-4 flex items-center border border-purple-100">
            <el-icon class="text-purple-500 text-2xl mr-3 bg-purple-100 p-2 rounded-full w-10 h-10 box-content">
              <PieChart />
            </el-icon>
            <div>
              <div class="text-gray-500 text-xs mb-1">合格率 (Low)</div>
              <div class="text-2xl font-bold text-purple-600">
                {{ resultSummary?.qualified_rate ?? 0 }}%
              </div>
            </div>
          </div>
        </div>

        <!-- 风险分布条 -->
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <div class="text-sm font-bold text-gray-700 mb-3 flex items-center">
            <span class="mr-2">风险分布</span>
            <el-tooltip content="基于风险等级的分布情况" placement="top">
              <el-icon class="text-gray-400 cursor-pointer text-xs"><InfoFilled /></el-icon>
            </el-tooltip>
          </div>
          
          <!-- 进度条可视化 -->
          <div class="flex h-3 rounded-full overflow-hidden bg-gray-100 mb-3">
            <div 
              v-if="(resultSummary?.level_distribution?.Low || 0) > 0"
              class="bg-green-500 h-full transition-all duration-500 hover:opacity-90"
              :style="{ width: `${((resultSummary?.level_distribution?.Low || 0) / (resultSummary?.total_cases || 1)) * 100}%` }"
              :title="`Low: ${resultSummary?.level_distribution?.Low}`"
            ></div>
            <div 
              v-if="(resultSummary?.level_distribution?.Medium || 0) > 0"
              class="bg-yellow-400 h-full transition-all duration-500 hover:opacity-90"
              :style="{ width: `${((resultSummary?.level_distribution?.Medium || 0) / (resultSummary?.total_cases || 1)) * 100}%` }"
              :title="`Medium: ${resultSummary?.level_distribution?.Medium}`"
            ></div>
            <div 
              v-if="(resultSummary?.level_distribution?.High || 0) > 0"
              class="bg-orange-500 h-full transition-all duration-500 hover:opacity-90"
              :style="{ width: `${((resultSummary?.level_distribution?.High || 0) / (resultSummary?.total_cases || 1)) * 100}%` }"
              :title="`High: ${resultSummary?.level_distribution?.High}`"
            ></div>
            <div 
              v-if="(resultSummary?.level_distribution?.Critical || 0) > 0"
              class="bg-red-600 h-full transition-all duration-500 hover:opacity-90"
              :style="{ width: `${((resultSummary?.level_distribution?.Critical || 0) / (resultSummary?.total_cases || 1)) * 100}%` }"
              :title="`Critical: ${resultSummary?.level_distribution?.Critical}`"
            ></div>
          </div>

          <!-- 图例 -->
          <div class="flex flex-wrap gap-4 text-xs">
            <div class="flex items-center">
              <span class="w-2 h-2 rounded-full bg-green-500 mr-1.5"></span>
              <span class="text-gray-600">Low</span>
              <span class="ml-1 font-bold text-gray-800">{{ resultSummary?.level_distribution?.Low ?? 0 }}</span>
            </div>
            <div class="flex items-center">
              <span class="w-2 h-2 rounded-full bg-yellow-400 mr-1.5"></span>
              <span class="text-gray-600">Medium</span>
              <span class="ml-1 font-bold text-gray-800">{{ resultSummary?.level_distribution?.Medium ?? 0 }}</span>
            </div>
            <div class="flex items-center">
              <span class="w-2 h-2 rounded-full bg-orange-500 mr-1.5"></span>
              <span class="text-gray-600">High</span>
              <span class="ml-1 font-bold text-gray-800">{{ resultSummary?.level_distribution?.High ?? 0 }}</span>
            </div>
            <div class="flex items-center">
              <span class="w-2 h-2 rounded-full bg-red-600 mr-1.5"></span>
              <span class="text-gray-600">Critical</span>
              <span class="ml-1 font-bold text-gray-800">{{ resultSummary?.level_distribution?.Critical ?? 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <el-card shadow="never">
      <template #header>
        <div class="font-bold">执行明细</div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="用例明细" name="cases">
          <el-table :data="cases" stripe v-loading="loading">
            <el-table-column
              type="index"
              label="序号"
              width="80"
              align="center"
              :index="(index) => (query.page_no - 1) * query.page_size + index + 1"
            />
            <el-table-column prop="prompt" label="提示词" min-width="240">
              <template #default="{ row }">
                <div class="truncate-2-lines">{{ row.prompt }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="风险等级" width="120" align="center">
              <template #default="{ row }">
                <ResultRiskTags :level="row.risk_level" />
              </template>
            </el-table-column>
            <el-table-column prop="output_text" label="模型输出" min-width="300">
              <template #default="{ row }">
                <div class="truncate-2-lines text-gray-500">{{ row.output_text || "-" }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="total_tokens" label="Token消耗" width="150" align="center">
              <template #default="{ row }">
                <div v-if="row.total_tokens">
                  <el-tag type="info" size="small" effect="plain">{{ row.total_tokens }}</el-tag>
                </div>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right" align="center">
              <template #default="{ row }">
                <el-button
                  link
                  type="primary"
                  :icon="View"
                  @click="viewOutput(row)"
                  :disabled="!row.output_text && !row.prompt"
                >
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="flex justify-end mt-4">
            <pagination
              :total="total"
              :page="query.page_no"
              :limit="query.page_size"
              @update:page="query.page_no = $event"
              @update:limit="query.page_size = $event"
              @pagination="refresh"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="执行日志" name="logs">
          <div class="mb-4 flex items-center gap-3">
            <el-select
              v-model="logQuery.stage"
              placeholder="全部阶段"
              clearable
              style="width: 180px"
              @change="handleLogFilterChange"
            >
              <el-option label="create" value="create" />
              <el-option label="start" value="start" />
              <el-option label="generate" value="generate" />
              <el-option label="complete" value="complete" />
              <el-option label="error" value="error" />
            </el-select>
            <el-select
              v-model="logQuery.level"
              placeholder="全部级别"
              clearable
              style="width: 160px"
              @change="handleLogFilterChange"
            >
              <el-option label="INFO" value="INFO" />
              <el-option label="WARNING" value="WARNING" />
              <el-option label="ERROR" value="ERROR" />
            </el-select>
            <el-button @click="loadTaskLogs" :icon="Refresh" :loading="logLoading">刷新日志</el-button>
          </div>

          <el-empty v-if="!logLoading && logs.length === 0" description="暂无日志" :image-size="90" />

          <el-timeline v-else v-loading="logLoading">
            <el-timeline-item
              v-for="item in logs"
              :key="item.id"
              :timestamp="formatLogTime(item.created_at)"
              placement="top"
              :type="item.level === 'ERROR' ? 'danger' : item.level === 'WARNING' ? 'warning' : 'primary'"
            >
              <el-card shadow="never" class="log-card">
                <div class="flex items-center gap-2 mb-2">
                  <el-tag size="small" effect="plain">{{ item.stage }}</el-tag>
                  <el-tag size="small" :type="levelTagType(item.level)">{{ item.level }}</el-tag>
                  <el-tag v-if="item.case_id" size="small" type="info" effect="plain">
                    用例 #{{ item.case_id }}
                  </el-tag>
                </div>
                <div class="text-gray-700 whitespace-pre-wrap break-words">{{ item.message }}</div>
              </el-card>
            </el-timeline-item>
          </el-timeline>

          <div class="flex justify-end mt-4">
            <pagination
              :total="logTotal"
              :page="logQuery.page_no"
              :limit="logQuery.page_size"
              @update:page="logQuery.page_no = $event"
              @update:limit="logQuery.page_size = $event"
              @pagination="loadTaskLogs"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 输出详情抽屉 -->
    <el-drawer
      v-model="outputDialogVisible"
      title="详情查看"
      size="900px"
      :close-on-click-modal="true"
      destroy-on-close
    >
      <el-descriptions :column="2" border class="mb-4">
        <el-descriptions-item label="用例ID">{{ currentCase?.id }}</el-descriptions-item>
        <el-descriptions-item label="执行状态">
          <el-tag :type="statusTagType(currentCase?.status || '')" size="small">
            {{ currentCase?.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="风险等级">
          <ResultRiskTags :level="currentCase?.risk_level" />
        </el-descriptions-item>
        <el-descriptions-item label="Token统计">
          <span class="text-xs text-gray-500">
            提示: {{ currentCase?.prompt_tokens || 0 }} / 完成:
            {{ currentCase?.completion_tokens || 0 }} / 总计: {{ currentCase?.total_tokens || 0 }}
          </span>
        </el-descriptions-item>
      </el-descriptions>

      <div
        v-if="currentCase?.llm_params && Object.keys(currentCase.llm_params).length > 0"
        class="content-block mb-4"
      >
        <div class="content-header flex-x-between">
          <span class="font-bold text-gray-700">模型参数</span>
          <el-button
            type="primary"
            link
            :icon="CopyDocument"
            @click="copyText(JSON.stringify(currentCase?.llm_params, null, 2))"
          >
            复制
          </el-button>
        </div>
        <div class="content-body prompt-bg">
          {{ JSON.stringify(currentCase?.llm_params, null, 2) }}
        </div>
      </div>

      <div class="content-block mb-4">
        <div class="content-header flex-x-between">
          <span class="font-bold text-gray-700">提示词</span>
          <el-button
            type="primary"
            link
            :icon="CopyDocument"
            @click="copyText(currentCase?.prompt || '')"
          >
            复制
          </el-button>
        </div>
        <div class="content-body prompt-bg">
          <Vue3MarkdownIt :source="currentCase?.prompt || ''" />
        </div>
      </div>

      <div class="content-block">
        <div class="content-header flex-x-between">
          <span class="font-bold text-gray-700">模型输出</span>
          <el-button
            type="primary"
            link
            :icon="CopyDocument"
            @click="copyText(currentCase?.output_text || '')"
          >
            复制
          </el-button>
        </div>
        <div class="content-body output-bg">
          <Vue3MarkdownIt :source="currentCase?.output_text || '暂无输出'" />
        </div>
      </div>

      <div v-if="deepteamItems.length > 0" class="content-block mt-4">
        <div class="content-header flex-x-between">
          <span class="font-bold text-gray-700">风险评分</span>
          <el-button type="primary" link :icon="CopyDocument" @click="copyText(deepteamItemsText)">
            复制
          </el-button>
        </div>
        <div class="content-body risk-bg">
          <el-table :data="deepteamItems" size="small" border>
            <el-table-column prop="name" label="风险类型" min-width="180" />
            <el-table-column label="风险判定" width="100" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.score === 0" type="danger" effect="dark" size="small">
                  有风险
                </el-tag>
                <el-tag v-else-if="row.score === 1" type="success" effect="dark" size="small">
                  无风险
                </el-tag>
                <el-tag v-else type="info" size="small">未知</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <div v-if="currentCase?.risk_reason" class="content-block mt-4">
        <div class="content-header flex-x-between">
          <span class="font-bold text-gray-700">风险分析</span>
          <el-button
            type="primary"
            link
            :icon="CopyDocument"
            @click="copyText(currentCase?.risk_reason || '')"
          >
            复制
          </el-button>
        </div>
        <div class="content-body risk-bg">
          <Vue3MarkdownIt :source="currentCase?.risk_reason || ''" />
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: "EvalTaskDetail", inheritAttrs: false });

import { ref, reactive, computed, onMounted, onUnmounted } from "vue";
import { ElMessage } from "element-plus";
import { useRoute } from "vue-router";
import {
  Refresh,
  DataAnalysis,
  View,
  CopyDocument,
  Tickets,
  CircleCheckFilled,
  CircleCloseFilled,
  PieChart,
  InfoFilled,
} from "@element-plus/icons-vue";
import EvalTaskAPI, {
  EvalTaskCaseItem,
  EvalTaskLogItem,
  EvalTaskProgress,
  EvalTaskResult,
} from "@/api/module_evaltask/task";
import ResultRiskTags from "./components/ResultRiskTags.vue";
import router from "@/router";
import Vue3MarkdownIt from "vue3-markdown-it";
import "highlight.js/styles/github.css";

const route = useRoute();
const taskId = Number(route.params.taskId as string);
const progress = ref<EvalTaskProgress | null>(null);
const result = ref<EvalTaskResult | null>(null);
const cases = ref<EvalTaskCaseItem[]>([]);
const total = ref(0);
const query = reactive({
  page_no: 1,
  page_size: 10,
});
const timer = ref<number | null>(null);
const progressEtag = ref<string | null>(null);
const casesEtag = ref<string | null>(null);
const outputDialogVisible = ref(false);
const currentCase = ref<EvalTaskCaseItem | null>(null);
const loading = ref(false);
const manualLoading = ref(false);
const activeTab = ref<"cases" | "logs">("cases");
const logs = ref<EvalTaskLogItem[]>([]);
const logTotal = ref(0);
const logLoading = ref(false);
const logQuery = reactive({
  page_no: 1,
  page_size: 10,
  stage: undefined as string | undefined,
  level: undefined as string | undefined,
  case_id: undefined as number | undefined,
});

const resultSummary = computed(() => (result.value?.summary || {}) as any);

const deepteamItems = computed(() => {
  const rs = currentCase.value?.risk_scores || {};
  const items: { name: string; score: number }[] = [];
  for (const [k, v] of Object.entries(rs)) {
    if (!k.startsWith("deepteam:")) continue;
    const name = k.slice("deepteam:".length) || k;
    const score = typeof v === "number" ? v : Number(v);
    if (Number.isFinite(score)) items.push({ name, score });
  }
  return items.sort((a, b) => b.score - a.score);
});

const deepteamItemsText = computed(() => {
  return deepteamItems.value.map((x) => `${x.name}=${x.score}`).join("\n");
});

const statusTagType = (s: string) => {
  if (s === "succeeded" || s === "completed") return "success";
  if (s === "running") return "primary";
  if (s === "queued") return "info";
  if (s === "failed") return "danger";
  if (s === "partial") return "warning";
  return "info";
};

const levelTagType = (level: string) => {
  if (level === "ERROR") return "danger";
  if (level === "WARNING") return "warning";
  return "info";
};

const formatLogTime = (value?: string | null) => {
  if (!value) return "-";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString();
};

const loadTaskLogs = async () => {
  logLoading.value = true;
  try {
    const res = await EvalTaskAPI.getTaskLogs(taskId, logQuery);
    logs.value = res.data.data?.items || [];
    logTotal.value = res.data.data?.total || 0;
  } catch {
    ElMessage.error("加载日志失败");
  } finally {
    logLoading.value = false;
  }
};

const handleLogFilterChange = async () => {
  logQuery.page_no = 1;
  await loadTaskLogs();
};

const refresh = async (silent = true) => {
  // silent=true 用于轮询刷新：不展示 loading、也不弹错误提示，避免界面闪烁
  if (!silent) {
    loading.value = true;
    manualLoading.value = true;
  }
  try {
    const pg = await EvalTaskAPI.getTaskProgress(taskId, {
      headers: progressEtag.value ? { "If-None-Match": progressEtag.value } : undefined,
    });
    if (pg.status !== 304) {
      const newProgress = pg.data.data || progress.value;
      progress.value = newProgress || null;
      const newPgEtag = (pg.headers?.etag as string) || (pg.headers?.ETag as string) || null;
      if (newPgEtag) progressEtag.value = newPgEtag;
    }

    const cs = await EvalTaskAPI.getTaskCases(
      taskId,
      { page_no: query.page_no, page_size: query.page_size },
      { headers: casesEtag.value ? { "If-None-Match": casesEtag.value } : undefined }
    );
    if (cs.status !== 304) {
      cases.value = (cs.data.data?.items || cases.value || []) as EvalTaskCaseItem[];
      total.value = cs.data.data?.total || 0;
      const newCsEtag = (cs.headers?.etag as string) || (cs.headers?.ETag as string) || null;
      if (newCsEtag) casesEtag.value = newCsEtag;
    }

    const status = progress.value?.status;
    const finished = progress.value?.finished ?? 0;
    const totalCases = progress.value?.total ?? 0;
    const polling =
      progress.value?.polling ??
      (status !== "completed" && status !== "failed" && status !== "partial" && finished < totalCases);

    if ((status === "completed" || status === "partial" || status === "failed") && !result.value) {
      try {
        const rr = await EvalTaskAPI.getTaskResult(taskId);
        result.value = rr.data.data || null;
      } catch (e) {
        console.error(e);
      }
    }

    if (!polling && timer.value) {
      window.clearInterval(timer.value);
      timer.value = null;
      console.log(`任务 ${taskId} 已完成，停止轮询`);
    } else if (polling && !timer.value) {
      timer.value = window.setInterval(() => refresh(true), 5000);
    }
  } catch (e) {
    console.error(e);
    if (!silent) {
      ElMessage.error("加载失败");
    }
  } finally {
    if (!silent) {
      loading.value = false;
      manualLoading.value = false;
    }
  }
};

const canViewReport = computed(() => {
  const status = progress.value?.status;
  return status === "completed" || status === "partial";
});
const goReport = () => router.push(`/evaltask/report/${taskId}`);

const viewOutput = (row: EvalTaskCaseItem) => {
  currentCase.value = row;
  outputDialogVisible.value = true;
};

const copyText = async (text?: string) => {
  if (!text) {
    ElMessage.warning("没有可复制的内容");
    return;
  }
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success("复制成功");
  } catch {
    ElMessage.error("复制失败");
  }
};

onMounted(() => {
  refresh(false);
  loadTaskLogs();
});

onUnmounted(() => {
  if (timer.value) window.clearInterval(timer.value);
});
</script>

<style scoped>
.truncate-2-lines {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.5;
}

.content-block {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.content-header {
  background-color: #f5f7fa;
  padding: 8px 12px;
  border-bottom: 1px solid #dcdfe6;
}

.content-body {
  padding: 12px;
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
  font-family: "Menlo", "Monaco", "Courier New", monospace;
  font-size: 13px;
}

/* 覆盖 Markdown 样式以适配内容区 */
.content-body :deep(h1),
.content-body :deep(h2),
.content-body :deep(h3),
.content-body :deep(h4) {
  margin: 10px 0 8px;
  font-weight: 700;
  line-height: 1.35;
}

.content-body :deep(h1) {
  font-size: 18px;
}
.content-body :deep(h2) {
  font-size: 16px;
}
.content-body :deep(h3) {
  font-size: 14px;
}

.content-body :deep(pre) {
  padding: 12px;
  margin: 10px 0;
  overflow-x: auto;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 6px;
}

.content-body :deep(code) {
  font-family: "Menlo", "Monaco", "Courier New", monospace;
  font-size: 13px;
}

.prompt-bg {
  background-color: #ffffff;
}

.output-bg {
  background-color: #fcfcfc;
}

.risk-bg {
  background-color: #fff8f0;
}

.log-card {
  border-color: #ebeef5;
}
</style>
