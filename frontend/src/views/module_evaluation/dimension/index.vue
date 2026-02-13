<template>
  <div class="app-container">
    <div class="search-container">
      <el-form ref="queryFormRef" :model="queryFormData" :inline="true" label-suffix=":" @submit.prevent="handleQuery">
        <el-form-item prop="name" label="风险维度名称">
          <el-input v-model="queryFormData.name" placeholder="请输入维度名称" clearable @keyup.enter="handleQuery" />
        </el-form-item>
        <el-form-item prop="code" label="风险维度代码">
          <el-input v-model="queryFormData.code" placeholder="请输入维度代码" clearable @keyup.enter="handleQuery" />
        </el-form-item>
        <el-form-item prop="status" label="状态">
          <el-select v-model="queryFormData.status" placeholder="请选择状态" style="width: 167.5px" clearable>
            <el-option value="true" label="启用" />
            <el-option value="false" label="停用" />
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
          <span>风险维度与类别管理</span>
        </div>
      </template>

      <div class="data-table__toolbar">
        <div class="data-table__toolbar--left">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-button type="success" icon="plus" @click="handleOpenDimensionDialog('create')">新增风险维度</el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button type="danger" icon="delete" :disabled="selectIds.length === 0" @click="handleDeleteDimensions(selectIds)">批量删除</el-button>
            </el-col>
            <el-col :span="1.5">
              <el-dropdown trigger="click">
                <el-button type="primary" icon="download">导出/导入</el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="handleExportTemplate">下载导入模板</el-dropdown-item>
                    <el-dropdown-item @click="handleExportData">导出分类数据</el-dropdown-item>
                    <el-dropdown-item @click="handleImportData">导入分类数据</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </el-col>
          </el-row>
        </div>
      </div>

      <el-table
        :data="treeTableData"
        v-loading="loading"
        class="data-table__content"
        height="500"
        row-key="id"
        border
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" :selectable="checkSelectable" />
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="name" label="分类名称" min-width="280" />
        <el-table-column prop="code" label="代码">
          <template #default="{ row }">
            {{ row.code || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status ? 'success' : 'info'">{{ row.status ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creator" label="创建人" min-width="120">
          <template #default="{ row }">
            {{ row.creator?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="160" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <template v-if="row.type === 'dimension'">
              <el-button type="success" link icon="plus" @click="handleOpenCategoryDialog('create', row)">添加风险类别</el-button>
              <el-button type="primary" link @click="handleOpenDimensionDialog('update', row)">编辑</el-button>
            </template>
            <template v-else>
              <el-button type="primary" link @click="handleOpenCategoryDialog('update', row)">编辑</el-button>
              <el-button type="danger" link @click="handleDeleteCategory(row)">删除</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <pagination v-model:total="total" v-model:page="queryFormData.page_no" v-model:limit="queryFormData.page_size" @pagination="handleQuery" />
      </template>
    </el-card>

    <!-- 维度对话框 -->
    <el-dialog v-model="dimensionDialog.visible" :title="dimensionDialog.title" width="600px" destroy-on-close>
      <el-form ref="dimensionFormRef" :model="dimensionForm" label-width="130px">
        <el-form-item prop="name" label="风险维度名称" required>
          <el-input v-model="dimensionForm.name" placeholder="请输入风险维度名称" />
        </el-form-item>
        <el-form-item prop="code" label="风险维度代码">
          <el-input v-model="dimensionForm.code" placeholder="请输入风险维度代码（可选）" />
        </el-form-item>
        <el-form-item prop="sort" label="排序">
          <el-input-number v-model="dimensionForm.sort" :min="0" />
        </el-form-item>
        <el-form-item prop="status" label="状态">
          <el-switch v-model="dimensionForm.status" />
        </el-form-item>
        <el-form-item prop="description" label="备注">
          <el-input v-model="dimensionForm.description" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dimensionDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleDimensionSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 分类对话框 -->
    <el-dialog v-model="categoryDialog.visible" :title="categoryDialog.title" width="600px" destroy-on-close>
      <el-form ref="categoryFormRef" :model="categoryForm" label-width="130px">
        <el-form-item prop="dimension_id" label="所属风险维度" required>
          <el-select v-model="categoryForm.dimension_id" placeholder="请选择维度" :disabled="!!categoryForm.id" style="width: 100%">
            <el-option v-for="dim in dimensions" :key="dim.id" :label="dim.name" :value="dim.id || 0" />
          </el-select>
        </el-form-item>
        <el-form-item prop="name" label="风险类别名称" required>
          <el-input v-model="categoryForm.name" placeholder="请输入风险类别名称" />
        </el-form-item>
        <el-form-item prop="code" label="风险类别代码">
          <el-input v-model="categoryForm.code" placeholder="请输入风险类别代码（可选）" />
        </el-form-item>
        <el-form-item prop="sort" label="排序">
          <el-input-number v-model="categoryForm.sort" :min="0" />
        </el-form-item>
        <el-form-item prop="status" label="状态">
          <el-switch v-model="categoryForm.status" />
        </el-form-item>
        <el-form-item prop="description" label="备注">
          <el-input v-model="categoryForm.description" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleCategorySubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: "EvaluationDimension", inheritAttrs: false });

import DimensionAPI, {
  DimensionTable,
  DimensionForm,
  DimensionPageQuery,
  CategoryTable,
  CategoryForm,
} from "@/api/module_evaluation/dimension";
import CategoryAPI from "@/api/module_evaluation/category";
import { formatToDateTime } from "@/utils/dateUtil";
import { ElMessage, ElMessageBox } from "element-plus";
import { Folder, Document } from "@element-plus/icons-vue";

const queryFormRef = ref();
const dimensionFormRef = ref();
const categoryFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const loading = ref(false);

const treeTableData = ref<any[]>([]);
const dimensions = ref<DimensionTable[]>([]);

const queryFormData = reactive<DimensionPageQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  code: undefined,
  status: undefined,
});

