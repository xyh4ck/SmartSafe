<template>
  <div class="dashboard-container">
    <el-card shadow="hover">
      <div class="flex flex-wrap">
        <!-- 左侧问候语区域 -->
        <div class="flex-1 flex items-start">
          <img
            class="w80px h80px rounded-full"
            :src="userStore.basicInfo.avatar + '?imageView2/1/w/80/h/80'"
          />
          <div class="ml-5">
            <div class="text-20px font-bold mb-5px">
              {{ timefix }}{{ userStore.basicInfo.name }}，{{ welcome }}
            </div>
            <p class="text-sm text-gray">今日天气晴朗，气温在15℃至25℃之间，东南风。</p>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "Home",
  inheritAttrs: false,
});

import { useUserStore } from "@/store/modules/user.store";
import { greetings } from "@/utils/common";

const timefix = greetings();
const welcome = "祝你开心每一天！";

const userStore = useUserStore();
</script>

<style lang="scss" scoped>
.dashboard-container {
  position: relative;
  padding: 16px;
}
</style>
