<template>
  <n-card title="📈 张力心电图" size="small" :bordered="true">
    <template #header-extra>
      <n-tag v-if="hasLowTension" type="warning" size="small">
        ⚠️ 检测到低张力章节
      </n-tag>
    </template>

    <div ref="chartRef" class="chart-container"></div>

    <!-- 低张力警告 -->
    <n-alert v-if="hasLowTension" type="warning" :show-icon="false" style="margin-top: 8px; font-size: 12px">
      建议插入缓冲章或调整剧情节奏
    </n-alert>
  </n-card>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

interface TensionData {
  chapter_number: number
  tension_score: number
  title?: string
}

const props = defineProps<{
  novelId: string
  threshold?: number  // 张力警戒线，默认 5.0
}>()

const emit = defineEmits<{
  'chapter-click': [chapterNumber: number]
  'low-tension-alert': [chapters: number[]]
}>()

const chartRef = ref<HTMLElement | null>(null)
const tensionData = ref<TensionData[]>([])
const loading = ref(false)

let chartInstance: echarts.ECharts | null = null

// 张力警戒线
const tensionThreshold = computed(() => props.threshold ?? 5.0)

// 是否有低张力章节
const hasLowTension = computed(() => {
  return tensionData.value.some(d => d.tension_score < tensionThreshold.value)
})

// 低张力章节列表
const lowTensionChapters = computed(() => {
  return tensionData.value
    .filter(d => d.tension_score < tensionThreshold.value)
    .map(d => d.chapter_number)
})

// 加载张力数据
async function loadTensionData() {
  loading.value = true
  try {
    const res = await fetch(`/api/v1/novels/${props.novelId}/tension-history`)
    if (res.ok) {
      const data = await res.json()
      tensionData.value = data.tension_history || []

      // 触发低张力警告
      if (lowTensionChapters.value.length > 0) {
        emit('low-tension-alert', lowTensionChapters.value)
      }

      await nextTick()
      renderChart()
    }
  } catch (err) {
    console.error('Failed to load tension data:', err)
  } finally {
    loading.value = false
  }
}

// 渲染图表
function renderChart() {
  if (!chartRef.value || tensionData.value.length === 0) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const chapterNumbers = tensionData.value.map(d => d.chapter_number)
  const tensionScores = tensionData.value.map(d => d.tension_score)

  const option: echarts.EChartsOption = {
    grid: {
      left: 40,
      right: 20,
      top: 30,
      bottom: 30
    },
    xAxis: {
      type: 'category',
      data: chapterNumbers,
      name: '章节',
      nameLocation: 'middle',
      nameGap: 25,
      axisLine: {
        lineStyle: { color: '#666' }
      },
      axisLabel: {
        color: '#999',
        fontSize: 11
      }
    },
    yAxis: {
      type: 'value',
      name: '张力值',
      min: 0,
      max: 10,
      interval: 2,
      axisLine: {
        lineStyle: { color: '#666' }
      },
      axisLabel: {
        color: '#999',
        fontSize: 11
      },
      splitLine: {
        lineStyle: {
          color: '#333',
          type: 'dashed'
        }
      }
    },
    series: [
      {
        type: 'line',
        data: tensionScores,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          width: 2,
          color: '#18a058'
        },
        itemStyle: {
          color: '#18a058',
          borderWidth: 2,
          borderColor: '#fff'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(24, 160, 88, 0.3)' },
            { offset: 1, color: 'rgba(24, 160, 88, 0.05)' }
          ])
        },
        markLine: {
          silent: true,
          symbol: 'none',
          label: {
            formatter: '警戒线',
            position: 'end',
            color: '#f0a020',
            fontSize: 11
          },
          lineStyle: {
            color: '#f0a020',
            type: 'dashed',
            width: 2
          },
          data: [
            { yAxis: tensionThreshold.value }
          ]
        },
        markPoint: {
          symbol: 'pin',
          symbolSize: 40,
          label: {
            fontSize: 10,
            color: '#fff'
          },
          data: [
            {
              type: 'max',
              name: '最高',
              itemStyle: { color: '#d03050' }
            },
            {
              type: 'min',
              name: '最低',
              itemStyle: { color: '#666' }
            }
          ]
        }
      }
    ],
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#333',
      textStyle: {
        color: '#fff',
        fontSize: 12
      },
      formatter: (params: any) => {
        const data = params[0]
        const chapterNum = data.name
        const tension = data.value
        const chapter = tensionData.value.find(d => d.chapter_number === Number(chapterNum))

        let html = `<div style="padding: 4px 8px;">
          <div style="font-weight: 600; margin-bottom: 4px;">第 ${chapterNum} 章</div>`

        if (chapter?.title) {
          html += `<div style="color: #aaa; font-size: 11px; margin-bottom: 6px;">${chapter.title}</div>`
        }

        html += `<div style="display: flex; align-items: center; gap: 8px;">
          <span style="color: ${getTensionColor(tension)};">张力值: ${tension.toFixed(1)}</span>
          <span style="color: #666;">|</span>
          <span style="color: #aaa; font-size: 11px;">${getTensionLabel(tension)}</span>
        </div>`

        if (tension < tensionThreshold.value) {
          html += `<div style="color: #f0a020; font-size: 11px; margin-top: 4px;">⚠️ 低于警戒线</div>`
        }

        html += `</div>`
        return html
      }
    }
  }

  chartInstance.setOption(option)

  // 点击事件
  chartInstance.off('click')
  chartInstance.on('click', (params: any) => {
    if (params.componentType === 'series') {
      const chapterNumber = Number(params.name)
      emit('chapter-click', chapterNumber)
    }
  })
}

// 获取张力颜色
function getTensionColor(tension: number): string {
  if (tension >= 8) return '#d03050'
  if (tension >= 5) return '#f0a020'
  return '#18a058'
}

// 获取张力标签
function getTensionLabel(tension: number): string {
  if (tension >= 8) return '🔥 高潮'
  if (tension >= 5) return '⚡冲突'
  return '🌊 平缓'
}

// 响应式调整
function handleResize() {
  chartInstance?.resize()
}

// 监听数据变化
watch(() => props.novelId, () => {
  loadTensionData()
})

watch(tensionData, () => {
  renderChart()
})

// 生命周期
onMounted(() => {
  loadTensionData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
  chartInstance = null
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 220px;
}
</style>