const dimensionForm = reactive<DimensionForm>({
  id: undefined,
  name: "",
  code: undefined,
  sort: 0,
  status: true,
  description: undefined,
});

const categoryForm = reactive<CategoryForm>({
  id: undefined,
  dimension_id: 0,
  name: "",
  code: undefined,
  sort: 0,
  status: true,
  description: undefined,
});

const dimensionDialog = reactive({ title: "", visible: false });
const categoryDialog = reactive({ title: "", visible: false });

// 构建树形数据
function buildTreeData(dimensions: DimensionTable[]): any[] {
  return dimensions.map((dim: any) => {
    const categories = dim.categories || [];
    return {
      ...dim,
      id: `dim_${dim.id}`, // 维度使用前缀避免与分类ID冲突
      type: "dimension",
      created_at: dim.created_at ? formatToDateTime(dim.created_at) : "",
      hasChildren: categories.length > 0, // 设置是否有子节点
      children: categories.map((cat: any) => ({
        ...cat,
        id: `cat_${cat.id}`, // 分类使用不同的ID前缀避免冲突
        originalId: cat.id, // 保存真实的分类ID用于删除
        type: "category",
        dimension_id: dim.id,
        hasChildren: false, // 分类没有子节点
        created_at: cat.created_at ? formatToDateTime(cat.created_at) : "",
      })),
    };
  });
}

async function handleQuery() {
  loading.value = true;
  try {
    const response = await DimensionAPI.page(queryFormData);
    const { data } = response.data;
    const items = data?.items ?? [];

    // 构建树形数据
    treeTableData.value = buildTreeData(items);
    dimensions.value = items;
    total.value = data?.total ?? 0;
  } finally {
    loading.value = false;
  }
}

function resetQuery() {
  queryFormData.name = undefined;
  queryFormData.status = undefined;
  queryFormData.page_no = 1;
  handleQuery();
}

function checkSelectable(row: any) {
  // 只允许选择维度行，不允许选择分类行
  return row.type === "dimension";
}

function handleSelectionChange(rows: any[]) {
  // 只统计维度行的ID（提取真实的维度ID）
  selectIds.value = rows
    .filter((r) => r.type === "dimension")
    .map((r) => {
      // 如果ID是字符串格式，提取数字部分
      if (typeof r.id === "string" && r.id.startsWith("dim_")) {
        return parseInt(r.id.replace("dim_", ""));
      }
      return r.id;
    });
}

// 维度相关操作
function handleOpenDimensionDialog(type: "create" | "update", row?: any) {
  if (type === "create") {
    Object.assign(dimensionForm, {
      id: undefined,
      name: "",
      code: undefined,
      sort: 0,
      status: true,
      description: undefined,
    });
    dimensionDialog.title = "新增维度";
  } else {
    // 提取真实的维度ID
    const realId =
      typeof row.id === "string" && row.id.startsWith("dim_")
        ? parseInt(row.id.replace("dim_", ""))
        : row.id;
    Object.assign(dimensionForm, { ...row, id: realId });
    dimensionDialog.title = "编辑维度";
  }
  dimensionDialog.visible = true;
}

