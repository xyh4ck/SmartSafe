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
                <el-icon v-if="data.key === 'all'" style="margin-right: 4px;"><Menu /></el-icon>
                <el-icon v-else-if="data.type === 'dimension'" style="margin-right: 4px;"><Folder /></el-icon>
                <el-icon v-else style="margin-right: 4px;"><Document /></el-icon>
                {{ node.label }}
              </span>
            </template>
          </el-tree>
        </el-card>
      </el-col>

      <!-- 右侧关键词列表 -->
      <el-col :span="19">
        <div class="search-container">
          <el-form ref="queryFormRef" :model="queryFormData" :inline="true" label-suffix=":" @submit.prevent="handleQuery">
            <el-form-item prop="word" label="关键词">
              <el-input v-model="queryFormData.word" placeholder="请输入关键词" clearable style="width: 200px" />
            </el-form-item>
            <el-form-item prop="match_type" label="匹配类型">
              <el-select v-model="queryFormData.match_type" placeholder="请选择" clearable style="width: 150px">
                <el-option label="精确匹配" value="exact" />
                <el-option label="模糊匹配" value="fuzzy" />
                <el-option label="正则匹配" value="regex" />
              </el-select>
            </el-form-item>
            <el-form-item prop="risk_level" label="风险等级">
              <el-select v-model="queryFormData.risk_level" placeholder="请选择" clearable style="width: 150px">
                <el-option label="高/High" value="high" />
                <el-option label="中/Medium" value="medium" />
                <el-option label="低/Low" value="low" />
              </el-select>
            </el-form-item>
            <el-form-item class="search-buttons">
              <el-button type="primary" :icon="Search" @click="handleQuery">查询</el-button>
              <el-button :icon="Refresh" @click="resetQuery">重置</el-button>
            </el-form-item>
          </el-form>
        </div>

        <el-card class="data-table">
          <template #header>
            <div class="card-header">
              <span>关键词列表</span>
              <span v-if="selectedCategory" class="selected-category-tag">
                当前分类: <el-tag>{{ selectedCategory.label }}</el-tag>
              </span>
            </div>
          </template>

          <div class="data-table__toolbar">
            <div class="data-table__toolbar--left">
              <el-row :gutter="10">
                <el-col :span="1.5">
                  <el-button type="success" :icon="Plus" @click="handleOpenKeywordDialog('create')">新增</el-button>
                </el-col>
                <el-col :span="1.5">
                  <el-button type="danger" :icon="Delete" :disabled="selectIds.length === 0" @click="handleDeleteKeywords(selectIds)">批量删除</el-button>
                </el-col>
                <el-col :span="1.5">
                  <el-button type="warning" :icon="Upload" @click="handleOpenImportDialog">导入</el-button>
                </el-col>
                <el-col :span="1.5">
                  <el-button :icon="Download" @click="handleExport">导出</el-button>
                </el-col>
                <el-col :span="1.5">
                  <el-button type="info" :icon="Search" @click="handleOpenMatchDialog">匹配测试</el-button>
                </el-col>
              </el-row>
            </div>
          </div>

          <el-table :data="pageTableData" v-loading="loading" class="data-table__content" height="500" @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="50" />
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="word" label="关键词" min-width="150">
              <template #default="{ row }">
                <el-tooltip v-if="row.word" effect="dark" :content="row.word" placement="top">
                  <div class="text-ellipsis">{{ row.word }}</div>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="category_name" label="分类" min-width="120" />
            <el-table-column prop="match_type" label="匹配类型" width="100">
              <template #default="{ row }">
                <el-tag :type="getMatchTypeTagType(row.match_type) || undefined">{{ getMatchTypeText(row.match_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="risk_level" label="风险等级" width="100">
              <template #default="{ row }">
                <el-tag :type="getRiskLevelType(row.risk_level) || undefined">{{ getRiskLevelText(row.risk_level) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="weight" label="权重" width="80" />
            <el-table-column prop="hit_count" label="命中次数" width="90" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status ? 'success' : 'info'">{{ row.status ? '启用' : '停用' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" min-width="160" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleViewKeyword(row)">查看</el-button>
                <el-button type="primary" link @click="handleOpenKeywordDialog('update', row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>

          <template #footer>
            <pagination v-model:total="total" v-model:page="queryFormData.page_no" v-model:limit="queryFormData.page_size" @pagination="handleQuery" />
          </template>
        </el-card>
      </el-col>
    </el-row>

    <!-- 关键词对话框 -->
    <el-dialog v-model="keywordDialogVisible.visible" :title="keywordDialogVisible.title" width="600px" destroy-on-close>
      <el-form ref="keywordFormRef" :model="keywordFormData" :rules="keywordFormRules" label-width="100px">
        <el-form-item prop="category_id" label="分类" required>
          <el-cascader
            v-model="keywordFormData.category_id"
            :options="categoryOptions"
            :props="{ value: 'id', label: 'name', children: 'categories', emitPath: false }"
            placeholder="请选择分类"
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item prop="word" label="关键词" required>
          <el-input v-model="keywordFormData.word" placeholder="请输入关键词" maxlength="255" show-word-limit />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item prop="match_type" label="匹配类型">
              <el-select v-model="keywordFormData.match_type" placeholder="请选择" style="width: 100%">
                <el-option label="精确匹配" value="exact" />
                <el-option label="模糊匹配" value="fuzzy" />
                <el-option label="正则匹配" value="regex" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="risk_level" label="风险等级">
              <el-select v-model="keywordFormData.risk_level" placeholder="请选择" style="width: 100%">
                <el-option label="高/High" value="high" />
                <el-option label="中/Medium" value="medium" />
                <el-option label="低/Low" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item prop="weight" label="权重">
              <el-input-number v-model="keywordFormData.weight" :min="1" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="status" label="状态">
              <el-switch v-model="keywordFormData.status" active-text="启用" inactive-text="停用" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item prop="synonyms" label="同义词">
          <el-select v-model="keywordFormData.synonyms" multiple filterable allow-create default-first-option placeholder="输入后回车添加" style="width: 100%" />
        </el-form-item>
        <el-form-item prop="tags" label="标签">
          <el-select v-model="keywordFormData.tags" multiple filterable allow-create default-first-option placeholder="输入后回车添加" style="width: 100%" />
        </el-form-item>
        <el-form-item prop="description" label="备注">
          <el-input v-model="keywordFormData.description" type="textarea" :rows="2" placeholder="请输入备注" maxlength="255" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="keywordDialogVisible.visible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitKeyword">确定</el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入关键词" width="800px" destroy-on-close>
      <div class="import-container">
        <el-alert title="导入说明" type="info" :closable="false" style="margin-bottom: 20px;">
          <p>1. 请先下载模板，按照模板格式填写数据</p>
          <p>2. 分类名称必须与系统中已有的分类名称完全一致</p>
          <p>3. 匹配类型可填写：精确匹配、模糊匹配、正则匹配（或 exact、fuzzy、regex）</p>
          <p>4. 风险等级可填写：高、中、低（或 high、medium、low）</p>
          <p>5. 同义词和标签用英文逗号分隔</p>
        </el-alert>

        <div class="import-actions" style="margin-bottom: 20px;">
          <el-button type="primary" :icon="Download" @click="handleDownloadTemplate">下载导入模板</el-button>
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
          <div class="el-upload__text">拖拽文件到此处或<em>点击上传</em></div>
          <template #tip>
            <div class="el-upload__tip">仅支持.xlsx格式的Excel文件，文件大小不超过10MB</div>
          </template>
        </el-upload>

        <div v-if="showPreview && importPreviewData.length > 0" class="preview-container">
          <el-divider>数据预览（共 {{ importPreviewData.length }} 条）</el-divider>
          <el-table :data="importPreviewData.slice(0, 5)" border :max-height="300">
            <el-table-column prop="word" label="关键词" min-width="150" show-overflow-tooltip />
            <el-table-column prop="category_name" label="分类" width="120" />
            <el-table-column prop="match_type" label="匹配类型" width="100">
              <template #default="{ row }">
                <el-tag :type="getMatchTypeTagType(row.match_type) || undefined">{{ getMatchTypeText(row.match_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="risk_level" label="风险等级" width="100">
              <template #default="{ row }">
                <el-tag :type="getRiskLevelType(row.risk_level) || undefined">{{ getRiskLevelText(row.risk_level) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="importPreviewData.length > 5" class="preview-tip">仅显示前5条，实际将导入 {{ importPreviewData.length }} 条数据</div>
        </div>
      </div>

      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="importLoading" :disabled="importPreviewData.length === 0" @click="handleConfirmImport">确认导入</el-button>
      </template>
    </el-dialog>

    <!-- 匹配测试对话框 -->
    <el-dialog v-model="matchDialogVisible" title="关键词匹配测试" width="800px" destroy-on-close>
      <el-form :model="matchFormData" label-width="100px">
        <el-form-item label="待匹配文本" required>
          <el-input v-model="matchFormData.text" type="textarea" :rows="4" placeholder="请输入待匹配的文本内容" />
        </el-form-item>
        <el-form-item label="限定分类">
          <el-cascader
            v-model="matchFormData.category_ids"
            :options="categoryOptions"
            :props="{ value: 'id', label: 'name', children: 'categories', emitPath: false, multiple: true }"
            placeholder="不限定则匹配所有分类"
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="最低风险等级">
          <el-select v-model="matchFormData.min_risk_level" placeholder="不限定" clearable style="width: 200px">
            <el-option label="高/High" value="high" />
            <el-option label="中/Medium" value="medium" />
            <el-option label="低/Low" value="low" />
          </el-select>
        </el-form-item>
      </el-form>

      <el-divider v-if="matchResult">匹配结果</el-divider>
      <div v-if="matchResult" class="match-result">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="匹配数量">
            <el-tag type="info">{{ matchResult.total_matches }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="风险评分">
            <el-tag :type="matchResult.risk_score >= 5 ? 'danger' : matchResult.risk_score >= 2 ? 'warning' : 'success'">
              {{ matchResult.risk_score }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="最高风险等级">
            <el-tag :type="getRiskLevelType(matchResult.highest_risk_level) || undefined">
              {{ getRiskLevelText(matchResult.highest_risk_level) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-table v-if="matchResult.matches.length > 0" :data="matchResult.matches" border style="margin-top: 16px;" :max-height="300">
          <el-table-column prop="word" label="关键词" width="120" />
          <el-table-column prop="matched_text" label="匹配文本" width="120" />
          <el-table-column prop="category_name" label="分类" width="120" />
          <el-table-column prop="match_type" label="匹配类型" width="100">
            <template #default="{ row }">
              <el-tag :type="getMatchTypeTagType(row.match_type) || undefined" size="small">{{ getMatchTypeText(row.match_type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="risk_level" label="风险等级" width="100">
            <template #default="{ row }">
              <el-tag :type="getRiskLevelType(row.risk_level) || undefined" size="small">{{ getRiskLevelText(row.risk_level) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="weight" label="权重" width="80" />
          <el-table-column prop="position" label="位置" width="80" />
        </el-table>
      </div>

      <template #footer>
        <el-button @click="matchDialogVisible = false">关闭</el-button>
        <el-button type="primary" :loading="matchLoading" :disabled="!matchFormData.text" @click="handleMatch">执行匹配</el-button>
      </template>
    </el-dialog>

    <!-- 查看详情抽屉 -->
    <el-drawer v-model="drawerVisible" title="关键词详情" size="500px" direction="rtl">
      <el-descriptions :column="1" border v-if="viewData">
        <el-descriptions-item label="ID">{{ viewData.id }}</el-descriptions-item>
        <el-descriptions-item label="关键词">{{ viewData.word }}</el-descriptions-item>
        <el-descriptions-item label="分类">
          <el-tag>{{ viewData.category_name }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="匹配类型">
          <el-tag :type="getMatchTypeTagType(viewData.match_type) || undefined">{{ getMatchTypeText(viewData.match_type) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="风险等级">
          <el-tag :type="getRiskLevelType(viewData.risk_level) || undefined">{{ getRiskLevelText(viewData.risk_level) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="权重">{{ viewData.weight }}</el-descriptions-item>
        <el-descriptions-item label="命中次数">{{ viewData.hit_count }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="viewData.status ? 'success' : 'info'">{{ viewData.status ? '启用' : '停用' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="同义词" v-if="viewData.synonyms && viewData.synonyms.length > 0">
          <el-tag v-for="s in viewData.synonyms" :key="s" style="margin-right: 8px;">{{ s }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="标签" v-if="viewData.tags && viewData.tags.length > 0">
          <el-tag v-for="t in viewData.tags" :key="t" type="info" style="margin-right: 8px;">{{ t }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注">{{ viewData.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建人">{{ viewData.creator?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ viewData.created_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ viewData.updated_at || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: "KeywordQuestionBank", inheritAttrs: false });

import {
  KeywordAPI,
  type KeywordTable,
  type KeywordForm,
  type KeywordPageQuery,
  type KeywordMatchRequest,
  type KeywordMatchResponse,
} from "@/api/module_evaluation/keyword_questionbank";
import CategoryAPI from "@/api/module_evaluation/category";
import { formatToDateTime } from "@/utils/dateUtil";
import { ElMessage, ElMessageBox, type UploadProps, type UploadFile } from "element-plus";
import {
  Plus, Delete, Search, Refresh, Upload, Download,
  Folder, Document, Menu
} from "@element-plus/icons-vue";
import ExcelJS from 'exceljs';

const queryFormRef = ref();
const keywordFormRef = ref();
const treeRef = ref();

const total = ref(0);
const selectIds = ref<number[]>([]);
const loading = ref(false);

const pageTableData = ref<KeywordTable[]>([]);

// 分类树数据
interface TreeNode {
  key: string;
  label: string;
  type: 'dimension' | 'category';
  dimension_id?: number;
  category_id?: number;
  children?: TreeNode[];
}

const treeData = ref<TreeNode[]>([]);
const selectedCategory = ref<TreeNode | null>(null);
const categoryOptions = ref<any[]>([]);

// 查询表单
const queryFormData = reactive<KeywordPageQuery>({
  page_no: 1,
  page_size: 10,
  category_id: undefined,
  word: undefined,
  match_type: undefined,
  risk_level: undefined,
});

// 关键词表单
const keywordFormData = reactive<KeywordForm>({
  id: undefined,
  category_id: 0,
  word: "",
  match_type: "exact",
  risk_level: "medium",
  weight: 1,
  synonyms: [],
  tags: [],
  status: true,
  description: undefined,
});

// 对话框状态
const keywordDialogVisible = reactive({ title: "", visible: false });
const importDialogVisible = ref(false);
const matchDialogVisible = ref(false);
const drawerVisible = ref(false);

const viewData = ref<KeywordTable | null>(null);

// 导入相关
const importFileList = ref<UploadFile[]>([]);
const importLoading = ref(false);
const importPreviewData = ref<any[]>([]);
const showPreview = ref(false);

// 匹配测试相关
const matchFormData = reactive<KeywordMatchRequest>({
  text: "",
  category_ids: undefined,
  min_risk_level: undefined,
});
const matchResult = ref<KeywordMatchResponse | null>(null);
const matchLoading = ref(false);

// 分类名称映射
const categoryNameMap = ref<Map<number, string>>(new Map());

// 表单验证规则
const keywordFormRules = {
  category_id: [{ required: true, message: "请选择分类", trigger: "change" }],
  word: [{ required: true, message: "请输入关键词", trigger: "blur" }],
};

// ==================== 数据加载 ====================

async function loadCategoryTree() {
  try {
    const response = await CategoryAPI.getTree(false);
    const treeList = response.data?.data ?? [];
    
    // 构建树形数据
    const tree: TreeNode[] = [
      { key: 'all', label: '全部', type: 'dimension' }
    ];
    
    // 构建分类选项（用于级联选择器）
    const options: any[] = [];
    
    for (const item of treeList) {
      if (!item.dimension_status) continue;
      
      const dimensionNode: TreeNode = {
        key: `dimension_${item.dimension_id}`,
        label: item.dimension_name || '',
        type: 'dimension',
        dimension_id: item.dimension_id,
        children: []
      };
      
      const dimensionOption: any = {
        id: `dim_${item.dimension_id}`,
        name: item.dimension_name,
        categories: []
      };
      
      dimensionNode.children = (item.categories || []).map((cat: any) => {
        categoryNameMap.value.set(cat.id, cat.name);
        dimensionOption.categories.push({
          id: cat.id,
          name: cat.name
        });
        return {
          key: `category_${cat.id}`,
          label: cat.name || '',
          type: 'category' as const,
          dimension_id: item.dimension_id,
          category_id: cat.id
        };
      });
      
      if (dimensionNode.children.length > 0) {
        tree.push(dimensionNode);
        options.push(dimensionOption);
      }
    }
    
    treeData.value = tree;
    categoryOptions.value = options;
  } catch (error) {
    console.error("加载分类树失败:", error);
  }
}

async function handleQuery() {
  loading.value = true;
  try {
    const { data } = (await KeywordAPI.page(queryFormData)).data;
    pageTableData.value = (data?.items ?? []).map((r: any) => ({
      ...r,
      created_at: r.created_at ? formatToDateTime(r.created_at) : "",
      updated_at: r.updated_at ? formatToDateTime(r.updated_at) : "",
    }));
    total.value = data?.total ?? 0;
  } finally {
    loading.value = false;
  }
}

function resetQuery() {
  queryFormData.category_id = undefined;
  queryFormData.word = undefined;
  queryFormData.match_type = undefined;
  queryFormData.risk_level = undefined;
  queryFormData.page_no = 1;
  selectedCategory.value = null;
  if (treeRef.value) {
    treeRef.value.setCurrentKey(null);
  }
  handleQuery();
}

function handleTreeNodeClick(data: TreeNode) {
  if (data.key === "all") {
    queryFormData.category_id = undefined;
    selectedCategory.value = null;
  } else if (data.type === 'category' && data.category_id) {
    queryFormData.category_id = data.category_id;
    selectedCategory.value = data;
  } else {
    queryFormData.category_id = undefined;
    selectedCategory.value = data;
  }
  queryFormData.page_no = 1;
  handleQuery();
}

function handleSelectionChange(rows: KeywordTable[]) {
  selectIds.value = rows.map((r) => r.id!);
}

// ==================== 关键词操作 ====================

function handleOpenKeywordDialog(type: "create" | "update", row?: KeywordTable) {
  if (type === "create") {
    const categoryId = selectedCategory.value?.category_id;
    Object.assign(keywordFormData, {
      id: undefined,
      category_id: categoryId || undefined,
      word: "",
      match_type: "exact",
      risk_level: "medium",
      weight: 1,
      synonyms: [],
      tags: [],
      status: true,
      description: undefined,
    });
    keywordDialogVisible.title = "新增关键词";
  } else {
    Object.assign(keywordFormData, {
      ...row,
      synonyms: row?.synonyms ?? [],
      tags: row?.tags ?? [],
    });
    keywordDialogVisible.title = "编辑关键词";
  }
  keywordDialogVisible.visible = true;
}

async function handleSubmitKeyword() {
  if (!keywordFormRef.value) return;
  try {
    await keywordFormRef.value.validate();
    if (keywordFormData.id) {
      await KeywordAPI.update(keywordFormData.id, keywordFormData);
      ElMessage.success("更新成功");
    } else {
      await KeywordAPI.create(keywordFormData);
      ElMessage.success("创建成功");
    }
    keywordDialogVisible.visible = false;
    handleQuery();
  } catch (error) {
    console.error("提交失败:", error);
  }
}

async function handleDeleteKeywords(ids: number[]) {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${ids.length} 个关键词吗？`, "提示", {
      type: "warning",
    });
    await KeywordAPI.delete(ids);
    ElMessage.success("删除成功");
    handleQuery();
  } catch (error) {
    if (error !== "cancel") {
      console.error("删除失败:", error);
    }
  }
}

function handleViewKeyword(row: KeywordTable) {
  viewData.value = { ...row };
  drawerVisible.value = true;
}

// ==================== 导入导出 ====================

function handleOpenImportDialog() {
  importDialogVisible.value = true;
  importFileList.value = [];
  importPreviewData.value = [];
  showPreview.value = false;
}

const beforeUpload: UploadProps["beforeUpload"] = (file) => {
  const isExcel = file.type === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" || file.name.endsWith(".xlsx");
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

async function parseExcelFile(file: File): Promise<any[]> {
  const workbook = new ExcelJS.Workbook();
  const arrayBuffer = await file.arrayBuffer();
  await workbook.xlsx.load(arrayBuffer);

  const worksheet = workbook.worksheets[0];
  if (!worksheet) {
    throw new Error("Excel文件中没有工作表");
  }

  const data: any[] = [];
  const headerRow = worksheet.getRow(1);

  const fieldMapping: Record<string, string> = {
    关键词: "word",
    分类: "category_name",
    匹配类型: "match_type",
    风险等级: "risk_level",
    权重: "weight",
    同义词: "synonyms",
    标签: "tags",
    状态: "status",
    描述: "description",
  };

  const columnIndexMap: Record<string, number> = {};
  headerRow.eachCell((cell, colNumber) => {
    const headerName = cell.value?.toString().trim();
    if (headerName && fieldMapping[headerName]) {
      columnIndexMap[fieldMapping[headerName]] = colNumber;
    }
  });

  if (!columnIndexMap["word"]) {
    throw new Error("Excel文件缺少必需列：关键词");
  }

  // 反向映射：分类名称 -> ID
  const categoryIdMap = new Map<string, number>();
  categoryNameMap.value.forEach((name, id) => {
    categoryIdMap.set(name, id);
  });

  worksheet.eachRow((row, rowNumber) => {
    if (rowNumber === 1) return;

    const word = row.getCell(columnIndexMap["word"])?.value?.toString().trim();
    if (!word) return;

    const categoryName = row.getCell(columnIndexMap["category_name"] || 999)?.value?.toString().trim();
    const category_id = categoryName ? categoryIdMap.get(categoryName) : undefined;
    if (!category_id) {
      console.warn(`第${rowNumber}行: 找不到分类"${categoryName}"`);
      return;
    }

    let match_type = row.getCell(columnIndexMap["match_type"] || 999)?.value?.toString().trim() || "exact";
    if (match_type === "精确匹配") match_type = "exact";
    else if (match_type === "模糊匹配") match_type = "fuzzy";
    else if (match_type === "正则匹配") match_type = "regex";

    let risk_level = row.getCell(columnIndexMap["risk_level"] || 999)?.value?.toString().trim() || "medium";
    if (risk_level === "高") risk_level = "high";
    else if (risk_level === "中") risk_level = "medium";
    else if (risk_level === "低") risk_level = "low";

    const weightCell = row.getCell(columnIndexMap["weight"] || 999)?.value;
    const weight = typeof weightCell === "number" ? weightCell : 1;

    const statusCell = row.getCell(columnIndexMap["status"] || 999)?.value?.toString().trim();
    const status = statusCell === "启用" || statusCell === "true" || statusCell === "1" || statusCell === undefined;

    const synonymsCell = row.getCell(columnIndexMap["synonyms"] || 999)?.value?.toString().trim();
    const synonyms = synonymsCell ? synonymsCell.split(",").map((s) => s.trim()).filter((s) => s) : [];

    const tagsCell = row.getCell(columnIndexMap["tags"] || 999)?.value?.toString().trim();
    const tags = tagsCell ? tagsCell.split(",").map((t) => t.trim()).filter((t) => t) : [];

    const description = row.getCell(columnIndexMap["description"] || 999)?.value?.toString().trim();

    data.push({
      category_id,
      category_name: categoryName,
      word,
      match_type,
      risk_level,
      weight,
      synonyms,
      tags,
      status,
      description,
    });
  });

  return data;
}

async function handleConfirmImport() {
  if (importPreviewData.value.length === 0) return;
  importLoading.value = true;
  try {
    const items = importPreviewData.value.map((item) => ({
      category_id: item.category_id,
      word: item.word,
      match_type: item.match_type,
      risk_level: item.risk_level,
      weight: item.weight,
      synonyms: item.synonyms,
      tags: item.tags,
      status: item.status,
      description: item.description,
    }));
    const response = await KeywordAPI.import(items);
    const result = response.data?.data;
    ElMessage.success(`导入完成：成功 ${result?.created || 0} 条，跳过 ${result?.skipped || 0} 条`);
    importDialogVisible.value = false;
    handleQuery();
  } catch (error) {
    console.error("导入失败:", error);
    ElMessage.error("导入失败");
  } finally {
    importLoading.value = false;
  }
}

async function handleDownloadTemplate() {
  const workbook = new ExcelJS.Workbook();
  const worksheet = workbook.addWorksheet("关键词导入模板");

  worksheet.columns = [
    { header: "关键词", key: "word", width: 20 },
    { header: "分类", key: "category_name", width: 15 },
    { header: "匹配类型", key: "match_type", width: 12 },
    { header: "风险等级", key: "risk_level", width: 12 },
    { header: "权重", key: "weight", width: 10 },
    { header: "同义词", key: "synonyms", width: 20 },
    { header: "标签", key: "tags", width: 20 },
    { header: "状态", key: "status", width: 10 },
    { header: "描述", key: "description", width: 30 },
  ];

  worksheet.addRow({
    word: "示例关键词",
    category_name: "示例分类",
    match_type: "精确匹配",
    risk_level: "高",
    weight: 1,
    synonyms: "同义词1,同义词2",
    tags: "标签1,标签2",
    status: "启用",
    description: "示例描述",
  });

  const buffer = await workbook.xlsx.writeBuffer();
  const blob = new Blob([buffer], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "关键词导入模板.xlsx";
  link.click();
  URL.revokeObjectURL(url);
}

async function handleExport() {
  try {
    const response = await KeywordAPI.export(queryFormData);
    const blob = new Blob([response.data], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "关键词列表.xlsx";
    link.click();
    URL.revokeObjectURL(url);
    ElMessage.success("导出成功");
  } catch (error) {
    console.error("导出失败:", error);
    ElMessage.error("导出失败");
  }
}

// ==================== 匹配测试 ====================

function handleOpenMatchDialog() {
  matchFormData.text = "";
  matchFormData.category_ids = undefined;
  matchFormData.min_risk_level = undefined;
  matchResult.value = null;
  matchDialogVisible.value = true;
}

async function handleMatch() {
  if (!matchFormData.text) {
    ElMessage.warning("请输入待匹配文本");
    return;
  }
  matchLoading.value = true;
  try {
    const response = await KeywordAPI.match(matchFormData);
    matchResult.value = response.data?.data ?? null;
  } catch (error) {
    console.error("匹配失败:", error);
    ElMessage.error("匹配失败");
  } finally {
    matchLoading.value = false;
  }
}

// ==================== 辅助函数 ====================

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
  if (level === "high" || level === "高") return "高";
  if (level === "medium" || level === "中") return "中";
  if (level === "low" || level === "低") return "低";
  return riskLevel;
}

function getMatchTypeTagType(matchType?: string) {
  if (!matchType) return "";
  if (matchType === "exact") return "success";
  if (matchType === "fuzzy") return "warning";
  if (matchType === "regex") return "danger";
  return "";
}

function getMatchTypeText(matchType?: string) {
  if (!matchType) return "-";
  if (matchType === "exact") return "精确";
  if (matchType === "fuzzy") return "模糊";
  if (matchType === "regex") return "正则";
  return matchType;
}

// ==================== 初始化 ====================

onMounted(async () => {
  await loadCategoryTree();
  await handleQuery();
});
</script>

<style scoped lang="scss">
.app-container {
  padding: 16px;
}

.tree-card {
  height: calc(100vh - 140px);
  
  :deep(.el-card__body) {
    height: calc(100% - 60px);
    overflow: auto;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-tree {
  :deep(.el-tree-node__content) {
    height: 32px;
  }
}

.tree-node-label {
  display: flex;
  align-items: center;
}

.search-container {
  background: #fff;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 16px;
}

.data-table {
  .selected-category-tag {
    margin-left: 16px;
    font-size: 14px;
    color: #666;
  }
}

.data-table__toolbar {
  margin-bottom: 16px;
}

.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

.import-container {
  .preview-container {
    margin-top: 16px;
  }
  
  .preview-tip {
    margin-top: 8px;
    color: #909399;
    font-size: 12px;
    text-align: center;
  }
}

.match-result {
  margin-top: 16px;
}
</style>
