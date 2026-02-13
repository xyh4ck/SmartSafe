<template>
  <div class="app-container">
    <el-row :gutter="16">
      <!-- 左侧分类树 -->
      <el-col :span="5">
        <el-card class="tree-card">
          <template #header>
            <div class="card-header">
              <span>风险分类</span>
            </div>
          </template>
          <el-tree
            ref="treeRef"
            :data="treeData"
            :props="{ children: 'children', label: 'label' }"
            node-key="key"
            :default-expand-all="false"
            :highlight-current="true"
            @node-click="handleTreeNodeClick"
            class="filter-tree"
          >
            <template #default="{ node, data }">
              <span class="tree-node-label">
                <el-icon v-if="data.key === 'all'" style="margin-right: 4px"><Menu /></el-icon>
                <el-icon v-else-if="data.type === 'dimension'" style="margin-right: 4px">
                  <Folder />
                </el-icon>
                <el-icon v-else style="margin-right: 4px"><Document /></el-icon>
                {{ node.label }}
              </span>
            </template>
          </el-tree>
        </el-card>
      </el-col>

      <!-- 右侧内容区域 -->
      <el-col :span="19">
        <div class="search-container">
          <el-form
            ref="queryFormRef"
            :model="queryFormData"
            :inline="true"
            label-suffix=":"
            @submit.prevent="handleQuery"
          >
            <el-form-item prop="dimension_id" label="维度">
              <el-select
                v-model="queryFormData.dimension_id"
                placeholder="请选择维度"
                clearable
                style="width: 200px"
                @change="handleQueryDimensionChange"
              >
                <el-option
                  v-for="dim in dimensions"
                  :key="dim.id!"
                  :label="dim.name"
                  :value="dim.id!"
                />
              </el-select>
            </el-form-item>
            <el-form-item prop="category_id" label="分类">
              <el-select
                v-model="queryFormData.category_id"
                placeholder="请选择分类"
                clearable
                style="width: 200px"
                :disabled="!queryFormData.dimension_id"
              >
                <el-option
                  v-for="cat in queryCategories"
                  :key="cat.id!"
                  :label="cat.name"
                  :value="cat.id!"
                />
              </el-select>
            </el-form-item>
            <el-form-item prop="risk_level" label="风险等级">
              <el-select
                v-model="queryFormData.risk_level"
                placeholder="请选择风险等级"
                clearable
                style="width: 200px"
              >
                <el-option label="高/High" value="high" />
                <el-option label="中/Medium" value="medium" />
                <el-option label="低/Low" value="low" />
              </el-select>
            </el-form-item>
            <el-form-item prop="refusal_expectation" label="题库类型">
              <el-select
                v-model="queryFormData.refusal_expectation"
                placeholder="请选择"
                clearable
                style="width: 150px"
              >
                <el-option label="应拒答" value="should_refuse" />
                <el-option label="非拒答" value="should_not_refuse" />
              </el-select>
            </el-form-item>
            <el-form-item class="search-buttons">
              <el-button type="primary" icon="search" @click="handleQuery">查询</el-button>
              <el-button icon="refresh" @click="resetQuery">重置</el-button>
            </el-form-item>
          </el-form>
        </div>

        <el-card class="data-table">
          <template #header>
            <div class="card-header">
              <span>测试用例列表</span>
            </div>
          </template>

          <div class="data-table__toolbar">
            <div class="data-table__toolbar--left">
              <el-row :gutter="10">
                <el-col :span="1.5">
                  <el-button type="success" icon="plus" @click="handleOpenDialog('create')">
                    新增
                  </el-button>
                </el-col>
                <el-col :span="1.5">
                  <el-button
                    type="danger"
                    icon="delete"
                    :disabled="selectIds.length === 0"
                    @click="handleDelete(selectIds)"
                  >
                    批量删除
                  </el-button>
                </el-col>
                <el-col :span="1.5">
                  <el-button type="warning" :icon="Upload" @click="handleOpenImportDialog">
                    导入
                  </el-button>
                </el-col>
                <el-col :span="1.5">
                  <el-button :icon="Download" @click="handleExport">导出</el-button>
                </el-col>
              </el-row>
            </div>
          </div>

          <el-table
            :data="pageTableData"
            v-loading="loading"
            class="data-table__content"
            height="550"
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="50" />
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column label="维度" min-width="120">
              <template #default="{ row }">
                {{ getDimensionName(row.dimension_id) }}
              </template>
            </el-table-column>
            <el-table-column label="分类" min-width="120">
              <template #default="{ row }">
                {{ getCategoryName(row.category_id) }}
              </template>
            </el-table-column>
            <el-table-column label="测试Prompt" min-width="200">
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
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="risk_level" label="风险等级" min-width="100">
              <template #default="{ row }">
                <el-tag v-if="row.risk_level" :type="getRiskLevelType(row.risk_level) || undefined">
                  {{ getRiskLevelText(row.risk_level) }}
                </el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="refusal_expectation" label="题库类型" width="100">
              <template #default="{ row }">
                <el-tag
                  v-if="row.refusal_expectation"
                  :type="row.refusal_expectation === 'should_refuse' ? 'danger' : 'success'"
                >
                  {{ row.refusal_expectation === "should_refuse" ? "应拒答" : "非拒答" }}
                </el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="version" label="版本" width="80" />
            <el-table-column prop="status" label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="row.status ? 'success' : 'info'">
                  {{ row.status ? "启用" : "停用" }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="creator.name" label="创建人" min-width="120" />
            <el-table-column prop="created_at" label="创建时间" min-width="160" />
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleView(row)">查看</el-button>
                <el-button type="primary" link @click="handleOpenDialog('update', row)">
                  编辑
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
      </el-col>
    </el-row>

    <el-dialog
      v-model="dialogVisible.visible"
      :title="dialogVisible.title"
      width="700px"
      destroy-on-close
    >
      <el-form ref="dataFormRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item prop="dimension_id" label="维度" required>
          <el-select
            v-model="formData.dimension_id"
            placeholder="请选择维度"
            style="width: 100%"
            @change="handleDimensionChange"
          >
            <el-option
              v-for="dim in dimensions"
              :key="dim.id!"
              :label="dim.name"
              :value="dim.id!"
            />
          </el-select>
        </el-form-item>
        <el-form-item prop="category_id" label="分类" required>
          <el-select
            v-model="formData.category_id"
            placeholder="请先选择维度"
            style="width: 100%"
            :disabled="!formData.dimension_id"
          >
            <el-option
              v-for="cat in categories"
              :key="cat.id!"
              :label="cat.name"
              :value="cat.id!"
            />
          </el-select>
        </el-form-item>
        <el-form-item prop="risk_level" label="风险等级" required>
          <el-select v-model="formData.risk_level" placeholder="请选择风险等级" style="width: 100%">
            <el-option label="高/High" value="high" />
            <el-option label="中/Medium" value="medium" />
            <el-option label="低/Low" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item prop="refusal_expectation" label="题库类型">
          <el-select
            v-model="formData.refusal_expectation"
            placeholder="请选择题库类型"
            clearable
            style="width: 100%"
          >
            <el-option label="应拒答" value="should_refuse" />
            <el-option label="非拒答" value="should_not_refuse" />
          </el-select>
        </el-form-item>
        <el-form-item prop="tags" label="标签">
          <el-select
            v-model="formData.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入后回车新增"
          ></el-select>
        </el-form-item>
        <el-form-item prop="status" label="状态">
          <el-switch v-model="formData.status" />
        </el-form-item>
        <el-form-item prop="prompt" label="测试Prompt" required>
          <el-input
            v-model="formData.prompt"
            type="textarea"
            :rows="4"
            placeholder="请输入测试Prompt"
          />
        </el-form-item>
        <el-form-item prop="expected_behavior" label="期望行为">
          <el-input
            v-model="formData.expected_behavior"
            type="textarea"
            :rows="3"
            placeholder="请输入期望行为"
          />
        </el-form-item>
        <el-form-item prop="description" label="备注">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="2"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible.visible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入测试用例" width="800px" destroy-on-close>
      <div class="import-container">
        <el-alert title="导入说明" type="info" :closable="false" style="margin-bottom: 20px">
          <p>1. 请先下载模板，按照模板格式填写数据</p>
          <p>2. 类别和子类别必须与系统中已有的维度和分类名称完全一致</p>
          <p>3. 风险等级可填写：高、中、低（或 high、medium、low）</p>
          <p>4. 状态可填写：启用、停用（或 true、false）</p>
          <p>5. 多个标签用英文逗号分隔</p>
        </el-alert>

        <div class="import-actions" style="margin-bottom: 20px">
          <el-button type="primary" :icon="Download" @click="handleDownloadTemplate">
            下载导入模板
          </el-button>
        </div>

        <el-upload
          v-model:file-list="importFileList"
          class="upload-container"
          drag
          :limit="1"
          accept=".xlsx"
          :auto-upload="false"
          :before-upload="beforeUpload"
          :on-change="handleFileChange"
        >
          <el-icon class="el-icon--upload"><Upload /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处或
            <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">仅支持.xlsx格式的Excel文件，文件大小不超过10MB</div>
          </template>
        </el-upload>

        <!-- 预览数据 -->
        <div v-if="showPreview && importPreviewData.length > 0" class="preview-container">
          <el-divider>数据预览（共 {{ importPreviewData.length }} 条）</el-divider>
          <el-table :data="importPreviewData.slice(0, 5)" border :max-height="300">
            <el-table-column prop="prompt" label="提示词" min-width="200" show-overflow-tooltip />
            <el-table-column prop="risk_level" label="风险等级" width="100">
              <template #default="{ row }">
                <el-tag :type="getRiskLevelType(row.risk_level) || undefined">
                  {{ getRiskLevelText(row.risk_level) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status ? 'success' : 'info'">
                  {{ row.status ? "启用" : "停用" }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="importPreviewData.length > 5" class="preview-tip">
            仅显示前5条，实际将导入 {{ importPreviewData.length }} 条数据
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="importLoading"
          :disabled="importPreviewData.length === 0"
          @click="handleConfirmImport"
        >
          确认导入
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看详情抽屉 -->
    <el-drawer v-model="drawerVisible" title="测试用例详情" size="500px" direction="rtl">
      <el-descriptions :column="1" border v-if="viewData">
        <el-descriptions-item label="ID">{{ viewData.id }}</el-descriptions-item>
        <el-descriptions-item label="维度">
          <el-tag>{{ getDimensionName(viewData.dimension_id) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="分类">
          <el-tag type="success">{{ getCategoryName(viewData.category_id) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="风险等级">
          <el-tag :type="getRiskLevelType(viewData.risk_level) || undefined">
            {{ viewData.risk_level }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="版本">
          <el-tag type="info">v{{ viewData.version }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="viewData.status ? 'success' : 'info'">
            {{ viewData.status ? "启用" : "停用" }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="标签" v-if="viewData.tags && viewData.tags.length > 0">
          <el-tag v-for="tag in viewData.tags" :key="tag" style="margin-right: 8px">
            {{ tag }}
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
        <el-descriptions-item label="备注">
          <div style="white-space: pre-wrap; word-break: break-all">
            {{ viewData.description || "-" }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="创建人">
          {{ viewData.creator?.name || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ viewData.created_at || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ viewData.updated_at || "-" }}
        </el-descriptions-item>
      </el-descriptions>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: "EvaluationTestCase", inheritAttrs: false });

import TestCaseAPI, {
  TestCaseTable,
  TestCaseForm,
  TestCasePageQuery,
} from "@/api/module_evaluation/testcase";
import DimensionAPI, { DimensionTable } from "@/api/module_evaluation/dimension";
import CategoryAPI, { CategoryTable } from "@/api/module_evaluation/category";
import { formatToDateTime } from "@/utils/dateUtil";
import { ElMessage, ElMessageBox, type UploadProps, type UploadFile } from "element-plus";
import { Folder, Document, Menu, Upload, Download } from "@element-plus/icons-vue";
import ExcelJS from "exceljs";

const queryFormRef = ref();
const dataFormRef = ref();
const treeRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const loading = ref(false);

const pageTableData = ref<TestCaseTable[]>([]);

// 维度和分类数据
const dimensions = ref<DimensionTable[]>([]);
const categories = ref<CategoryTable[]>([]); // 用于编辑表单的动态分类
const queryCategories = ref<CategoryTable[]>([]); // 用于查询表单的分类列表
const allCategoriesMap = ref<Map<number, CategoryTable>>(new Map()); // 用于表格显示的全局分类映射

// 分类树数据
interface TreeNode {
  key: string;
  label: string;
  type: "dimension" | "category";
  dimension_id?: number;
  category_id?: number;
  children?: TreeNode[];
}

const treeData = ref<TreeNode[]>([]);

const queryFormData = reactive<TestCasePageQuery>({
  page_no: 1,
  page_size: 10,
  dimension_id: undefined,
  category_id: undefined,
  category: undefined,
  risk_level: undefined,
  refusal_expectation: undefined,
});

const formData = reactive<TestCaseForm>({
  id: undefined,
  dimension_id: undefined,
  category_id: undefined,
  prompt: "",
  expected_behavior: undefined,
  risk_level: "",
  tags: [],
  status: true,
  description: undefined,
  refusal_expectation: undefined,
});

const dialogVisible = reactive({ title: "", visible: false });
const drawerVisible = ref(false);
const viewData = ref<TestCaseTable | null>(null);

// 导入对话框相关状态
const importDialogVisible = ref(false);
const importFileList = ref<UploadFile[]>([]);
const importLoading = ref(false);
const importPreviewData = ref<TestCaseForm[]>([]);
const showPreview = ref(false);

// 表单验证规则
const formRules = {
  dimension_id: [{ required: true, message: "请选择风险维度", trigger: "change" }],
  category_id: [{ required: true, message: "请选择风险分类", trigger: "change" }],
  risk_level: [{ required: true, message: "请选择风险等级", trigger: "change" }],
  prompt: [
    { required: true, message: "请输入测试Prompt", trigger: "blur" },
    { min: 1, max: 2000, message: "长度在 1 到 2000 个字符", trigger: "blur" },
  ],
};

async function handleQuery() {
  loading.value = true;
  try {
    const { data } = (await TestCaseAPI.page(queryFormData)).data;
    pageTableData.value = (data?.items ?? []).map((r: any) => ({
      ...r,
      created_at: r.created_at ? formatToDateTime(r.created_at) : "",
      updated_at: r.updated_at ? formatToDateTime(r.updated_at) : "",
    }));
    total.value = data?.total ?? 0;

    // 收集所有唯一的 dimension_id 和 category_id，批量加载分类
    const dimensionIds = new Set<number>();
    const categoryIds = new Set<number>();
    pageTableData.value.forEach((row) => {
      if (row.dimension_id) dimensionIds.add(row.dimension_id);
      if (row.category_id) categoryIds.add(row.category_id);
    });

    // 批量加载分类数据
    if (dimensionIds.size > 0) {
      await loadAllCategoriesForDimensions(Array.from(dimensionIds));
    }
  } finally {
    loading.value = false;
  }
}

function resetQuery() {
  queryFormData.dimension_id = undefined;
  queryFormData.category_id = undefined;
  queryFormData.category = undefined;
  queryFormData.risk_level = undefined;
  queryFormData.refusal_expectation = undefined;
  queryFormData.page_no = 1;
  queryCategories.value = [];
  // 取消树的选中状态
  if (treeRef.value) {
    treeRef.value.setCurrentKey(null);
  }
  handleQuery();
}

async function handleQueryDimensionChange(dimensionId: number) {
  // 清空分类选择
  queryFormData.category_id = undefined;
  // 加载对应维度的分类
  if (dimensionId) {
    try {
      const response = await CategoryAPI.getByDimension(dimensionId, true);
      queryCategories.value = response.data?.data ?? [];
      // 同步树的选中状态
      if (treeRef.value) {
        treeRef.value.setCurrentKey(`dimension_${dimensionId}`);
      }
    } catch (error) {
      console.error("加载分类失败:", error);
      queryCategories.value = [];
    }
  } else {
    queryCategories.value = [];
    // 取消树的选中状态
    if (treeRef.value) {
      treeRef.value.setCurrentKey(null);
    }
  }
}

// 监听查询表单变化，同步树节点选中状态
watch(
  () => [queryFormData.dimension_id, queryFormData.category_id],
  ([dimensionId, categoryId]) => {
    if (treeRef.value) {
      if (categoryId && dimensionId) {
        // 选中分类节点
        treeRef.value.setCurrentKey(`category_${categoryId}`);
      } else if (dimensionId) {
        // 只选中维度节点
        treeRef.value.setCurrentKey(`dimension_${dimensionId}`);
      } else if (!dimensionId && !categoryId) {
        // 没有选中任何维度或分类时，选中"全部"节点
        treeRef.value.setCurrentKey("all");
      }
    }
  }
);

function handleSelectionChange(rows: TestCaseTable[]) {
  selectIds.value = rows.map((r) => r.id!);
}

async function handleOpenDialog(type: "create" | "update", row?: TestCaseTable) {
  if (type === "create") {
    // 重置表单数据
    Object.assign(formData, {
      id: undefined,
      dimension_id: undefined,
      category_id: undefined,
      prompt: "",
      expected_behavior: undefined,
      risk_level: "",
      tags: [],
      status: true,
      description: undefined,
    });

    dialogVisible.title = "新增用例";

    // 根据当前查询条件自动填充维度和分类
    if (queryFormData.dimension_id) {
      formData.dimension_id = queryFormData.dimension_id;
      // 加载该维度的分类列表
      await loadCategories(queryFormData.dimension_id);

      // 如果查询条件中也有分类ID，自动填充
      if (queryFormData.category_id) {
        formData.category_id = queryFormData.category_id;
      }
    } else {
      // 如果没有选择维度，重置分类列表
      categories.value = [];
    }
  } else {
    Object.assign(formData, { ...row, tags: row?.tags ?? [] });
    dialogVisible.title = "编辑用例";
    // 如果已有维度ID，加载对应的分类
    if (formData.dimension_id) {
      await loadCategories(formData.dimension_id);
    }
  }
  dialogVisible.visible = true;
}

async function handleDimensionChange(dimensionId: number) {
  // 清空分类选择
  formData.category_id = undefined;
  // 加载对应维度的分类
  if (dimensionId) {
    await loadCategories(dimensionId);
  } else {
    categories.value = [];
  }
}

async function loadCategories(dimensionId: number) {
  try {
    const response = await CategoryAPI.getByDimension(dimensionId, true);
    categories.value = response.data?.data ?? [];
  } catch (error) {
    console.error("加载分类失败:", error);
    categories.value = [];
  }
}

async function loadAllCategoriesForDimensions(dimensionIds: number[]) {
  try {
    // 并行加载所有维度的分类
    const promises = dimensionIds.map((dimensionId) =>
      CategoryAPI.getByDimension(dimensionId, true)
    );
    const responses = await Promise.all(promises);

    // 将所有分类存储到 Map 中，以 category_id 为 key
    responses.forEach((response) => {
      const categoryList = response.data?.data ?? [];
      categoryList.forEach((cat) => {
        if (cat.id) {
          allCategoriesMap.value.set(cat.id, cat);
        }
      });
    });
  } catch (error) {
    console.error("批量加载分类失败:", error);
  }
}

async function loadDimensions() {
  try {
    const response = await DimensionAPI.getAllActive();
    dimensions.value = response.data?.data ?? [];
    // 加载维度后，构建分类树
    await buildTreeData();
  } catch (error) {
    console.error("加载维度失败:", error);
    dimensions.value = [];
  }
}

// 构建分类树数据
async function buildTreeData() {
  const tree: TreeNode[] = [
    // 添加"全部"根节点
    {
      key: "all",
      label: "全部",
      type: "dimension",
    },
  ];

  // 优化：使用新的 tree 接口，一次性获取所有维度和分类数据
  try {
    const response = await CategoryAPI.getTree(false);
    const treeList = response.data?.data ?? [];

    for (const item of treeList) {
      // 只显示启用的维度
      if (!item.dimension_status) continue;

      const dimensionNode: TreeNode = {
        key: `dimension_${item.dimension_id}`,
        label: item.dimension_name || "",
        type: "dimension",
        dimension_id: item.dimension_id,
        children: [],
      };

      // 映射分类数据
      dimensionNode.children = (item.categories || []).map((cat) => ({
        key: `category_${cat.id}`,
        label: cat.name || "",
        type: "category",
        dimension_id: item.dimension_id,
        category_id: cat.id,
      }));

      // 如果有分类，才添加到树中
      if (dimensionNode.children.length > 0) {
        tree.push(dimensionNode);
      }
    }
  } catch (error) {
    console.error("加载维度分类树失败:", error);
  }

  treeData.value = tree;
}

// 树节点点击处理
async function handleTreeNodeClick(data: TreeNode) {
  if (data.key === "all") {
    // 点击"全部"：清空所有筛选条件
    queryFormData.dimension_id = undefined;
    queryFormData.category_id = undefined;
    queryFormData.category = undefined;
    queryCategories.value = [];
  } else if (data.type === "dimension" && data.dimension_id) {
    // 点击维度：设置维度ID，清空分类ID
    queryFormData.dimension_id = data.dimension_id;
    queryFormData.category_id = undefined;
    // 加载该维度的分类到查询下拉框
    handleQueryDimensionChange(data.dimension_id);
  } else if (data.type === "category" && data.dimension_id && data.category_id) {
    // 点击分类：设置维度和分类ID
    queryFormData.dimension_id = data.dimension_id;
    queryFormData.category_id = data.category_id;
    // 加载该维度的分类到查询下拉框（但不清空已设置的category_id）
    try {
      const response = await CategoryAPI.getByDimension(data.dimension_id, true);
      queryCategories.value = response.data?.data ?? [];
      // 同步树的选中状态
      if (treeRef.value) {
        treeRef.value.setCurrentKey(`category_${data.category_id}`);
      }
    } catch (error) {
      console.error("加载分类失败:", error);
      queryCategories.value = [];
    }
  }
  // 自动触发查询
  handleQuery();
}

async function handleSubmit() {
  // 表单验证
  if (!dataFormRef.value) return;

  try {
    await dataFormRef.value.validate();

    // 验证通过，提交数据
    if (formData.id) {
      await TestCaseAPI.update(formData.id, formData);
      ElMessage.success("更新成功");
    } else {
      await TestCaseAPI.create(formData);
      ElMessage.success("创建成功");
    }
    dialogVisible.visible = false;
    handleQuery();
  } catch (error) {
    console.error("表单验证失败:", error);
    ElMessage.warning("请检查表单填写是否完整");
  }
}

async function handleDelete(ids: number[]) {
  await TestCaseAPI.delete(ids);
  handleQuery();
}

async function handleView(row: TestCaseTable) {
  viewData.value = { ...row };
  // 如果有维度ID，加载对应的分类数据
  if (row.dimension_id) {
    await loadCategories(row.dimension_id);
  }
  drawerVisible.value = true;
}

function getDimensionName(dimensionId?: number) {
  if (!dimensionId) return "-";
  const dimension = dimensions.value.find((d) => d.id === dimensionId);
  return dimension?.name || "-";
}

function getCategoryName(categoryId?: number) {
  if (!categoryId) return "-";
  // 先从全局 Map 中查找（用于表格显示）
  const categoryFromMap = allCategoriesMap.value.get(categoryId);
  if (categoryFromMap) return categoryFromMap.name || "-";
  // 如果 Map 中没有，再从表单的分类列表中查找（用于编辑表单）
  const category = categories.value.find((c) => c.id === categoryId);
  return category?.name || "-";
}

function getRiskLevelType(riskLevel?: string) {
  if (!riskLevel) return "";
  const level = riskLevel.toLowerCase();
  if (level === "high" || level === "高") return "danger";
  if (level === "medium" || level === "中") return "warning";
  if (level === "low" || level === "低") return "success";
  return "";
}

function getRiskLevelText(riskLevel?: string) {
  if (!riskLevel) return "-";
  const level = riskLevel.toLowerCase();
  if (level === "high" || level === "高") return "高/High";
  if (level === "medium" || level === "中") return "中/Medium";
  if (level === "low" || level === "低") return "低/Low";
  return riskLevel;
}

// 打开导入对话框
function handleOpenImportDialog() {
  importDialogVisible.value = true;
  importFileList.value = [];
  importPreviewData.value = [];
  showPreview.value = false;
}

// 文件上传前的校验
const beforeUpload: UploadProps["beforeUpload"] = (file) => {
  const isExcel =
    file.type === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ||
    file.name.endsWith(".xlsx");
  if (!isExcel) {
    ElMessage.error("只支持上传.xlsx格式的Excel文件！");
    return false;
  }
  const isLt10M = file.size / 1024 / 1024 < 10;
  if (!isLt10M) {
    ElMessage.error("文件大小不能超过10MB！");
    return false;
  }
  return true;
};

// 处理文件上传
const handleFileChange: UploadProps["onChange"] = async (uploadFile) => {
  if (!uploadFile.raw) return;

  importLoading.value = true;
  try {
    const data = await parseExcelFile(uploadFile.raw);
    if (data.length === 0) {
      ElMessage.warning("Excel文件中没有有效数据");
      importFileList.value = [];
      return;
    }
    importPreviewData.value = data;
    showPreview.value = true;
    ElMessage.success(`成功解析${data.length}条记录`);
  } catch (error: any) {
    console.error("解析文件失败:", error);
    ElMessage.error("解析文件失败: " + (error.message || "未知错误"));
    importFileList.value = [];
    showPreview.value = false;
  } finally {
    importLoading.value = false;
  }
};

// 解析Excel文件
async function parseExcelFile(file: File): Promise<TestCaseForm[]> {
  const workbook = new ExcelJS.Workbook();
  const arrayBuffer = await file.arrayBuffer();
  await workbook.xlsx.load(arrayBuffer);

  const worksheet = workbook.worksheets[0];
  if (!worksheet) {
    throw new Error("Excel文件中没有工作表");
  }

  const data: TestCaseForm[] = [];
  const headerRow = worksheet.getRow(1);

  // 定义字段映射（Excel列名 -> 数据字段）
  const fieldMapping: Record<string, string> = {
    类别: "category",
    子类别: "subcategory",
    提示词: "prompt",
    期望行为: "expected_behavior",
    风险等级: "risk_level",
    标签: "tags",
    状态: "status",
    描述: "description",
  };

  // 获取列索引映射
  const columnIndexMap: Record<string, number> = {};
  headerRow.eachCell((cell, colNumber) => {
    const headerName = cell.value?.toString().trim();
    if (headerName && fieldMapping[headerName]) {
      columnIndexMap[fieldMapping[headerName]] = colNumber;
    }
  });

  // 验证必需字段
  if (!columnIndexMap["prompt"]) {
    throw new Error("Excel文件缺少必需列：提示词");
  }

  // 解析数据行
  worksheet.eachRow((row, rowNumber) => {
    if (rowNumber === 1) return; // 跳过表头

    const prompt = row.getCell(columnIndexMap["prompt"])?.value?.toString().trim();
    if (!prompt) return; // 跳过空行

    // 解析风险等级
    let risk_level =
      row
        .getCell(columnIndexMap["risk_level"] || 999)
        ?.value?.toString()
        .trim() || "medium";
    if (risk_level === "高") risk_level = "high";
    else if (risk_level === "中") risk_level = "medium";
    else if (risk_level === "低") risk_level = "low";

    // 解析状态
    const statusCell = row
      .getCell(columnIndexMap["status"] || 999)
      ?.value?.toString()
      .trim();
    const status = statusCell === "启用" || statusCell === "true" || statusCell === "1";

    // 解析标签
    const tagsCell = row
      .getCell(columnIndexMap["tags"] || 999)
      ?.value?.toString()
      .trim();
    const tags = tagsCell
      ? tagsCell
          .split(",")
          .map((t) => t.trim())
          .filter((t) => t)
      : [];

    // 从类别和子类别查找对应的维度和分类ID
    const category = row
      .getCell(columnIndexMap["category"] || 999)
      ?.value?.toString()
      .trim();
    const subcategory = row
      .getCell(columnIndexMap["subcategory"] || 999)
      ?.value?.toString()
      .trim();

    // 查找维度ID（根据category名称）
    const dimension = dimensions.value.find((d) => d.name === category);
    if (!dimension) {
      console.warn(`第${rowNumber}行: 找不到维度"${category}"`);
      return;
    }

    // 这里需要加载该维度的分类，但由于是同步遍历，我们先记录下来，后续批量处理
    data.push({
      dimension_id: dimension.id,
      category_id: undefined, // 稍后填充
      prompt,
      expected_behavior:
        row
          .getCell(columnIndexMap["expected_behavior"] || 999)
          ?.value?.toString()
          .trim() || undefined,
      risk_level,
      tags: tags.length > 0 ? tags : undefined,
      status,
      description:
        row
          .getCell(columnIndexMap["description"] || 999)
          ?.value?.toString()
          .trim() || undefined,
      _subcategory: subcategory, // 临时字段，用于后续查找
    } as any);
  });

  // 批量加载所有维度的分类数据，填充category_id
  const dimensionIds = new Set(
    data.map((item) => item.dimension_id).filter((id) => id !== undefined)
  );
  const categoryMapByDimension = new Map<number, CategoryTable[]>();

  for (const dimensionId of dimensionIds) {
    try {
      const response = await CategoryAPI.getByDimension(dimensionId!, true);
      const categories = response.data?.data ?? [];
      categoryMapByDimension.set(dimensionId!, categories);
    } catch (error) {
      console.error(`加载维度${dimensionId}的分类失败:`, error);
    }
  }

  // 填充category_id
  const validData: TestCaseForm[] = [];
  for (const item of data) {
    if (!item.dimension_id) continue;

    const categories = categoryMapByDimension.get(item.dimension_id);
    if (!categories) {
      console.warn(`维度${item.dimension_id}没有分类数据`);
      continue;
    }

    const category = categories.find((c) => c.name === (item as any)._subcategory);
    if (!category) {
      console.warn(`找不到分类"${(item as any)._subcategory}"`);
      continue;
    }

    item.category_id = category.id;
    delete (item as any)._subcategory;
    validData.push(item);
  }

  return validData;
}

// 确认导入
async function handleConfirmImport() {
  if (importPreviewData.value.length === 0) {
    ElMessage.warning("没有可导入的数据");
    return;
  }

  try {
    await ElMessageBox.confirm(
      `确定要导入${importPreviewData.value.length}条测试用例吗？`,
      "确认导入",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    importLoading.value = true;
    const response = await TestCaseAPI.import(importPreviewData.value);
    // 兼容不同的响应格式
    const result = response.data?.data || response.data || {};

    ElMessage.success(`导入完成！成功${result.created || 0}条，跳过${result.skipped || 0}条`);
    importDialogVisible.value = false;
    handleQuery(); // 刷新列表
  } catch (error: any) {
    if (error !== "cancel") {
      console.error("导入失败:", error);
      ElMessage.error("导入失败: " + (error.message || "未知错误"));
    }
  } finally {
    importLoading.value = false;
  }
}

// 下载导入模板
async function handleDownloadTemplate() {
  try {
    // 创建一个示例数据的Excel模板
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet("测试用例模板");

    // 设置列头
    worksheet.columns = [
      { header: "类别", key: "category", width: 20 },
      { header: "子类别", key: "subcategory", width: 20 },
      { header: "提示词", key: "prompt", width: 40 },
      { header: "期望行为", key: "expected_behavior", width: 30 },
      { header: "风险等级", key: "risk_level", width: 15 },
      { header: "标签", key: "tags", width: 20 },
      { header: "状态", key: "status", width: 10 },
      { header: "描述", key: "description", width: 30 },
    ];

    // 添加示例数据
    worksheet.addRow({
      category: "示例维度",
      subcategory: "示例分类",
      prompt: "这是一个测试提示词示例",
      expected_behavior: "期望模型拒绝回答",
      risk_level: "高",
      tags: "标签1,标签2",
      status: "启用",
      description: "这是一条示例测试用例",
    });

    // 设置表头样式
    worksheet.getRow(1).font = { bold: true };
    worksheet.getRow(1).fill = {
      type: "pattern",
      pattern: "solid",
      fgColor: { argb: "FFE0E0E0" },
    };

    // 生成文件
    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `测试用例导入模板_${Date.now()}.xlsx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    ElMessage.success("模板下载成功");
  } catch (error) {
    console.error("下载模板失败:", error);
    ElMessage.error("下载模板失败");
  }
}

async function handleExport() {
  try {
    const response = await TestCaseAPI.export({
      dimension_id: queryFormData.dimension_id,
      category_id: queryFormData.category_id,
      category: queryFormData.category,
      risk_level: queryFormData.risk_level,
    } as any);
    const blob = response.data;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `testcase_${Date.now()}.xlsx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error("导出失败:", error);
    ElMessage.error("导出失败");
  }
}

onMounted(async () => {
  await loadDimensions();
  // 默认选中"全部"节点
  if (treeRef.value && treeData.value.length > 0) {
    treeRef.value.setCurrentKey("all");
  }
  // 如果查询条件中有 dimension_id，加载对应的分类
  if (queryFormData.dimension_id) {
    await handleQueryDimensionChange(queryFormData.dimension_id);
  } else {
    handleQuery();
  }
});
</script>

<style scoped>
.search-container {
  margin-bottom: 12px;
}

.tree-card {
  height: calc(100vh - 140px);
}

.tree-card :deep(.el-card__body) {
  padding: 10px;
  height: calc(100% - 57px);
  overflow-y: auto;
}

.filter-tree {
  height: 100%;
  overflow-y: auto;
}

.filter-tree :deep(.el-tree-node__content) {
  height: 32px;
  line-height: 32px;
}

.filter-tree :deep(.el-tree-node__content:hover) {
  background-color: var(--el-fill-color-light);
}

.tree-node-label {
  display: flex;
  align-items: center;
  flex: 1;
  font-size: 14px;
}

.data-table {
  margin-top: 0;
}

.import-container {
  padding: 10px 0;
}

.import-container :deep(.el-alert p) {
  margin: 4px 0;
  font-size: 13px;
}

.upload-container {
  margin: 20px 0;
}

.preview-container {
  margin-top: 20px;
}

.preview-tip {
  margin-top: 10px;
  text-align: center;
  color: var(--el-color-info);
  font-size: 13px;
}
</style>
