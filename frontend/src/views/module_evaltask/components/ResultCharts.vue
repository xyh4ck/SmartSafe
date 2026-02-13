<template>
  <div>
    <el-row :gutter="10">
      <el-col v-for="(v,k) in metrics" :key="k" :xs="24" :sm="12" :md="8">
        <el-card class="mb-3" shadow="never">
          <template #header>
            <span>{{ k }}</span>
          </template>
          <div class="flex items-center">
            <el-progress :percentage="Math.round((v as number) * 100)" style="width: 200px" />
            <span class="ml-3 text-gray">{{ (v as number).toFixed(2) }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
defineProps<{ metrics: Record<string, number> }>();
</script>

<style scoped>
.mb-3 { margin-bottom: 12px; }
</style>