<template>
  <div>
    <h1 class="brand">对调</h1>
    <p class="muted">先生成周表，再填写两格对调（day + task_id）；pending 可提反案，确认须显式选案</p>
    <div class="week-card" style="margin-bottom:12px">
      <label>A day <input type="number" v-model.number="form.a_day" /></label>
      <label>A task_id <input type="number" v-model.number="form.a_task" /></label>
      <label>B day <input type="number" v-model.number="form.b_day" /></label>
      <label>B task_id <input type="number" v-model.number="form.b_task" /></label>
      <button @click="request">申请对调</button>
    </div>
    <p v-if="err" class="err">{{ err }}</p>
    <ul class="list">
      <li v-for="s in rows" :key="s.id">
        <div>
          #{{ s.id }} 原案 D{{ s.a_day }}/T{{ s.a_task }} ↔ D{{ s.b_day }}/T{{ s.b_task }}
          <span class="muted">M{{ s.a_member }}↔M{{ s.b_member }}</span>
          <span class="chip" :class="{ coral: s.status==='pending' }">{{ s.status }}</span>
          <span v-if="s.selected_case" class="chip">选{{ s.selected_case==='counter' ? '反案' : '原案' }}</span>
        </div>
        <div v-if="s.c_a_day !== null" class="muted">
          反案 D{{ s.c_a_day }}/T{{ s.c_a_task }} ↔ D{{ s.c_b_day }}/T{{ s.c_b_task }}
          <span>M{{ s.c_a_member }}↔M{{ s.c_b_member }}</span>
        </div>
        <div v-if="s.status==='pending'" style="margin-top:4px">
          <button @click="confirm(s.id, 'original')">确认原案</button>
          <button v-if="s.c_a_day !== null" style="margin-left:8px" @click="confirm(s.id, 'counter')">确认反案</button>
          <button class="ghost" style="margin-left:8px" @click="toggleCounter(s.id)">提反案</button>
        </div>
        <div v-if="counterFor === s.id" class="week-card" style="margin-top:8px">
          <label>A day <input type="number" v-model.number="counterForm.a_day" /></label>
          <label>A task_id <input type="number" v-model.number="counterForm.a_task" /></label>
          <label>B day <input type="number" v-model.number="counterForm.b_day" /></label>
          <label>B task_id <input type="number" v-model.number="counterForm.b_task" /></label>
          <button @click="submitCounter(s.id)">提交反案</button>
        </div>
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
const counterFor = ref(null)
const counterForm = ref({ a_day: 0, a_task: 1, b_day: 1, b_task: 1 })
async function load() { rows.value = await api('/swaps') }
async function request() {
  err.value = ''
  try {
    await api('/weeks/1/swaps', { method: 'POST', body: JSON.stringify(form.value) })
    await load()
  } catch (e) { err.value = e.message }
}
function toggleCounter(id) { counterFor.value = counterFor.value === id ? null : id }
async function submitCounter(id) {
  err.value = ''
  try {
    await api('/swaps/' + id + '/counter', { method: 'POST', body: JSON.stringify(counterForm.value) })
    counterFor.value = null
    await load()
  } catch (e) { err.value = e.message }
}
async function confirm(id, which) {
  err.value = ''
  try {
    await api('/swaps/' + id + '/confirm', { method: 'POST', body: JSON.stringify({ case: which }) })
    await load()
  } catch (e) { err.value = e.message }
}
onMounted(load)
</script>
