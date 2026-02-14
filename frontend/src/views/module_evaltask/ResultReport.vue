<template>
  <div class="p-4 h-full overflow-auto bg-gray-50 min-h-screen">
    <!-- 头部区域 -->
    <div class="mb-4 flex justify-between items-center bg-white p-4 rounded-lg shadow-sm">
      <div class="flex items-center gap-4">
        <el-button circle icon="Back" @click="$router.back()" />
        <div>
          <h2 class="text-xl font-bold text-gray-800">评测结果报告</h2>
          <div class="flex items-center gap-2 mt-1">
            <el-tag type="info" size="small" effect="plain" class="font-mono">Task ID: {{ taskId }}</el-tag>
            <el-tag v-if="result" :type="getStatusType(resultSummary.status)" size="small">
               {{ resultSummary.status || '已完成' }}
            </el-tag>
          </div>
        </div>
      </div>
      <div>
         <el-button
          type="primary"
          plain
          icon="Download"
          @click="handleExportReport"
          :loading="exportLoading"
          :disabled="!canExportReport"
        >
          导出报告
        </el-button>
      </div>
    </div>

    <!-- 核心指标卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
      <!-- 合格率 -->
      <el-card shadow="hover" class="border-none">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-blue-50 text-blue-500 mr-4">
             <el-icon class="text-2xl"><PieChart /></el-icon>
          </div>
          <div>
            <div class="text-gray-500 text-sm mb-1">合格率 (Low风险)</div>
            <div class="text-2xl font-bold text-gray-800">
               {{ resultSummary.qualified_rate || 0 }}<span class="text-sm text-gray-400 ml-1">%</span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 总用例数 -->
      <el-card shadow="hover" class="border-none">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-purple-50 text-purple-500 mr-4">
             <el-icon class="text-2xl"><Tickets /></el-icon>
          </div>
          <div>
            <div class="text-gray-500 text-sm mb-1">测试用例总数</div>
            <div class="text-2xl font-bold text-gray-800">
               {{ resultSummary.total_cases || 0 }}
            </div>
          </div>
        </div>
      </el-card>

      <!-- 成功/失败 -->
      <el-card shadow="hover" class="border-none">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-green-50 text-green-500 mr-4">
             <el-icon class="text-2xl"><CircleCheckFilled /></el-icon>
          </div>
          <div>
            <div class="text-gray-500 text-sm mb-1">执行成功</div>
            <div class="text-2xl font-bold text-gray-800">
               {{ resultSummary.succeeded_cases || 0 }}
            </div>
          </div>
        </div>
      </el-card>

       <!-- 风险数 -->
       <el-card shadow="hover" class="border-none">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-red-50 text-red-500 mr-4">
             <el-icon class="text-2xl"><WarningFilled /></el-icon>
          </div>
          <div>
            <div class="text-gray-500 text-sm mb-1">高危风险数 (High+)</div>
            <div class="text-2xl font-bold text-red-600">
               {{ (resultSummary.level_distribution?.High || 0) + (resultSummary.level_distribution?.Critical || 0) }}
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 图表分析区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
      <!-- 风险分布饼图 -->
      <el-col :span="24" class="lg:col-span-1">
        <el-card shadow="hover" class="border-none h-full">
           <template #header>
            <div class="font-bold text-gray-700 flex items-center">
              <el-icon class="mr-2 text-orange-500"><DataAnalysis /></el-icon>
              风险等级分布
            </div>
          </template>
          <div class="h-[300px]">
            <ECharts :options="riskPieOption" height="100%" width="100%" />
          </div>
        </el-card>
      </el-col>

      <!-- 维度分析（占用2列） -->
      <el-col :span="24" class="lg:col-span-2">
         <ResultCharts :metrics="result?.metrics || {}" />
      </el-col>
    </div>

    <!-- Top 10 风险详情 -->
    <el-card class="border-none mb-4" shadow="hover">
      <template #header>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2 border-l-4 border-red-500 pl-3">
            <span class="text-lg font-bold text-gray-800">Top 10 风险样本</span>
            <el-tag type="danger" size="small" effect="plain">按综合风险分排序</el-tag>
          </div>
        </div>
      </template>
      
      <el-table 
        :data="result?.top_risks || []" 
        stripe 
        style="width: 100%"
        :header-cell-style="{ background: '#f8fafc', color: '#475569', fontWeight: 'bold' }"
      >
        <el-table-column prop="case_id" label="用例ID" width="100" align="center">
          <template #default="{ row }">
             <span class="font-mono text-gray-600">#{{ row.case_id }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="综合风险分" width="120" align="center" sortable :sort-method="sortRisksByScore">
          <template #default="{ row }">
            <div class="flex items-center justify-center">
               <span class="text-lg font-bold text-red-600">{{ sumScores(row.scores || {}) }}</span>
            </div>
          </template>
        </el-table-column>

         <el-table-column label="风险详情" min-width="400">
          <template #default="{ row }">
            <div class="flex flex-wrap gap-2">
              <template v-for="(score, name) in row.scores">
                <el-tooltip :key="name" :content="`${name}: ${score}`" placement="top" v-if="Number(score) > 0">
                   <el-tag 
                    :type="getScoreTagType(score)" 
                    effect="light"
                    class="border-0"
                  >
                    <span class="font-medium">{{ name }}</span>
                    <span class="ml-1 font-bold opacity-80">{{ score }}</span>
                  </el-tag>
                </el-tooltip>
              </template>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="100" align="center" fixed="right">
           <template #default="{ row }">
             <el-button link type="primary" size="small" @click="viewCaseDetail(row.case_id)">查看</el-button>
           </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 底部版权或说明 -->
    <div class="text-center text-gray-400 text-xs py-4">
      SmartSafe Evaluation Report &copy; {{ new Date().getFullYear() }}
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: "EvalTaskReport", inheritAttrs: false });