async function handleDimensionSubmit() {
  if (!dimensionForm.name) {
    ElMessage.warning("请输入维度名称");
    return;
  }
  try {
    if (dimensionForm.id) {
      await DimensionAPI.update(dimensionForm.id, dimensionForm);
    } else {
      await DimensionAPI.create(dimensionForm);
    }
    dimensionDialog.visible = false;
    handleQuery();
  } catch (error: any) {
    ElMessage.error(error.message || "操作失败");
  }
}

async function handleDeleteDimensions(ids: number[]) {
  if (ids.length === 0) return;
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${ids.length} 个维度吗？`, "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });
    await DimensionAPI.delete(ids);
    handleQuery();
  } catch (error: any) {
    if (error !== "cancel") {
      ElMessage.error(error.message || "删除失败");
    }
  }
}

// 分类相关操作
function handleOpenCategoryDialog(type: "create" | "update", row?: any) {
  if (type === "create") {
    // 从维度行创建分类
    // 提取真实的维度ID
    const realDimensionId =
      typeof row.id === "string" && row.id.startsWith("dim_")
        ? parseInt(row.id.replace("dim_", ""))
        : row.id;
    Object.assign(categoryForm, {
      id: undefined,
      dimension_id: realDimensionId || 0,
      name: "",
      code: undefined,
      sort: 0,
      status: true,
      description: undefined,
    });
    categoryDialog.title = "新增分类";
  } else {
    // 从分类行编辑
    // 使用保存的真实分类ID
    const realCategoryId =
      row.originalId ||
      (typeof row.id === "string" && row.id.startsWith("cat_")
        ? parseInt(row.id.replace("cat_", ""))
        : row.id);
    Object.assign(categoryForm, {
      id: realCategoryId,
      dimension_id: row.dimension_id || 0,
      name: row.name,
      code: row.code,
      sort: row.sort,
      status: row.status,
      description: row.description,
    });
    categoryDialog.title = "编辑分类";
  }
  categoryDialog.visible = true;
}

async function handleCategorySubmit() {
  if (!categoryForm.name) {
    ElMessage.warning("请输入分类名称");
    return;
  }
  if (!categoryForm.dimension_id) {
    ElMessage.warning("请选择所属维度");
    return;
  }
  try {
    if (categoryForm.id) {
      await CategoryAPI.update(categoryForm.id, categoryForm);
    } else {
      await CategoryAPI.create(categoryForm);
    }
    categoryDialog.visible = false;
    handleQuery();
  } catch (error: any) {
    ElMessage.error(error.message || "操作失败");
  }
}

async function handleDeleteCategory(row: any) {
  try {
    await ElMessageBox.confirm(`确定要删除分类 "${row.name}" 吗？`, "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });
    // 使用保存的真实分类ID
    const realCategoryId =
      row.originalId ||
      (typeof row.id === "string" && row.id.startsWith("cat_")
        ? parseInt(row.id.replace("cat_", ""))
        : row.id);
    await CategoryAPI.delete([realCategoryId]);
    handleQuery();
  } catch (error: any) {
    if (error !== "cancel") {
      ElMessage.error(error.message || "删除失败");
    }
  }
}

// 导入导出相关操作
async function handleExportTemplate() {
  try {
    const response = await CategoryAPI.exportTemplate();
    // 创建blob url进行下载
    const url = window.URL.createObjectURL(response.data);
    const link = document.createElement("a");
    link.href = url;
    link.download = "分类导入模板.xlsx";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    ElMessage.success("导出模板成功");
  } catch (error: any) {
    ElMessage.error(error.message || "导出模板失败");
  }
}

async function handleExportData() {
  try {
    const response = await CategoryAPI.export();
    const url = window.URL.createObjectURL(response.data);
    const link = document.createElement("a");
    link.href = url;
    link.download = "风险分类数据.xlsx";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    ElMessage.success("导出数据成功");
  } catch (error: any) {
    ElMessage.error(error.message || "导出数据失败");
  }
}

async function handleImportData() {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = ".xlsx,.xls";
  input.onchange = async (e: any) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const response = await CategoryAPI.import(file);
      const result = response.data.data;
      
      if (result.error_count === 0) {
        ElMessage.success(`导入成功 ${result.success_count} 条数据`);
      } else {
        ElMessage.warning(
          `导入成功 ${result.success_count} 条，失败 ${result.error_count} 条\n错误: ${result.errors.join("\n")}`
        );
      }
      
      handleQuery();
    } catch (error: any) {
      ElMessage.error(error.message || "导入失败");
    }
  };
  input.click();
}

onMounted(() => handleQuery());
</script>

<style scoped>
.search-container {
  margin-bottom: 12px;
}

.ml-2 {
  margin-left: 8px;
}
</style>

