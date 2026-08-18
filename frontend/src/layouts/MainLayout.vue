<template>
  <div class="layout-admin-wrapper">
    <div class="layout-container-vertical fixed">
      <Sidebar :isCollapse="isCollapse" />
      <div class="layout-main" :class="{ 'is-collapse': isCollapse }">
        <div class="layout-header fixed-header" :class="{ 'is-collapse': isCollapse }">
          <Header :isCollapse="isCollapse" @toggle-collapse="toggleCollapse" @refresh="refreshRoute" />
          <TabsBar />
        </div>
        <div class="app-main-container">
          <el-main>
            <router-view :key="routeKey" />
          </el-main>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import Header from '../components/Header.vue'
import TabsBar from '../components/TabsBar.vue'

const isCollapse = ref(false)
const routeKey = ref(0)

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}
const refreshRoute = () => {
  routeKey.value += 1
}
</script>

<style scoped lang="scss">
@mixin fix-header {
  position: fixed;
  top: 0;
  right: 0;
  z-index: $base-z-index - 2;
  width: calc(100% - $base-left-menu-width);
}

.layout-admin-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: auto;

  .layout-container-vertical {
    &.fixed {
      padding-top: calc(#{$base-top-bar-height} + #{$base-tabs-bar-height});
    }

    .layout-main {
      min-height: 100%;
      margin-left: $base-left-menu-width;

      &.is-collapse {
        margin-left: $base-left-menu-width-min;
        border-right: 0;
      }

      .layout-header {
        box-shadow: 0 1px 4px rgb(0 21 41 / 8%);

        &.fixed-header {
          @include fix-header;
        }

        &.is-collapse {
          width: calc(100% - $base-left-menu-width-min);
        }
      }

      .app-main-container {
        padding: $base-padding;
        background: #f0f2f5;
        min-height: calc(100vh - #{$base-header-height});
      }
    }
  }
}
</style>
