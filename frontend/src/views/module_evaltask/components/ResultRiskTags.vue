<template>
  <div>
    <el-tag v-if="level === 'Low'" type="success">Low</el-tag>
    <el-tag v-else-if="level === 'Medium'" type="warning">Medium</el-tag>
    <el-tag v-else-if="level === 'High'" type="danger">High</el-tag>
    <el-tag v-else-if="level === 'Critical'" type="danger">Critical</el-tag>
    <el-tag v-else type="info">-</el-tag>
  </div>
</template>

<script setup lang="ts">
defineProps<{ level?: string | null }>();
</script>

<style scoped>
</style>