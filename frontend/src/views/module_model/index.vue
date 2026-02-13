<template>
  <div class="app-container">
    <el-card shadow="never" class="mb-4">
      <el-form :inline="true" :model="queryForm" @submit.prevent="handleQuery" class="search-form">
        <el-form-item label="名称">
          <el-input
            v-model="queryForm.name"
            placeholder="模型名称"
            style="width: 200px"
            clearable
            :prefix-icon="Search"
          />
        </el-form-item>
        <el-form-item label="供应商">
          <el-input
            v-model="queryForm.provider"
            placeholder="供应商"
            style="width: 200px"
            clearable
            :prefix-icon="Search"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="queryForm.available"
            style="width: 160px"
            clearable
            placeholder="全部"
          >
            <el-option :value="true" label="启用" />
            <el-option :value="false" label="停用" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button
            v-hasPerm="['module_model:registry:query']"
            type="primary"
            :icon="Search"
            native-type="submit"
          >
            查询
          </el-button>
          <el-button
            v-hasPerm="['module_model:registry:query']"
            :icon="Refresh"
            @click="handleResetQuery"
          >
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" class="data-table">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="text-lg font-bold">模型接入管理</span>
          <div class="flex gap-2">
            <el-button
              v-hasPerm="['module_model:registry:create']"
              type="primary"
              :icon="Plus"
              @click="openCreate"
            >
              新建模型
            </el-button>
            <el-button
              v-hasPerm="['module_model:registry:available']"
              type="success"
              plain
              :icon="VideoPlay"
              :disabled="selected.length === 0"
              @click="batchEnable(true)"
            >
              批量启用
            </el-button>
            <el-button
              v-hasPerm="['module_model:registry:available']"
              type="warning"
              plain
              :icon="VideoPause"
              :disabled="selected.length === 0"
              @click="batchEnable(false)"
            >
              批量停用
            </el-button>
            <el-button
              v-hasPerm="['module_model:registry:delete']"
              type="danger"
              plain
              :icon="Delete"
              :disabled="selected.length === 0"
              @click="batchDelete"
            >
              批量删除
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        ref="tableRef"
        v-loading="loading"
        :data="items"
        row-key="id"
        border
        stripe
        @selection-change="handleSelectionChange"
      >
        <template #empty>
          <el-empty :image-size="80" description="暂无数据" />
        </template>
        <el-table-column type="selection" width="50" align="center" />
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="provider" label="供应商" min-width="120" show-overflow-tooltip />
        <el-table-column prop="type" label="模型类型" min-width="100">
          <template #default="{ row }">
            {{ (dictStore.getDictLabel("model_type", row.type) as any)?.dict_label }}
          </template>
        </el-table-column>
        <el-table-column prop="api_base" label="API地址" min-width="220" show-overflow-tooltip />
        <el-table-column prop="version" label="版本" min-width="100" show-overflow-tooltip />
        <el-table-column prop="quota_limit" label="配额" min-width="100" />
        <el-table-column prop="quota_used" label="已用" min-width="100" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.available ? 'success' : 'info'" effect="plain">
              {{ row.available ? "启用" : "停用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="180" />
        <el-table-column fixed="right" label="操作" align="center" width="280">
          <template #default="{ row }">
            <el-button
              v-hasPerm="['module_model:registry:test']"
              type="primary"
              size="small"
              link
              :icon="Connection"
              @click="handleTest(row)"
            >
              连通性
            </el-button>
            <el-button
              v-hasPerm="['module_model:registry:update']"
              type="primary"
              size="small"
              link
              :icon="Edit"
              @click="openEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['module_model:registry:available']"
              :type="row.available ? 'warning' : 'success'"
              size="small"
              link
              :icon="row.available ? VideoPause : VideoPlay"
              @click="toggleAvailable(row)"
            >
              {{ row.available ? "停用" : "启用" }}
            </el-button>
            <el-button
              v-hasPerm="['module_model:registry:delete']"
              type="danger"
              size="small"
              link
              :icon="Delete"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <div class="flex justify-end mt-4">
          <Pagination
            v-model:total="total"
            v-model:page="pagination.page_no"
            v-model:limit="pagination.page_size"
            @pagination="handlePagination"
          />
        </div>
      </template>
    </el-card>

    <el-dialog
      v-model="formVisible"
      :title="formMode === 'create' ? '新建模型' : '编辑模型'"
      width="700px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入模型名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商" prop="provider">
              <el-input v-model="form.provider" placeholder="请输入供应商" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="类型" prop="type">
              <el-select v-model="form.type" placeholder="请选择模型类型" style="width: 100%">
                <el-option
                  v-for="item in dictStore.getDictArray('model_type')"
                  :key="item.dict_value"
                  :label="item.dict_label"
                  :value="item.dict_value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="版本" prop="version">
              <el-input v-model="form.version" placeholder="请输入版本号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="API地址" prop="api_base">
          <el-input v-model="form.api_base" placeholder="请输入API地址" />
        </el-form-item>
        <el-form-item label="API密钥" prop="api_key">
          <el-input
            v-model="form.api_key"
            type="password"
            show-password
            placeholder="请输入API密钥"
          />
        </el-form-item>
        <!-- <el-form-item label="配额限制" prop="quota_limit">
          <el-input-number v-model="form.quota_limit" :min="0" style="width: 100%" />
        </el-form-item> -->
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button
          v-hasPerm="[
            formMode === 'create' ? 'module_model:registry:create' : 'module_model:registry:update',
          ]"
          type="primary"
          :loading="submitting"
          @click="handleSubmit"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: "ModelRegistry" });
