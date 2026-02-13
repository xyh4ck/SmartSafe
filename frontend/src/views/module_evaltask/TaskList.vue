<template>
  <div class="app-container p-4">
    <el-card shadow="never" class="mb-4">
      <el-form :inline="true" :model="query" @submit.prevent="handleQuery" class="search-form">
        <el-form-item label="任务名称">
          <el-input 
            v-model="query.name" 
            placeholder="请输入任务名称" 
            style="width: 240px" 
            clearable 
            :prefix-icon="Search"
          />
        </el-form-item>
        <el-form-item label="任务状态">
          <el-select v-model="query.status" placeholder="全部状态" style="width: 160px" clearable>
            <el-option label="全部" value="" />
            <el-option label="排队中" value="queued" />
            <el-option label="进行中" value="running" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
            <el-option label="部分完成" value="partial" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" native-type="submit">查询</el-button>
          <el-button :icon="Refresh" @click="handleResetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" class="data-table">
      <template #header>
        <div class="flex justify-between items-center">
          <div class="text-lg font-bold">评测任务管理</div>
          <div class="flex gap-2">
            <el-button type="primary" :icon="Plus" @click="openCreateDialog">新建任务</el-button>
            <el-button
              type="danger"
              plain
              :icon="Delete"
              :disabled="selectedTasks.length === 0"
              @click="handleBatchDelete"
            >
              批量删除
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="items"
        row-key="id"
        border
        stripe
        @selection-change="handleSelectionChange"
        class="w-full"
      >
        <template #empty>
          <el-empty :image-size="80" description="暂无数据" />
        </template>
        <el-table-column type="selection" width="50" align="center" />
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="name" label="任务名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="font-medium text-gray-700">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" effect="plain" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="评测用时" width="140" align="center">
          <template #default="{ row }">
            <span class="text-gray-600">{{ formatTaskDuration(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="进度" min-width="240">
          <template #default="{ row }">
            <div class="flex items-center">
              <el-progress 
                :percentage="computePercent(row)" 
                :status="row.status === 'failed' ? 'exception' : (row.status === 'completed' ? 'success' : '')"
                :stroke-width="8"
                :show-text="false"
                class="flex-1 mr-3"
              />
              <span class="text-xs text-gray-500 whitespace-nowrap">{{ row.finished_cases }}/{{ row.total_cases }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column fixed="right" label="操作" align="center" width="180">
          <template #default="{ row }">
            <el-button type="primary" link :icon="View" @click="goDetail(row.id)">
              详情
            </el-button>
            <el-button type="danger" link :icon="Delete" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="flex justify-end mt-4">
        <pagination
          v-model:total="total"
          v-model:page="query.page_no"
          v-model:limit="query.page_size"
          @pagination="loadData"
        />
      </div>
    </el-card>

    <!-- 新建任务对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="新建评测任务"
      width="900px"
      :close-on-click-modal="false"
      @close="handleDialogClose"
      destroy-on-close
      class="task-create-dialog"
    >
      <el-steps :active="currentStep" align-center finish-status="success" class="mb-8 mt-4 custom-steps">
        <el-step title="基本信息" :icon="Edit">
            <template #description>任务名称与描述</template>
        </el-step>
        <el-step title="模型配置" :icon="Cpu">
            <template #description>选择待测模型</template>
        </el-step>
        <el-step title="用例选择" :icon="Document">
             <template #description>配置评测策略</template>
        </el-step>
      </el-steps>

      <div class="px-4 min-h-[400px]">
        <el-form :model="taskForm" label-width="100px" label-position="top" size="large">
          <!-- 步骤1: 基本信息 -->
          <div v-show="currentStep === 0" class="step-content animate__animated animate__fadeIn">
             <div class="max-w-2xl mx-auto pt-8">
                <el-alert
                    title="请填写评测任务的基本信息"
                    type="info"
                    :closable="false"
                    show-icon
                    class="mb-6"
                />
                <el-form-item label="任务名称" required>
                  <el-input 
                    v-model="taskForm.name" 
                    placeholder="请输入任务名称，例如：金融助手安全性评测-2025Q1" 
                    size="large"
                    clearable
                    :prefix-icon="Edit"
                  />
                </el-form-item>
                <el-form-item label="任务描述">
                    <el-input
                        v-model="taskForm.description"
                        type="textarea"
                        :rows="4"
                        placeholder="请输入任务描述（可选）"
                    />
                </el-form-item>
             </div>
          </div>

          <!-- 步骤2: 模型配置 -->
          <div v-show="currentStep === 1" class="step-content animate__animated animate__fadeIn">
             <div class="max-w-3xl mx-auto">
                <el-form-item label="选择待测模型" required class="mb-6">
                  <el-select
                    v-model="taskForm.selectedModelId"
                    placeholder="请选择模型"
                    filterable
                    size="large"
                    style="width: 100%"
                    @change="handleModelChange"
                    class="custom-select"
                  >
                    <el-option
                      v-for="model in availableModels"
                      :key="model.id"
                      :label="`${model.name} (${model.provider})`"
                      :value="model.id!"
                    >
                      <div class="flex justify-between items-center w-full">
                        <span class="font-medium text-gray-700">{{ model.name }}</span>
                        <el-tag size="small" effect="plain" type="info">{{ model.provider }}</el-tag>
                      </div>
                    </el-option>
                  </el-select>
                </el-form-item>
                
                <div v-if="selectedModel" class="model-info-card bg-blue-50 p-6 rounded-lg border border-blue-100 transition-all duration-300">
                    <div class="flex items-center mb-4">
                        <div class="p-3 bg-white rounded-full shadow-sm mr-4 text-blue-500 flex items-center justify-center">
                            <el-icon :size="24"><Cpu /></el-icon>
                        </div>
                        <div>
                            <div class="text-lg font-bold text-gray-800">{{ selectedModel.name }}</div>
                            <div class="text-sm text-gray-500">{{ selectedModel.provider }}</div>
                        </div>
                    </div>
                    <el-descriptions :column="2" border size="default" class="bg-white">
                        <el-descriptions-item label="模型类型">{{ selectedModel.type || 'LLM' }}</el-descriptions-item>
                        <el-descriptions-item label="API Base" :span="2">
                            <span class="font-mono text-xs">{{ selectedModel.api_base || '-' }}</span>
                        </el-descriptions-item>
                        <el-descriptions-item label="版本">{{ selectedModel.version || 'Latest' }}</el-descriptions-item>
                    </el-descriptions>
                </div>
                 <el-empty v-if="!selectedModel" description="请先选择一个模型" :image-size="100"></el-empty>
             </div>
          </div>

          <!-- 步骤3: 用例输入 -->
          <div v-show="currentStep === 2" class="step-content animate__animated animate__fadeIn">
            <div class="selection-mode-card mb-6">
               <div class="text-sm font-medium text-gray-500 mb-3">选择策略</div>
               <el-radio-group v-model="taskForm.selectionMode" @change="handleSelectionModeChange" class="w-full flex gap-4" size="large">
                  <el-radio-button value="all" class="flex-1 !mr-0">
                     <span>全部风险维度</span>
                  </el-radio-button>
                  <el-radio-button value="dimensions" class="flex-1 !mr-0">
                     <span>按维度选择</span>
                  </el-radio-button>
                  <el-radio-button value="categories" class="flex-1 !mr-0">
                     <span>按分类选择</span>
                  </el-radio-button>
              </el-radio-group>
            </div>

            <!-- 过滤器区域 -->
            <div v-if="taskForm.selectionMode !== 'all'" class="filter-panel bg-gray-50 p-4 rounded-lg border border-gray-100 mb-4 transition-all duration-300">
                 <!-- 选择维度模式 -->
              <div v-if="taskForm.selectionMode === 'dimensions'">
                <span class="text-sm text-gray-600 mr-2">选择维度:</span>
                <el-select
                  v-model="taskForm.selectedDimensionIds"
                  placeholder="请选择风险维度（可多选）"
                  multiple
                  collapse-tags
                  collapse-tags-tooltip
                  style="width: 80%"
                  @change="handleDimensionsChange"
                >
                  <el-option
                    v-for="dim in dimensions"
                    :key="dim.dimension_id"
                    :label="dim.dimension_name"
                    :value="dim.dimension_id"
                  />
                </el-select>
              </div>

              <!-- 选择分类模式 -->
              <div v-if="taskForm.selectionMode === 'categories'" class="flex gap-4 items-center">
                <div class="w-1/2">
                    <span class="text-sm text-gray-600 block mb-1">风险维度</span>
                    <el-select
                    v-model="taskForm.selectedDimensionId"
                    placeholder="先选择风险维度"
                    clearable
                    style="width: 100%"
                    @change="handleDimensionChange"
                    >
                    <el-option
                        v-for="dim in dimensions"
                        :key="dim.dimension_id"
                        :label="dim.dimension_name"
                        :value="dim.dimension_id"
                    />
                    </el-select>
                </div>
                <div class="w-1/2">
                     <span class="text-sm text-gray-600 block mb-1">风险类别</span>
                    <el-select
                    v-model="taskForm.selectedCategoryIds"
                    placeholder="再选择风险类别（可多选）"
                    multiple
                    collapse-tags
                    collapse-tags-tooltip
                    style="width: 100%"
                    :disabled="!taskForm.selectedDimensionId"
                    @change="handleCategoriesChange"
                    >
                    <el-option
                        v-for="cat in filteredCategories"
                        :key="cat.id"
                        :label="cat.name"
                        :value="cat.id!"
                    />
                    </el-select>
                </div>
              </div>
            </div>

            <!-- 说明提示 -->
            <el-alert
              v-if="testCases.length > 0"
              title="以下所有用例将自动用于测试，无需手动选择"
              type="info"
              :closable="false"
              show-icon
              class="mb-4"
            />

            <!-- 用例列表 -->
            <div class="test-case-list border rounded-lg overflow-hidden shadow-sm">
                <div class="bg-gray-50 px-4 py-2 flex justify-between items-center border-b">
                    <div class="font-bold text-gray-700 flex items-center gap-2">
                        <el-icon class="text-primary"><Document /></el-icon>
                        用例列表
                    </div>
                    <div class="flex items-center gap-2">
                         <span class="text-xs text-gray-500">共计:</span>
                         <span class="text-lg font-bold text-primary">{{ testCases.length }}</span>
                         <span class="text-xs text-gray-400">条用例</span>
                    </div>
                </div>
                <el-table
                ref="testCaseTableRef"
                v-loading="loadingTestCases"
                :data="paginatedTestCases"
                height="350"
                stripe
                size="small"
                class="w-full"
                >
                <el-table-column type="index" label="序号" width="60" align="center" />
                <el-table-column
                    prop="prompt"
                    label="用例内容"
                    min-width="300"
                    show-overflow-tooltip
                >
                    <template #default="{ row }">
                         <div class="truncate font-mono text-xs">{{ row.prompt }}</div>
                    </template>
                </el-table-column>
                <el-table-column prop="risk_level" label="风险等级" width="100" align="center">
                    <template #default="{ row }">
                    <el-tag :type="getRiskLevelType(row.risk_level)" size="small" effect="light" round>
                        {{ row.risk_level }}
                    </el-tag>
                    </template>
                </el-table-column>
                 <el-table-column prop="category" label="分类" width="120" show-overflow-tooltip />
                </el-table>
                 <div class="flex justify-end p-2 bg-white border-t">
                    <el-pagination
                        v-model:current-page="testCaseCurrentPage"
                        v-model:page-size="testCasePageSize"
                        :page-sizes="[10, 20, 50, 100]"
                        :total="testCases.length"
                        layout="total, sizes, prev, pager, next"
                        size="small"
                        @size-change="handleTestCasePageSizeChange"
                        @current-change="handleTestCasePageChange"
                    />
                </div>
            </div>
          </div>
        </el-form>
      </div>

      <template #footer>
        <div class="dialog-footer flex justify-between items-center px-4 pb-2">
           <div class="text-gray-400 text-sm">
              <span v-if="currentStep===2">将测试 {{ testCases.length }} 条用例</span>
           </div>
           <div>
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button v-if="currentStep > 0" @click="prevStep" :icon="ArrowLeft">上一步</el-button>
                <el-button v-if="currentStep < 2" type="primary" @click="nextStep">
                    下一步 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
                </el-button>
                <el-button
                    v-if="currentStep === 2"
                    type="primary"
                    :loading="submitting"
                    @click="handleSubmit"
                >
                    提交评测
                </el-button>
            </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: "EvalTaskList", inheritAttrs: false });

import { ElMessage, ElMessageBox } from "element-plus";
import { 
  Search, Refresh, Plus, Delete, View, 
  Edit, Cpu, Document, ArrowLeft, ArrowRight 
} from "@element-plus/icons-vue";
import EvalTaskAPI, { EvalTaskItem } from "@/api/module_evaltask/task";
import ModelRegistryAPI, { type ModelItem } from "@/api/module_model/registry";
import CategoryAPI, {
  type DimensionCategoryTree,
  type CategoryTable,
} from "@/api/module_evaluation/category";
import TestCaseAPI, { type TestCaseTable } from "@/api/module_evaluation/testcase";
import router from "@/router";

const loading = ref(false);
const query = reactive({
  name: undefined as string | undefined,
  status: undefined as string | undefined,
  page_no: 1,
  page_size: 10,
  order_by: "created_at, desc",
});
const items = ref<EvalTaskItem[]>([]);
const total = ref(0);
const selectedTasks = ref<EvalTaskItem[]>([]);

// 新建任务对话框相关
const dialogVisible = ref(false);
const currentStep = ref(0);
const submitting = ref(false);
const taskForm = reactive({
  name: "",
  description: "",
  selectedModelId: undefined as number | undefined,
  selectionMode: "all" as "all" | "dimensions" | "categories",
  selectedDimensionId: undefined as number | undefined,
  selectedDimensionIds: [] as number[],
  selectedCategoryIds: [] as number[],
});

// 模型相关
const availableModels = ref<ModelItem[]>([]);
const selectedModel = computed(() =>
  availableModels.value.find((m) => m.id === taskForm.selectedModelId)
);

// 维度和类别相关
const dimensions = ref<DimensionCategoryTree[]>([]);
const filteredCategories = computed(() => {
  if (!taskForm.selectedDimensionId) return [];
  const dim = dimensions.value.find((d) => d.dimension_id === taskForm.selectedDimensionId);
  return dim?.categories || [];
});

// 测试用例相关
const loadingTestCases = ref(false);
const testCases = ref<TestCaseTable[]>([]);
const testCaseTableRef = ref();
// 测试用例分页
const testCaseCurrentPage = ref(1);
const testCasePageSize = ref(10);
const paginatedTestCases = computed(() => {
  const start = (testCaseCurrentPage.value - 1) * testCasePageSize.value;
  const end = start + testCasePageSize.value;
  return testCases.value.slice(start, end);
});

const statusTagType = (s: string) => {
  if (s === "completed") return "success";
  if (s === "running") return "primary";
  if (s === "queued") return "info";
  if (s === "failed") return "danger";
  if (s === "partial") return "warning";
  return "info";
};

const computePercent = (row: EvalTaskItem) => {
  if (!row.total_cases) return 0;
  return Math.round((row.finished_cases / row.total_cases) * 100);
};

const formatDuration = (ms: number) => {
  if (ms < 1000) return "0秒";
  const totalSeconds = Math.floor(ms / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  if (hours > 0) return `${hours}时${minutes}分${seconds}秒`;
  if (minutes > 0) return `${minutes}分${seconds}秒`;
  return `${seconds}秒`;
};

const formatTaskDuration = (row: EvalTaskItem) => {
  if (!row.started_at) return "-";
  const startedAt = new Date(row.started_at).getTime();
  if (Number.isNaN(startedAt)) return "-";

  const endTime = row.finished_at ? new Date(row.finished_at).getTime() : Date.now();
  if (Number.isNaN(endTime)) return "-";

  const durationText = formatDuration(Math.max(0, endTime - startedAt));
  if (!row.finished_at && row.status === "running") return `进行中 ${durationText}`;
  return durationText;
};

const getRiskLevelType = (level: string) => {
  if (level === "高" || level === "high") return "danger";
  if (level === "中" || level === "medium") return "warning";
  if (level === "低" || level === "low") return "info";
  return undefined;
};

const loadData = async () => {
  loading.value = true;
  try {
    const res = await EvalTaskAPI.getTasks(query);
    items.value = res.data.data?.items || [];
    total.value = res.data.data?.total || 0;
  } catch (e) {
    ElMessage.error("加载失败");
  } finally {
    loading.value = false;
  }
};

const handleQuery = async () => {
  query.page_no = 1;
  await loadData();
};

const handleResetQuery = async () => {
  query.name = undefined;
  query.status = undefined;
  query.page_no = 1;
  await loadData();
};

const goDetail = (id: number) => router.push(`/evaltask/detail/${id}`);

// 选择变化
const handleSelectionChange = (selection: EvalTaskItem[]) => {
  selectedTasks.value = selection;
};

// 删除单个任务
const handleDelete = async (row: EvalTaskItem) => {
  try {
    await ElMessageBox.confirm(`确定要删除任务 "${row.name}" 吗？`, "确认删除", {
      type: "warning",
    });
    await EvalTaskAPI.deleteTasks([row.id]);
    await loadData();
  } catch (e) {
    if (e !== "cancel") {
      ElMessage.error("删除失败");
    }
  }
};

// 批量删除任务
const handleBatchDelete = async () => {
  if (selectedTasks.value.length === 0) return;
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedTasks.value.length} 个任务吗？`,
      "确认删除",
      { type: "warning" }
    );
    const ids = selectedTasks.value.map((t) => t.id);
    await EvalTaskAPI.deleteTasks(ids);
    selectedTasks.value = [];
    await loadData();
  } catch (e) {
    if (e !== "cancel") {
      ElMessage.error("删除失败");
    }
  }
};

// 对话框相关函数
const openCreateDialog = async () => {
  dialogVisible.value = true;
  currentStep.value = 0;
  taskForm.name = "";
  taskForm.description = "";
  taskForm.selectedModelId = undefined;
  taskForm.selectionMode = "all";
  taskForm.selectedDimensionId = undefined;
  taskForm.selectedDimensionIds = [];
  taskForm.selectedCategoryIds = [];

  // 加载模型列表
  await loadModels();
  // 加载维度和类别树
  await loadDimensionsAndCategories();
};

const handleDialogClose = () => {
  currentStep.value = 0;
};

// 加载可用模型
const loadModels = async () => {
  try {
    const res = await ModelRegistryAPI.getList({ available: true, page_no: 1, page_size: 100 });
    availableModels.value = res.data?.data?.items || [];
  } catch (e) {
    ElMessage.error("加载模型列表失败");
  }
};

// 加载维度和类别树
const loadDimensionsAndCategories = async () => {
  try {
    const res = await CategoryAPI.getTree(true);
    dimensions.value = res.data?.data || [];
  } catch (e) {
    ElMessage.error("加载维度类别失败");
  }
};

// 模型选择变化
const handleModelChange = () => {
  // 可以在这里添加额外的逻辑
};

// 选择模式变化
const handleSelectionModeChange = async () => {
  // 清空之前的选择
  taskForm.selectedDimensionId = undefined;
  taskForm.selectedDimensionIds = [];
  taskForm.selectedCategoryIds = [];
  testCases.value = [];
  testCaseCurrentPage.value = 1;

  // 如果选择全部维度，立即加载所有用例
  if (taskForm.selectionMode === "all") {
    await loadTestCases();
  }
};

// 维度选择变化（单选，用于分类模式）
const handleDimensionChange = () => {
  taskForm.selectedCategoryIds = [];
  testCases.value = [];
  testCaseCurrentPage.value = 1;
};

// 多个维度选择变化
const handleDimensionsChange = async () => {
  if (taskForm.selectedDimensionIds.length === 0) {
    testCases.value = [];
    testCaseCurrentPage.value = 1;
    return;
  }
  testCaseCurrentPage.value = 1;
  // 加载选中维度下的所有测试用例
  await loadTestCases();
};

// 多个类别选择变化
const handleCategoriesChange = async () => {
  if (taskForm.selectedCategoryIds.length === 0) {
    testCases.value = [];
    testCaseCurrentPage.value = 1;
    return;
  }
  testCaseCurrentPage.value = 1;
  // 加载选中类别下的测试用例
  await loadTestCases();
};

// 加载测试用例
const loadTestCases = async () => {
  loadingTestCases.value = true;
  try {
    let query: any = {
      status: "true",
      page_no: 1,
      page_size: 100, // 增加页面大小以获取更多用例
    };

    // 根据选择模式构建查询参数
    if (taskForm.selectionMode === "all") {
      // 全部维度：不添加任何过滤条件
    } else if (taskForm.selectionMode === "dimensions") {
      // 选择维度：使用逗号分隔的维度ID列表
      if (taskForm.selectedDimensionIds.length === 0) return;
      query.dimension_ids = taskForm.selectedDimensionIds.join(",");
    } else if (taskForm.selectionMode === "categories") {
      // 选择分类：使用逗号分隔的分类ID列表
      if (taskForm.selectedCategoryIds.length === 0) return;
      query.category_ids = taskForm.selectedCategoryIds.join(",");
    }

    const res = await TestCaseAPI.page(query);
    testCases.value = res.data?.data?.items || [];
  } catch (e) {
    ElMessage.error("加载测试用例失败");
  } finally {
    loadingTestCases.value = false;
  }
};

// 测试用例选择变化（已废弃，自动使用所有筛选的用例）
const handleTestCaseSelection = (selection: TestCaseTable[]) => {
  // 不再需要手动选择，所有筛选出的用例都将被使用
};

// 测试用例分页变化
const handleTestCasePageChange = (page: number) => {
  testCaseCurrentPage.value = page;
};

const handleTestCasePageSizeChange = (size: number) => {
  testCasePageSize.value = size;
  testCaseCurrentPage.value = 1;
};

const nextStep = async () => {
  // 验证当前步骤
  if (currentStep.value === 0) {
    if (!taskForm.name.trim()) {
      ElMessage.warning("请填写任务名称");
      return;
    }
  } else if (currentStep.value === 1) {
    if (!taskForm.selectedModelId) {
      ElMessage.warning("请选择模型");
      return;
    }
    // 进入第三步时，如果是全部维度模式，自动加载用例
    if (taskForm.selectionMode === "all") {
      await loadTestCases();
    }
  } else if (currentStep.value === 2) {
    // 验证选择模式
    if (taskForm.selectionMode === "dimensions" && taskForm.selectedDimensionIds.length === 0) {
      ElMessage.warning("请至少选择一个风险维度");
      return;
    }
    if (taskForm.selectionMode === "categories") {
      if (!taskForm.selectedDimensionId) {
        ElMessage.warning("请选择风险维度");
        return;
      }
      if (taskForm.selectedCategoryIds.length === 0) {
        ElMessage.warning("请至少选择一个风险类别");
        return;
      }
    }
    if (testCases.value.length === 0) {
      ElMessage.warning("没有可用的测试用例，请检查筛选条件");
      return;
    }
  }

  if (currentStep.value < 2) {
    currentStep.value++;
  }
};

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
};

const handleSubmit = async () => {
  if (!taskForm.name.trim()) {
    ElMessage.error("请填写任务名称");
    return;
  }

  if (!taskForm.selectedModelId) {
    ElMessage.error("请选择模型");
    return;
  }

  if (testCases.value.length === 0) {
    ElMessage.error("没有可用的测试用例");
    return;
  }

  // 获取选中的模型信息
  const model = availableModels.value.find((m) => m.id === taskForm.selectedModelId);
  if (!model) {
    ElMessage.error("模型信息获取失败");
    return;
  }

  // 构建payload - 使用所有筛选出的测试用例
  const payload = {
    name: taskForm.name,
    cases: testCases.value.map((testCase) => ({
      prompt: testCase.prompt || "",
      llm_provider: model.provider,
      llm_params: {
        model: model.name,
        api_base: model.api_base,
      },
    })),
  };

  submitting.value = true;
  try {
    await EvalTaskAPI.createTask(payload);
    dialogVisible.value = false;
    await loadData();
  } catch (e) {
    ElMessage.error("创建任务失败");
  } finally {
    submitting.value = false;
  }
};

onMounted(loadData);
</script>

<style scoped>
.task-create-dialog :deep(.el-dialog__body) {
  padding-top: 10px;
  padding-bottom: 10px;
}

.custom-steps :deep(.el-step__head.is-success) {
  color: var(--el-color-primary);
  border-color: var(--el-color-primary);
}

.custom-steps :deep(.el-step__title.is-success) {
  color: var(--el-color-primary);
}

.selection-mode-card :deep(.el-radio-button__inner) {
  width: 100%;
  border: 1px solid var(--el-border-color);
  border-radius: 4px !important;
  box-shadow: none !important;
  padding: 10px;
  height: auto;
  line-height: 1.5;
}

.selection-mode-card :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  border-color: var(--el-color-primary);
  box-shadow: none;
}

.test-case-list :deep(.el-table__inner-wrapper::before) {
    display: none;
}
</style>
