<template>
  <div class="app-container">
    <el-card class="search-container">
      <el-form
        ref="queryFormRef"
        :model="queryFormData"
        :inline="true"
        label-suffix=":"
        @submit.prevent="handleQuery"
      >
        <el-form-item prop="refusal_expectation" label="题库类型">
          <el-select
            v-model="queryFormData.refusal_expectation"
            placeholder="请选择"
            clearable
            style="width: 180px"
          >
            <el-option label="应拒答" value="should_refuse" />
            <el-option label="非拒答" value="should_not_refuse" />
          </el-select>
        </el-form-item>
        <el-form-item prop="status" label="状态">
          <el-select
            v-model="queryFormData.status"
            placeholder="请选择"
            clearable
            style="width: 150px"
          >
            <el-option label="待审核" value="pending_review" />
            <el-option label="已通过" value="approved" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item prop="gen_batch_id" label="批次">
          <el-input
            v-model="queryFormData.gen_batch_id"
            placeholder="生成批次ID"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item class="search-buttons">
          <el-button type="primary" icon="search" @click="handleQuery">查询</el-button>
          <el-button icon="refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>候选题池</span>
          <div class="header-actions">
            <el-button type="primary" :icon="DataAnalysis" @click="handleOpenCoverage">
              覆盖度统计
            </el-button>
            <el-button type="success" :icon="MagicStick" @click="handleOpenGenerate">
              自动生成
            </el-button>
          </div>
        </div>
      </template>

      <div class="data-table__toolbar">
        <div class="data-table__toolbar--left">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-button
                type="success"
                icon="check"
                :disabled="selectIds.length === 0"
                @click="handleBatchReview('approve')"
              >
                批量通过
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                type="danger"
                icon="close"
                :disabled="selectIds.length === 0"
                @click="handleBatchReview('reject')"
              >
                批量驳回
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                type="primary"
                icon="upload"
                :disabled="approvedIds.length === 0"
                @click="handlePublish"
              >
                发布入库 ({{ approvedIds.length }})
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete"
              >
                删除
              </el-button>
            </el-col>
          </el-row>
        </div>
      </div>

      <el-table
        :data="pageTableData"
        v-loading="loading"
        class="data-table__content"
        height="450"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="refusal_expectation" label="题库类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.refusal_expectation === 'should_refuse' ? 'danger' : 'success'">
              {{ row.refusal_expectation === "should_refuse" ? "应拒答" : "非拒答" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dimension_name" label="维度" width="120" show-overflow-tooltip />
        <el-table-column prop="category_name" label="分类" width="120" show-overflow-tooltip />
        <el-table-column label="测试Prompt" min-width="250">
          <template #default="{ row }">
            <el-tooltip v-if="row.prompt" effect="dark" :content="row.prompt" placement="top">
              <div
                style="
                  overflow: hidden;
                  text-overflow: ellipsis;
                  white-space: nowrap;
                  max-width: 100%;
                "
              >
                {{ row.prompt }}
              </div>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="risk_level" label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskLevelType(row.risk_level)">
              {{ getRiskLevelText(row.risk_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="gen_batch_id" label="批次" width="180" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button
              v-if="row.status === 'pending_review'"
              type="success"
              link
              @click="handleSingleReview(row, 'approve')"
            >
              通过
            </el-button>
            <el-button
              v-if="row.status === 'pending_review'"
              type="danger"
              link
              @click="handleSingleReview(row, 'reject')"
            >
              驳回
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <pagination
          v-model:total="total"
          v-model:page="queryFormData.page_no"
          v-model:limit="queryFormData.page_size"
          @pagination="handleQuery"
        />
      </template>
    </el-card>

    <!-- 查看详情抽屉 -->
    <el-drawer v-model="drawerVisible" title="候选题详情" size="500px" direction="rtl">
      <el-descriptions :column="1" border v-if="viewData">
        <el-descriptions-item label="ID">{{ viewData.id }}</el-descriptions-item>
        <el-descriptions-item label="维度">
          {{ viewData.dimension_name || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="分类">
          {{ viewData.category_name || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="题库类型">
          <el-tag :type="viewData.refusal_expectation === 'should_refuse' ? 'danger' : 'success'">
            {{ viewData.refusal_expectation === "should_refuse" ? "应拒答" : "非拒答" }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="风险等级">
          <el-tag :type="getRiskLevelType(viewData.risk_level)">
            {{ getRiskLevelText(viewData.risk_level) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(viewData.status)">
            {{ getStatusText(viewData.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="测试Prompt">
          <div style="white-space: pre-wrap; word-break: break-all">
            {{ viewData.prompt || "-" }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="期望行为">
          <div style="white-space: pre-wrap; word-break: break-all">
            {{ viewData.expected_behavior || "-" }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="拒答理由">
          <div style="white-space: pre-wrap; word-break: break-all">
            {{ viewData.refusal_reason || "-" }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="审核备注">
          {{ viewData.review_note || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="批次ID">
          {{ viewData.gen_batch_id || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ viewData.created_at || "-" }}
        </el-descriptions-item>
      </el-descriptions>
    </el-drawer>

    <!-- 覆盖度统计弹窗 -->
    <el-dialog
      v-model="coverageDialogVisible"
      title="题库覆盖度统计"
      width="800px"
      destroy-on-close
    >
      <div v-loading="coverageLoading">
        <el-tabs>
          <el-tab-pane label="应拒答题库">
            <el-alert type="info" :closable="false" style="margin-bottom: 16px">
              <p>总量：{{ coverageData?.should_refuse?.total || 0 }} 题（要求 ≥ 500）</p>
              <p>
                缺口分类：{{ coverageData?.should_refuse?.gaps?.length || 0 }} 个（每类要求 ≥ 20）
              </p>
            </el-alert>
            <el-table :data="coverageData?.should_refuse?.gaps || []" border max-height="300">
              <el-table-column prop="category_name" label="分类名称" />
              <el-table-column prop="current" label="当前数量" width="100" />
              <el-table-column prop="required" label="要求数量" width="100" />
              <el-table-column prop="gap" label="缺口" width="100">
                <template #default="{ row }">
                  <el-tag type="danger">-{{ row.gap }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="非拒答题库">
            <el-alert type="info" :closable="false" style="margin-bottom: 16px">
              <p>总量：{{ coverageData?.should_not_refuse?.total || 0 }} 题（要求 ≥ 500）</p>
              <p>
                缺口方面：{{ coverageData?.should_not_refuse?.gaps?.length || 0 }} 个（每方面要求 ≥
                20）
              </p>
            </el-alert>
            <el-table :data="coverageData?.should_not_refuse?.gaps || []" border max-height="300">
              <el-table-column prop="aspect" label="方面" />
              <el-table-column prop="current" label="当前数量" width="100" />
              <el-table-column prop="required" label="要求数量" width="100" />
              <el-table-column prop="gap" label="缺口" width="100">
                <template #default="{ row }">
                  <el-tag type="danger">-{{ row.gap }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <!-- 自动生成弹窗 -->
    <el-dialog
      v-model="generateDialogVisible"
      title="自动生成候选题"
      width="500px"
      destroy-on-close
    >
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="题库类型" required>
          <el-select
            v-model="generateForm.refusal_expectation"
            placeholder="请选择"
            style="width: 100%"
          >
            <el-option label="应拒答" value="should_refuse" />
            <el-option label="非拒答" value="should_not_refuse" />
          </el-select>
        </el-form-item>
        <el-form-item label="每类数量">
          <el-input-number v-model="generateForm.count_per_category" :min="1" :max="50" />
        </el-form-item>
        <el-alert type="warning" :closable="false" style="margin-top: 16px">
          将根据覆盖度缺口自动选择分类并生成候选题，生成后需人工审核。
        </el-alert>
      </el-form>
      <template #footer>
        <el-button @click="generateDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="generateLoading" @click="handleConfirmGenerate">
          确认生成
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: "TestCaseCandidateList", inheritAttrs: false });

import TestCaseCandidateAPI, {
  TestCaseCandidateTable,
  TestCaseCandidatePageQuery,
  CoverageResult,
} from "@/api/module_evaluation/testcase_candidate";
import { formatToDateTime } from "@/utils/dateUtil";
import { ElMessage, ElMessageBox } from "element-plus";
import { DataAnalysis, MagicStick } from "@element-plus/icons-vue";

const queryFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const approvedIds = ref<number[]>([]);
const loading = ref(false);
const pageTableData = ref<TestCaseCandidateTable[]>([]);
const drawerVisible = ref(false);
const viewData = ref<TestCaseCandidateTable | null>(null);

// 覆盖度统计
const coverageDialogVisible = ref(false);
const coverageLoading = ref(false);
const coverageData = ref<CoverageResult | null>(null);

// 自动生成
const generateDialogVisible = ref(false);
const generateLoading = ref(false);
const generateForm = reactive({
  refusal_expectation: "should_refuse",
  count_per_category: 5,
});

const queryFormData = reactive<TestCaseCandidatePageQuery>({
  page_no: 1,
  page_size: 10,
  refusal_expectation: undefined,
  status: undefined,
  gen_batch_id: undefined,
});

async function handleQuery() {
  loading.value = true;
  try {
    const { data } = (await TestCaseCandidateAPI.page(queryFormData)).data;
    pageTableData.value = (data?.items ?? []).map((r: any) => ({
      ...r,
      created_at: r.created_at ? formatToDateTime(r.created_at) : "",
    }));
    total.value = data?.total ?? 0;
  } finally {
    loading.value = false;
  }
}

function resetQuery() {
  queryFormData.refusal_expectation = undefined;
  queryFormData.status = undefined;
  queryFormData.gen_batch_id = undefined;
  queryFormData.page_no = 1;
  handleQuery();
}

function handleSelectionChange(rows: TestCaseCandidateTable[]) {
  selectIds.value = rows.map((r) => r.id!);
  approvedIds.value = rows.filter((r) => r.status === "approved").map((r) => r.id!);
}

function handleView(row: TestCaseCandidateTable) {
  viewData.value = { ...row };
  drawerVisible.value = true;
}

async function handleBatchReview(action: "approve" | "reject") {
  if (selectIds.value.length === 0) return;
  const actionText = action === "approve" ? "通过" : "驳回";
  try {
    await ElMessageBox.confirm(
      `确定要${actionText}选中的 ${selectIds.value.length} 条候选题吗？`,
      "确认操作",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );
    await TestCaseCandidateAPI.review({ ids: selectIds.value, action });
    ElMessage.success(`${actionText}成功`);
    handleQuery();
  } catch (error: any) {
    if (error !== "cancel") {
      ElMessage.error(`${actionText}失败`);
    }
  }
}

async function handleSingleReview(row: TestCaseCandidateTable, action: "approve" | "reject") {
  const actionText = action === "approve" ? "通过" : "驳回";
  try {
    await TestCaseCandidateAPI.review({ ids: [row.id!], action });
    ElMessage.success(`${actionText}成功`);
    handleQuery();
  } catch {
    ElMessage.error(`${actionText}失败`);
  }
}

async function handlePublish() {
  if (approvedIds.value.length === 0) return;
  try {
    await ElMessageBox.confirm(
      `确定要将 ${approvedIds.value.length} 条已通过的候选题发布到正式库吗？`,
      "确认发布",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );
    const result = await TestCaseCandidateAPI.publish({ ids: approvedIds.value });
    const data = result.data?.data || {};
    ElMessage.success(`发布完成！成功 ${data.created || 0} 条，跳过 ${data.skipped || 0} 条`);
    handleQuery();
  } catch (error: any) {
    if (error !== "cancel") {
      ElMessage.error("发布失败");
    }
  }
}

async function handleDelete() {
  if (selectIds.value.length === 0) return;
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectIds.value.length} 条候选题吗？`,
      "确认删除",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );
    await TestCaseCandidateAPI.delete(selectIds.value);
    ElMessage.success("删除成功");
    handleQuery();
  } catch (error: any) {
    if (error !== "cancel") {
      ElMessage.error("删除失败");
    }
  }
}

async function handleOpenCoverage() {
  coverageDialogVisible.value = true;
  coverageLoading.value = true;
  try {
    const result = await TestCaseCandidateAPI.coverage();
    coverageData.value = result.data?.data || null;
  } finally {
    coverageLoading.value = false;
  }
}

function handleOpenGenerate() {
  generateDialogVisible.value = true;
}

async function handleConfirmGenerate() {
  generateLoading.value = true;
  try {
    const result = await TestCaseCandidateAPI.generate({
      refusal_expectation: generateForm.refusal_expectation,
      count_per_category: generateForm.count_per_category,
    });
    const data = result.data?.data || {};
    ElMessage.success(`生成完成！批次: ${data.batch_id}，生成 ${data.generated || 0} 条`);
    generateDialogVisible.value = false;
    handleQuery();
  } catch {
    ElMessage.error("生成失败");
  } finally {
    generateLoading.value = false;
  }
}

function getRiskLevelType(
  riskLevel?: string
): "danger" | "warning" | "success" | "info" | undefined {
  if (!riskLevel) return undefined;
  const level = riskLevel.toLowerCase();
  if (level === "high") return "danger";
  if (level === "medium") return "warning";
  if (level === "low") return "success";
  return undefined;
}

function getRiskLevelText(riskLevel?: string) {
  if (!riskLevel) return "-";
  const level = riskLevel.toLowerCase();
  if (level === "high") return "高";
  if (level === "medium") return "中";
  if (level === "low") return "低";
  return riskLevel;
}

function getStatusType(status?: string) {
  if (status === "pending_review") return "warning";
  if (status === "approved") return "success";
  if (status === "rejected") return "danger";
  return "info";
}

function getStatusText(status?: string) {
  if (status === "pending_review") return "待审核";
  if (status === "approved") return "已通过";
  if (status === "rejected") return "已驳回";
  if (status === "published") return "已发布";
  return status || "-";
}

onMounted(() => {
  handleQuery();
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-actions {
  display: flex;
  gap: 10px;
}
</style>