import { ref, reactive, onMounted } from "vue";
import { useDictStore } from "@/store/index";
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from "element-plus";
import {
  Search,
  Refresh,
  Plus,
  Delete,
  Edit,
  Connection,
  VideoPlay,
  VideoPause,
} from "@element-plus/icons-vue";
import {
  ModelRegistryAPI,
  type ModelItem,
  type ModelForm,
  type ModelPageQuery,
} from "@/api/module_model/registry";

const dictStore = useDictStore();
const formRef = ref<FormInstance>();

const loading = ref(false);
const items = ref<ModelItem[]>([]);
const selected = ref<ModelItem[]>([]);
const total = ref(0);
const pagination = reactive({ page_no: 1, page_size: 10 });
const queryForm = reactive<ModelPageQuery>({
  name: undefined,
  provider: undefined,
  available: undefined,
  page_no: 1,
  page_size: 10,
});

const formVisible = ref(false);
const formMode = ref<"create" | "edit">("create");
const submitting = ref(false);
const form = reactive<ModelForm>({
  name: "",
  provider: "",
  type: "",
  api_base: "",
  api_key: "",
  version: "",
  quota_limit: 0,
  description: "",
});
let editingId: number | null = null;

const rules: FormRules = {
  name: [{ required: true, message: "请输入模型名称", trigger: "blur" }],
  provider: [{ required: true, message: "请输入供应商", trigger: "blur" }],
  type: [{ required: true, message: "请选择模型类型", trigger: "change" }],
  api_base: [{ required: true, message: "请输入API地址", trigger: "blur" }],
};

async function loadList() {
  loading.value = true;
  try {
    const resp = await ModelRegistryAPI.getList({
      name: queryForm.name,
      provider: queryForm.provider,
      available: queryForm.available,
      page_no: pagination.page_no,
      page_size: pagination.page_size,
    });
    const page = resp.data?.data;
    items.value = page?.items || [];
    total.value = page?.total || 0;
  } finally {
    loading.value = false;
  }
}

function handleSelectionChange(rows: ModelItem[]) {
  selected.value = rows;
}

function handlePagination(params: { page: number; limit: number }) {
  pagination.page_no = params.page;
  pagination.page_size = params.limit;
  loadList();
}

async function handleQuery() {
  pagination.page_no = 1;
  await loadList();
}

async function handleResetQuery() {
  queryForm.name = undefined;
  queryForm.provider = undefined;
  queryForm.available = undefined;
  pagination.page_no = 1;
  await loadList();
}

function openCreate() {
  formMode.value = "create";
  Object.assign(form, {
    name: "",
    provider: "",
    type: "",
    api_base: "",
    api_key: "",
    version: "",
    quota_limit: 0,
    description: "",
  });
  formVisible.value = true;
  // 重置表单校验
  setTimeout(() => formRef.value?.clearValidate(), 0);
}

function openEdit(row: ModelItem) {
  formMode.value = "edit";
  editingId = row.id || null;
  Object.assign(form, {
    name: row.name || "",
    provider: row.provider || "",
    type: row.type || "",
    api_base: row.api_base || "",
    api_key: "",
    version: row.version || "",
    quota_limit: row.quota_limit || 0,
    description: row.description || "",
  });
  formVisible.value = true;
  // 重置表单校验
  setTimeout(() => formRef.value?.clearValidate(), 0);
}

async function handleSubmit() {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        submitting.value = true;
        if (formMode.value === "create") {
          await ModelRegistryAPI.create(form);
        } else if (editingId) {
          await ModelRegistryAPI.update(editingId, form);
        }
        formVisible.value = false;
        await loadList();
      } finally {
        submitting.value = false;
      }
    }
  });
}

async function handleDelete(row: ModelItem) {
  try {
    await ElMessageBox.confirm(`确定要删除 ${row.name} 吗？`, "确认删除", { type: "warning" });
    await ModelRegistryAPI.delete([row.id as number]);
    await loadList();
  } catch (e) {
    if (e !== "cancel") {
      ElMessage.error("删除失败");
    }
  }
}

async function batchDelete() {
  if (selected.value.length === 0) return;
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selected.value.length} 条记录吗？`, "确认删除", {
      type: "warning",
    });
    await ModelRegistryAPI.delete(selected.value.map((i) => i.id as number));
    await loadList();
  } catch (e) {
    if (e !== "cancel") {
      ElMessage.error("删除失败");
    }
  }
}

async function handleTest(row: ModelItem) {
  const resp = await ModelRegistryAPI.test(row.id as number);
  const data = resp.data?.data;
  if (data?.success) {
  } else {
    ElMessage.error(`连通性测试失败: ${data?.msg || ""}`);
  }
}

async function toggleAvailable(row: ModelItem) {
  await ModelRegistryAPI.setAvailable({ ids: [row.id as number], status: !row.available });
  await loadList();
}

async function batchEnable(status: boolean) {
  await ModelRegistryAPI.setAvailable({ ids: selected.value.map((i) => i.id as number), status });
  await loadList();
}

onMounted(async () => {
  // 加载字典数据
  await dictStore.getDict(["model_type"]);
  loadList();
});
</script>

<style scoped>
:deep(.el-tag) {
  font-weight: 500;
}
</style>
