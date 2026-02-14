<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <!-- 雷达图：维度能力模型 -->
    <el-card shadow="hover" class="border-none">
      <template #header>
        <div class="flex items-center justify-between">
          <span class="font-bold text-gray-700">维度能力模型</span>
          <el-tooltip content="展示各维度的得分分布，越向外得分越高" placement="top">
            <el-icon class="text-gray-400 cursor-pointer"><InfoFilled /></el-icon>
          </el-tooltip>
        </div>
      </template>
      <div class="h-[300px] w-full">
        <ECharts :options="radarOption" height="100%" width="100%" />
      </div>
    </el-card>

    <!-- 柱状图：维度得分排行 -->
    <el-card shadow="hover" class="border-none">
      <template #header>
        <div class="flex items-center justify-between">
          <span class="font-bold text-gray-700">维度得分排行</span>
          <el-tooltip content="各维度得分从高到低排序" placement="top">
            <el-icon class="text-gray-400 cursor-pointer"><InfoFilled /></el-icon>
          </el-tooltip>
        </div>
      </template>
      <div class="h-[300px] w-full">
        <ECharts :options="barOption" height="100%" width="100%" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { InfoFilled } from "@element-plus/icons-vue";
import ECharts from "@/components/ECharts/index.vue";
import type { EChartsOption } from "echarts";

const props = defineProps<{ metrics: Record<string, number> }>();

// 维度数据处理
const dimensions = computed(() => Object.keys(props.metrics || {}));
const scores = computed(() => Object.values(props.metrics || {}).map((v) => Number((v * 100).toFixed(1))));

// 雷达图配置
const radarOption = computed<EChartsOption>(() => {
  if (dimensions.value.length === 0) return {};

  const maxVal = 100;
  
  return {
    tooltip: {
      trigger: 'item'
    },
    radar: {
      indicator: dimensions.value.map((name) => ({
        name,
        max: maxVal,
      })),
      splitNumber: 4,
      axisName: {
        color: '#666',
        fontSize: 12
      },
      splitArea: {
        areaStyle: {
          color: ['#f8f9fa', '#f8f9fa', '#f8f9fa', '#f8f9fa'],
          shadowColor: 'rgba(0, 0, 0, 0.1)',
          shadowBlur: 10
        }
      }
    },
    series: [
      {
        name: '维度评分',
        type: 'radar',
        data: [
          {
            value: scores.value,
            name: '当前任务',
            itemStyle: {
              color: '#409eff'
            },
            areaStyle: {
              color: 'rgba(64, 158, 255, 0.2)'
            },
            lineStyle: {
              width: 2
            }
          }
        ]
      }
    ]
  };
});

// 柱状图配置
const barOption = computed<EChartsOption>(() => {
  if (dimensions.value.length === 0) return {};

  // 排序数据
  const data = dimensions.value.map((name, index) => ({
    name,
    value: scores.value[index]
  })).sort((a, b) => a.value - b.value); 

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: '{b}: {c}分'
    },
    grid: {
      top: '10%',
      left: '3%',
      right: '10%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      max: 100,
      splitLine: {
        lineStyle: {
          type: 'dashed'
        }
      }
    },
    yAxis: {
      type: 'category',
      data: data.map(item => item.name),
      axisLabel: {
        width: 100,
        overflow: 'truncate'
      }
    },
    series: [
      {
        name: '得分',
        type: 'bar',
        data: data.map(item => ({
          value: item.value,
          itemStyle: {
            color: ((params: any) => {
              const val = params.value;
              if (val >= 80) return '#67c23a';
              if (val >= 60) return '#e6a23c';
              return '#f56c6c';
            }) as any
          }
        })),
        barWidth: '60%',
        label: {
          show: true,
          position: 'right',
          formatter: '{c}分'
        }
      }
    ]
  } as any;
});
</script>
