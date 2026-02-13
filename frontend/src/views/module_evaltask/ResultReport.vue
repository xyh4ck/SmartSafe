<template>
  <div class="p-4 h-full overflow-auto bg-gray-50">
    <!-- Header Area -->
    <div class="mb-6 flex justify-between items-center bg-white p-4 rounded-lg shadow-sm">
      <div class="flex items-center gap-4">
        <el-button circle icon="Back" @click="$router.back()" />
        <div>
          <h2 class="text-xl font-bold text-gray-800">评测结果报告</h2>
          <div class="flex items-center gap-2 mt-1">
            <el-tag size="small" effect="plain">Task ID: {{ taskId }}</el-tag>
          </div>
        </div>
      </div>
      <div>
        <!-- Future actions like Export can go here -->
      </div>
    </div>

    <!-- Summary Statistics -->
    <el-row :gutter="20" class="mb-6">
      <!-- Metric Count Card -->
      <el-col :xs="24" :sm="8" :md="6">
        <el-card shadow="hover" class="h-full border-none stats-card">
          <div class="text-center py-4">
            <div class="text-gray-500 text-sm mb-2 font-medium">评测维度总数</div>
            <div class="text-4xl font-bold text-primary">
              {{ Object.keys(result?.metrics || {}).length }}
              <span class="text-sm text-gray-400 font-normal">个</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Risk Level Distribution -->
      <el-col :xs="24" :sm="16" :md="18">
        <el-card shadow="hover" class="h-full border-none">
          <template #header>
            <div class="font-medium text-gray-700">风险等级分布</div>
          </template>
          <div class="flex flex-wrap justify-around items-center h-full py-2 gap-4">
            <div 
              v-for="level in levelOrder" 
              :key="level" 
              class="text-center min-w-[80px] p-2 rounded-lg bg-gray-50"
            >
              <div class="text-2xl font-bold mb-1" :class="getLevelColor(level)">
                {{ result?.summary?.level_distribution?.[level] || 0 }}
              </div>
              <div class="text-gray-500 text-xs uppercase tracking-wider">{{ level }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts Section -->
    <el-card class="mb-6 border-none" shadow="hover">
      <template #header>
        <div class="flex items-center gap-2 border-l-4 border-blue-500 pl-3">
          <span class="text-lg font-bold text-gray-800">维度评分详情</span>
        </div>
      </template>
      <div class="p-2">
        <ResultCharts :metrics="result?.metrics || {}" />
      </div>
    </el-card>

    <!-- Top Risks Table -->
    <el-card class="border-none" shadow="hover">
      <template #header>
        <div class="flex items-center gap-2 border-l-4 border-red-500 pl-3">
          <span class="text-lg font-bold text-gray-800">Top 10 风险样本</span>
        </div>
      </template>
      <el-table 
        :data="result?.top_risks || []" 
        stripe 
        style="width: 100%"
        :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
      >
        <el-table-column prop="case_id" label="用例ID" width="180" show-overflow-tooltip>
          <template #default="{ row }">
             <span class="font-mono text-blue-600">{{ row.case_id }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="综合风险分" width="150" align="center">
          <template #default="{ row }">
            <span class="text-lg font-bold text-red-600">{{ sumScores(row.scores || {}) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="分值构成详情" min-width="300">
          <template #default="{ row }">
            <div class="flex flex-wrap gap-2">
              <el-tag 
                v-for="(v,k) in row.scores" 
                :key="k" 
                class="mr-1 mb-1"
                type="info" 
                effect="light"
                size="default"
              >
                <span class="font-medium text-gray-700">{{ k }}</span>: 
                <span class="font-bold ml-1" :class="getScoreColor(v)">{{ v }}</span>
              </el-tag>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: "EvalTaskReport", inheritAttrs: false });

import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { useRoute, useRouter } from "vue-router";
import EvalTaskAPI, { EvalTaskResult } from "@/api/module_evaltask/task";
import ResultCharts from "./components/ResultCharts.vue";

const route = useRoute();
const router = useRouter(); // Ensure router is available for back button
const taskId = Number(route.params.taskId as string);
const result = ref<EvalTaskResult | null>(null);

// Helper constants
const levelOrder = ['Low', 'Medium', 'High', 'Critical'];

const sumScores = (scores: Record<string, number>) => Object.values(scores).reduce((a, b) => a + b, 0).toFixed(2);

const getLevelColor = (level: string) => {
  const colors: Record<string, string> = {
    'Low': 'text-green-500',
    'Medium': 'text-yellow-500',
    'High': 'text-orange-500',
    'Critical': 'text-red-600'
  };
  return colors[level] || 'text-gray-500';
};

const getScoreColor = (score: number) => {
  if (score >= 0.8) return 'text-red-600';
  if (score >= 0.5) return 'text-orange-500';
  return 'text-green-600';
};

const loadData = async () => {
  try {
    const res = await EvalTaskAPI.getTaskResult(taskId);
    result.value = res.data.data || null;
  } catch (e) {
    ElMessage.error("加载失败");
  }
};

onMounted(loadData);
</script>

<style scoped>
.stats-card {
  background: linear-gradient(to bottom right, #ffffff, #f9fafb);
}
</style>