import { ref, onMounted, computed } from "vue";
import { ElMessage } from "element-plus";
import { useRoute, useRouter } from "vue-router";
import {
  Back,
  Download,
  PieChart,
  Tickets,
  CircleCheckFilled,
  WarningFilled,
  DataAnalysis,
} from "@element-plus/icons-vue";
import EvalTaskAPI, { EvalTaskResult } from "@/api/module_evaltask/task";
import ResultCharts from "./components/ResultCharts.vue";
import ECharts from "@/components/ECharts/index.vue";
import type { EChartsOption } from "echarts";

const route = useRoute();
const router = useRouter();
const taskId = Number(route.params.taskId as string);
const result = ref<EvalTaskResult | null>(null);
const exportLoading = ref(false);

const resultSummary = computed(() => result.value?.summary || {});
const canExportReport = computed(() => Boolean(result.value?.task_id));

// 风险等级颜色映射
const levelColors = {
  Low: '#67c23a',
  Medium: '#e6a23c',
  High: '#f56c6c',
  Critical: '#8b0000'
};

// 饼图配置
const riskPieOption = computed<EChartsOption>(() => {
  const dist = (resultSummary.value.level_distribution || {}) as Record<string, number>;
  const data = Object.entries(dist).map(([name, value]) => ({
    name,
    value: value as number,
    itemStyle: { color: levelColors[name as keyof typeof levelColors] || '#909399' }
  })).filter(item => item.value > 0);

  if (data.length === 0) {
    return {
      title: {
         text: '暂无数据',
         left: 'center',
         top: 'center',
         textStyle: { color: '#909399', fontSize: 14 }
      }
    };
  }

  return {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: 'bottom',
      icon: 'circle'
    },
    series: [
      {
        name: '风险分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 4,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: data
      }
    ]
  } as any;
});

const sumScores = (scores: Record<string, any> = {}) => {
  const total = Object.values(scores).reduce((acc: number, cur: any) => acc + (Number(cur) || 0), 0);
  return Number(total.toFixed(2));
};

const sortRisksByScore = (a: any, b: any) => {
  return sumScores(a.scores) - sumScores(b.scores);
};

const getScoreTagType = (score: number | string | unknown) => {
  const s = Number(score);
  if (s >= 0.8) return 'danger';
  if (s >= 0.5) return 'warning';
  return 'info';
};

const getStatusType = (status?: string) => {
  if (status === 'completed') return 'success';
  if (status === 'failed') return 'danger';
  return 'primary';
};

const loadData = async () => {
  try {
    const res = await EvalTaskAPI.getTaskResult(taskId);
    result.value = res.data.data || null;
  } catch (e) {
    ElMessage.error("加载报告数据失败");
  }
};

const handleExportReport = async () => {
  if (!canExportReport.value) {
    ElMessage.warning("任务执行完毕后才可导出报告");
    return;
  }

  exportLoading.value = true;
  try {
    const res = await EvalTaskAPI.exportTaskReport(taskId);
    const fileData = res.data;
    const disposition = String(res.headers?.["content-disposition"] || "");

    let fileName = `evaltask_report_${taskId}.pdf`;
    if (disposition.includes("filename=")) {
      fileName = decodeURI(disposition.split("filename=")[1].replace(/"/g, "").trim());
    }

    const fileType = "application/pdf";
    const blob = new Blob([fileData], { type: fileType });
    const downloadUrl = window.URL.createObjectURL(blob);
    const downloadLink = document.createElement("a");
    downloadLink.href = downloadUrl;
    downloadLink.download = fileName;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
    window.URL.revokeObjectURL(downloadUrl);

    ElMessage.success("导出成功");
  } catch (e: any) {
    ElMessage.error(e?.message || "导出失败");
  } finally {
    exportLoading.value = false;
  }
};

const viewCaseDetail = (caseId: number) => {
  router.push({
     name: 'EvalTaskDetail', 
     params: { taskId: String(taskId) }, 
     query: { case_id: caseId } 
  });
};

onMounted(loadData);
</script>

<style scoped>
/* 覆盖 Element Card 样式以适配 Dashboard */
:deep(.el-card__header) {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}
:deep(.el-card__body) {
  padding: 16px;
  height: 100%;
}
</style>
