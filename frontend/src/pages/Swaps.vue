<template>
  <div>
    <h1 class="brand">对调</h1>
    <p class="muted">先生成周表，再填写两格对调（day + task_id）。pending 单可由对方提交反案，确认时须显式选择原案或反案。</p>
    <div class="week-card" style="margin-bottom:12px">
      <label>A day <input type="number" v-model.number="form.a_day" /></label>
      <label>A task_id <input type="number" v-model.number="form.a_task" /></label>
      <label>B day <input type="number" v-model.number="form.b_day" /></label>
      <label>B task_id <input type="number" v-model.number="form.b_task" /></label>
      <button @click="request">申请对调</button>
    </div>
    <p v-if="err" class="err">{{ err }}</p>
    <ul class="list">
      <li v-for="s in rows" :key="s.id" style="margin-bottom:10px">
        <div>
          #{{ s.id }}
          <span class="chip" :class="{ coral: s.status==='pending' }">{{ s.status }}</span>
          <span v-if="s.selected" class="chip">已选：{{ s.selected === 'counter' ? '反案' : '原案' }}</span>
        </div>
        <div>原案：{{ fmt(s.original) }}</div>
        <div v-if="s.counter">反案：{{ fmt(s.counter) }}</div>
        <template v-if="s.status==='pending'">
          <div class="week-card" style="margin:6px 0">
            <label>反案 A day <input type="number" v-model.number="cforms[s.id].a_day" /></label>
            <label>A task <input type="number" v-model.number="cforms[s.id].a_task" /></label>
            <label>B day <input type="number" v-model.number="cforms[s.id].b_day" /></label>
            <label>B task <input type="number" v-model.number="cforms[s.id].b_task" /></label>
            <button @click="counter(s.id)">提交反案</button>
          </div>
          <button @click="confirm(s.id,'original')">按原案确认改表</button>
          <button :disabled="!s.counter" @click="confirm(s.id,'counter')">按反案确认改表</button>
        </template>
      </li>
    </ul>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'
const rows = ref([])
const err = ref('')
const form = ref({ a_day: 0, a_task: 1, b_day: 1, b_task: 1 })
const cforms = ref({})
function fmt(q) {
  if (!q) return '—'
  return `D${q.a_day}/T${q.a_task}(${q.a_member_name ?? q.a_member}) ↔ D${q.b_day}/T${q.b_task}(${q.b_member_name ?? q.b_member})`
}
async function load() {
  rows.value = await api('/swaps')
  for (const s of rows.value) {
    if (!(s.id in cforms.value) && s.status === 'pending') {
      cforms.value[s.id] = { a_day: 0, a_task: 1, b_day: 1, b_task: 1 }
    }
  }
}
async function request() {
  err.value = ''
  try {
    await api('/weeks/1/swaps', { method: 'POST', body: JSON.stringify(form.value) })
    await load()
  } catch (e) { err.value = e.message }
}
async function counter(id) {
  err.value = ''
  try {
    await api('/swaps/' + id + '/counter', { method: 'POST', body: JSON.stringify(cforms.value[id]) })
    await load()
  } catch (e) { err.value = e.message }
}
async function confirm(id, proposal) {
  err.value = ''
  try {
    await api('/swaps/' + id + '/confirm', { method: 'POST', body: JSON.stringify({ proposal }) })
    await load()
  } catch (e) { err.value = e.message }
}
onMounted(load)
</script>
