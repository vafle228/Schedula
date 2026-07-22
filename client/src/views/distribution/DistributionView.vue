<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { store } from '../../store/index.js'
import { confirmDelete } from '../../composables/useConfirm.js'
import { initials, avatarBg } from '../../utils/format.js'
import InfoDot from '../../components/InfoDot.vue'
import AssignMenu from './AssignMenu.vue'
import CreateDisciplineModal from './CreateDisciplineModal.vue'
import AddTopicModal from './AddTopicModal.vue'
import CurriculumExportModal from './CurriculumExportModal.vue'
import {
  dui, norm, filtered, progress, dragTopicIds, dragH, hoursOf, teacherOfTopic,
  courseOfGroup, openMenuAt, openMenuEv, commitAssign, resetFilters,
  kindLabel, kindColor, dotRadius, topicIndex, KINDS,
} from './useDistribution.js'

const searchEl = ref(null)

/* ---------- header ---------- */

const periodBtns = [
  { k: 'fall', label: 'Осень' },
  { k: 'spring', label: 'Весна' },
]
const progressPct = computed(() => (progress.value.tot ? Math.round((progress.value.don / progress.value.tot) * 100) : 0))
const canUndo = computed(() => store.state.planUndo.length > 0)
const canRedo = computed(() => store.state.planRedo.length > 0)

/* Switching season: pool, teacher load and progress recompute by period.
   Cancel any in-flight drag and close menus/modals that hold topics or a
   discipline from the season we're leaving, so nothing acts on stale ids. */
function pickSeason(k) {
  if (store.state.period === k) return
  store.setPeriod(k)
  dui.dragKind = null
  dui.dragId = null
  dui.dragOver = null
  dui.menu = null
  dui.ov = false
  dui.cd = null
  dui.addTopic = null
  dui.exp = null
  dui.expDisc = {}
}

/* ---------- filters ---------- */

const statusOpts = [
  { v: 'all', label: 'Статус: все' },
  { v: 'open', label: 'Есть незакрытые' },
  { v: 'done', label: 'Всё закрыто' },
]
const kindOpts = [
  { v: 'all', label: 'Вид: все' },
  ...KINDS.map((k) => ({ v: k.k, label: 'Только: ' + k.label.toLowerCase() })),
]
const courseOpts = [
  { v: 'all', label: 'Курс: все' },
  ...[1, 2, 3, 4].map((c) => ({ v: String(c), label: c + ' курс' })),
]

/* ---------- pool view-model ---------- */

const groupsList = computed(() => {
  const map = {}
  filtered.value.forEach((d) => { (map[d.groupId] = map[d.groupId] || []).push(d) })
  return Object.keys(map).sort().map((g) => {
    const ds = map[g]
    const totalTopics = ds.reduce((n, d) => n + d.topics.length, 0)
    const asgTopics = ds.reduce((n, d) => n + d.topics.filter((tp) => teacherOfTopic(tp.id)).length, 0)
    return {
      label: g,
      meta: (courseOfGroup(g) || '?') + ' курс, тем ' + asgTopics + '/' + totalTopics,
      discs: ds.map(mkDisc),
    }
  })
})

function mkDisc(d) {
  const total = d.topics.length
  const asg = d.topics.filter((tp) => teacherOfTopic(tp.id)).length
  const totalHours = d.topics.reduce((h, tp) => h + tp.hours, 0)
  const full = asg >= total
  return {
    d, total, asg, full,
    hoursLabel: totalHours + ' ч',
    badge: asg + '/' + total,
    badgeColor: full ? '#1F8A5B' : asg ? '#B45309' : '#8A857C',
    badgeBg: full ? 'rgba(31,138,91,0.10)' : asg ? 'rgba(217,119,6,0.10)' : '#F2F0EB',
    expanded: !!dui.expDisc[d.id],
    dragging: dui.dragKind === 'disc' && dui.dragId === d.id,
    dragTitle: full ? 'Все темы назначены' : 'Перетащите на преподавателя — назначатся все незакрытые темы',
    topics: d.topics
      .filter((tp) => dui.fKind === 'all' || tp.kind === dui.fKind)
      .map((tp) => mkTopic(d, tp)),
  }
}

function mkTopic(d, tp) {
  const tid = teacherOfTopic(tp.id)
  const t = tid ? store.teacherById(tid) : null
  return {
    tp, t,
    dotColor: kindColor(tp.kind),
    dotRadius: dotRadius(tp.kind),
    kindLabel: kindLabel(tp.kind),
    hours: tp.hours + ' ч',
    aInit: t && !t.photo ? initials(t.name) : '',
    aBg: t ? avatarBg(t.photo) : '',
    aTitle: t ? t.name + ' — клик снимает назначение' : '',
    dragging: dui.dragKind === 'topic' && dui.dragId === tp.id,
  }
}

function toggleDisc(d) {
  const ex = { ...dui.expDisc }
  if (ex[d.id]) delete ex[d.id]
  else ex[d.id] = true
  dui.expDisc = ex
}

const anyExpanded = computed(() => filtered.value.some((d) => dui.expDisc[d.id]))
function toggleAll() {
  if (anyExpanded.value) { dui.expDisc = {}; return }
  const ex = {}
  filtered.value.forEach((d) => { ex[d.id] = true })
  dui.expDisc = ex
}

/* drag from pool */
function discDragStart(d, e) {
  e.dataTransfer.setData('text/plain', d.id)
  e.dataTransfer.effectAllowed = 'move'
  dui.dragKind = 'disc'
  dui.dragId = d.id
}
function topicDragStart(tp, e) {
  e.stopPropagation()
  e.dataTransfer.setData('text/plain', tp.id)
  e.dataTransfer.effectAllowed = 'move'
  dui.dragKind = 'topic'
  dui.dragId = tp.id
}
function dragEnd() {
  dui.dragKind = null
  dui.dragId = null
  dui.dragOver = null
}

/* assign / unassign */
function assignAll(disc, e) {
  const ids = disc.topics.filter((tp) => !teacherOfTopic(tp.id)).map((tp) => tp.id)
  if (ids.length) openMenuEv(ids, e, 'Назначить все незакрытые темы: ' + disc.name + ' (' + disc.groupId + ')')
}
function topicPlus(d, tp, e) {
  openMenuEv([tp.id], e, kindLabel(tp.kind) + ': ' + tp.name + ', ' + d.name + ' (' + d.groupId + ')')
}
function topicClick(d, tp, e) {
  openMenuAt([tp.id], e.clientX, e.clientY, kindLabel(tp.kind) + ': ' + tp.name + ', ' + d.name)
}
function unassign(tp) {
  commitAssign([{ topicId: tp.id, to: null }])
}
async function removeDisc(d) {
  const n = d.topics.length
  const ok = await confirmDelete({
    title: 'Удалить дисциплину?',
    message: n
      ? `Дисциплина и все её темы (${n}) будут удалены из плана вместе с назначениями и занятиями в расписании. Действие необратимо.`
      : 'Дисциплина будет удалена из плана. Действие необратимо.',
    entityName: `${d.name} · ${d.groupId}`,
  })
  if (ok) store.removeDiscipline(d.id)
}

async function removeTopic(d, tp) {
  const ok = await confirmDelete({
    title: 'Удалить тему?',
    message: 'Тема, её назначение и занятия в расписании будут удалены. Дисциплина сохранится. Действие необратимо.',
    entityName: `${tp.name} · ${d.name}`,
  })
  if (ok) store.removeTopic(tp.id)
}

/* ---------- teachers view-model ---------- */

const teachersList = computed(() => {
  const q = dui.tSearch.trim().toLowerCase()
  return store.state.teachers
    .filter((t) => !q || t.name.toLowerCase().includes(q))
    .map(mkTeacher)
})

function mkTeacher(t) {
  const period = store.state.period
  const h = hoursOf(t.id, period)
  const over = !!(dui.dragOver === t.id && dui.dragId)
  const warn = h > norm
  const { topicById, discOfTopic } = topicIndex.value
  const assigns = []
  for (const topId in store.state.assignments) {
    if (store.state.assignments[topId].teacherId !== t.id) continue
    const d = discOfTopic[topId]
    const tp = topicById[topId]
    if (d && tp && d.period === period) assigns.push({ d, tp })
  }
  return {
    t, h, over, warn, assigns,
    init: over || !t.photo ? initials(t.name) : '',
    avatar: over ? '#3B62C4' : avatarBg(t.photo),
    avatarColor: over ? '#FFFFFF' : t.photo ? 'transparent' : '#5C574E',
    hoursLabel: over ? h + ' → ' + (h + dragH.value) + ' ч' : h + ' / ' + norm + ' ч',
    hoursColor: over ? '#3B62C4' : warn ? '#B45309' : h ? '#5C574E' : '#B5B0A6',
    warnMark: warn && !over ? ' ⚠' : '',
    barPct: Math.min(100, Math.round((h / norm) * 100)) + '%',
    barColor: warn ? '#D97706' : '#8A857C',
    countLabel: over ? '+' + dragTopicIds.value.length : assigns.length ? String(assigns.length) : '—',
    expanded: !!dui.expTeacher[t.id],
  }
}

function toggleTeacher(t) {
  const ex = { ...dui.expTeacher }
  if (ex[t.id]) delete ex[t.id]
  else ex[t.id] = true
  dui.expTeacher = ex
}

function teacherDrop(t) {
  if (dragTopicIds.value.length) {
    commitAssign(dragTopicIds.value.map((id) => ({ topicId: id, to: t.id })))
  }
  dragEnd()
}

/* ---------- resizer ---------- */

function startResize(e) {
  e.preventDefault()
  const sx = e.clientX
  const sw = dui.leftW
  const mv = (ev) => { dui.leftW = Math.max(400, Math.min(880, sw + (ev.clientX - sx))) }
  const up = () => {
    window.removeEventListener('mousemove', mv)
    window.removeEventListener('mouseup', up)
  }
  window.addEventListener('mousemove', mv)
  window.addEventListener('mouseup', up)
}

/* ---------- modals / shortcuts ---------- */

function openCreateDisc() {
  const firstGroup = store.state.groups[0]
  dui.cd = {
    name: '',
    group: firstGroup ? firstGroup.id : '',
    topics: [{ kind: 'lec', name: '', hours: 32 }],
    error: '',
  }
}
function openExport() {
  dui.exp = { step: 'config', period: store.state.period }
}

function onKey(e) {
  const tag = (e.target.tagName || '').toLowerCase()
  const inInput = tag === 'input' || tag === 'textarea'
  if (e.key === 'Escape') {
    if (dui.ov) dui.ov = false
    else if (dui.menu) dui.menu = null
    else if (dui.addTopic) dui.addTopic = null
    else if (dui.cd) dui.cd = null
    else if (dui.exp) dui.exp = null
    return
  }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
    e.preventDefault()
    if (e.shiftKey) store.planRedoAct()
    else store.planUndoAct()
    return
  }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'y') { e.preventDefault(); store.planRedoAct(); return }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'e') { e.preventDefault(); openExport(); return }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'n') { e.preventDefault(); openCreateDisc(); return }
  if (!inInput && e.key === '/') {
    e.preventDefault()
    if (searchEl.value) searchEl.value.focus()
  }
}

onMounted(() => document.addEventListener('keydown', onKey))
onUnmounted(() => document.removeEventListener('keydown', onKey))
</script>

<template>
  <div class="view">
    <!-- ======= header ======= -->
    <div class="head">
      <span class="head-title" title="Учебный план, учебный год 2026/27">Учебный план</span>
      <span class="sem-plaque" title="Семестр активного учебного года — переключается прямо здесь">
        <span class="plaque-lead mono">СЕМЕСТР</span>
        <button
          v-for="p in periodBtns"
          :key="p.k"
          class="plaque-btn"
          :class="{ on: store.state.period === p.k }"
          @click="pickSeason(p.k)"
        >{{ p.label }}</button>
      </span>
      <router-link class="year-chip" to="/settings" title="Даты семестров, сетка звонков — в настройках учебного года">
        <span class="plaque-lead mono">УЧ. ГОД</span>
        <span class="yc-year">2026/27</span>
        <span class="yc-act mono">настроить ↗</span>
      </router-link>
      <div class="progress">
        <span class="progress-label">Назначено тем {{ progress.don }} из {{ progress.tot }}</span>
        <div class="progress-track"><div class="progress-fill" :style="{ width: progressPct + '%' }"></div></div>
      </div>
      <div class="sp"></div>
      <button class="btn" title="Экспорт в Excel по государственному шаблону (Ctrl+E)" @click="openExport">Экспорт…</button>
      <div class="ov-wrap">
        <button
          class="btn ov-btn"
          :style="{ background: dui.ov ? '#F2F0EB' : '' }"
          title="Ещё: история действий"
          @click="dui.ov = !dui.ov"
        >⋯</button>
        <template v-if="dui.ov">
          <div class="ov-backdrop" @click="dui.ov = false"></div>
          <div class="ov-menu">
            <button
              class="ov-item"
              :style="{ color: canUndo ? '#1F1E1B' : '#C9C5BB' }"
              @click="dui.ov = false; store.planUndoAct()"
            >↶ Отменить<span class="ov-kbd mono">Ctrl+Z</span></button>
            <button
              class="ov-item"
              :style="{ color: canRedo ? '#1F1E1B' : '#C9C5BB' }"
              @click="dui.ov = false; store.planRedoAct()"
            >↷ Повторить<span class="ov-kbd mono">Ctrl+Shift+Z</span></button>
          </div>
        </template>
      </div>
    </div>

    <!-- ======= workspace ======= -->
    <div class="work">
      <!-- pool -->
      <div class="panel pool" :style="{ width: dui.leftW + 'px' }">
        <div class="pool-head">
          <div class="pool-title-row">
            <span class="pool-title">Дисциплины</span>
            <InfoDot tip="Дисциплина раскрывается в темы. Перетащите тему (или всю дисциплину) на преподавателя справа — или нажмите ＋ на строке." />
            <span class="sp"></span>
            <button class="btn-primary new-disc" title="Создать дисциплину (Ctrl+N)" @click="openCreateDisc">
              <span class="plus">＋</span>Дисциплина
            </button>
          </div>
          <input
            ref="searchEl"
            v-model="dui.search"
            class="input"
            placeholder="Поиск дисциплины, темы или группы…  ( / )"
            style="font-size: 12.5px"
          >
          <div class="filters">
            <div class="select-wrap" style="flex: 1.25; min-width: 0">
              <select v-model="dui.fStatus" :style="{ color: dui.fStatus !== 'all' ? '#1F1E1B' : '#5C574E', fontWeight: 500, fontSize: '12px' }">
                <option v-for="o in statusOpts" :key="o.v" :value="o.v">{{ o.label }}</option>
              </select>
              <span class="chev">▾</span>
            </div>
            <div class="select-wrap" style="flex: 1.1; min-width: 0">
              <select v-model="dui.fKind" :style="{ color: dui.fKind !== 'all' ? '#1F1E1B' : '#5C574E', fontWeight: 500, fontSize: '12px' }">
                <option v-for="o in kindOpts" :key="o.v" :value="o.v">{{ o.label }}</option>
              </select>
              <span class="chev">▾</span>
            </div>
            <div class="select-wrap" style="flex: 1; min-width: 0">
              <select v-model="dui.fCourse" :style="{ color: dui.fCourse !== 'all' ? '#1F1E1B' : '#5C574E', fontWeight: 500, fontSize: '12px' }">
                <option v-for="o in courseOpts" :key="o.v" :value="o.v">{{ o.label }}</option>
              </select>
              <span class="chev">▾</span>
            </div>
            <button class="link-btn" @click="toggleAll">{{ anyExpanded ? 'Свернуть все' : 'Развернуть все' }}</button>
          </div>
        </div>

        <div class="pool-list">
          <div v-for="grp in groupsList" :key="grp.label" class="group-block">
            <div class="group-head">
              <span class="group-name">{{ grp.label }}</span>
              <span class="group-meta mono">{{ grp.meta }}</span>
            </div>
            <div v-for="dv in grp.discs" :key="dv.d.id" class="disc" :class="{ dragging: dv.dragging }">
              <div
                class="disc-head"
                :title="dv.dragTitle"
                draggable="true"
                @click="toggleDisc(dv.d)"
                @dragstart="discDragStart(dv.d, $event)"
                @dragend="dragEnd"
              >
                <span class="chevron" title="Развернуть / свернуть темы">{{ dv.expanded ? '▾' : '▸' }}</span>
                <span class="disc-name" :title="dv.d.name">{{ dv.d.name }}</span>
                <span v-if="dv.d.isNew" class="new-tag mono">создана</span>
                <span class="disc-hours mono">{{ dv.hoursLabel }}</span>
                <span class="disc-badge" :style="{ color: dv.badgeColor, background: dv.badgeBg }">{{ dv.badge }}</span>
                <span
                  v-if="!dv.full"
                  class="plus-circle"
                  title="Назначить все незакрытые темы"
                  @click.stop="assignAll(dv.d, $event)"
                >＋</span>
                <span
                  class="disc-rm"
                  title="Удалить дисциплину из плана"
                  @click.stop="removeDisc(dv.d)"
                >×</span>
              </div>
              <div v-if="dv.expanded" class="topics">
                <div
                  v-for="tv in dv.topics"
                  :key="tv.tp.id"
                  class="topic-row"
                  :style="{ opacity: tv.dragging ? 0.4 : 1 }"
                  draggable="true"
                  @click="topicClick(dv.d, tv.tp, $event)"
                  @contextmenu.prevent="topicClick(dv.d, tv.tp, $event)"
                  @dragstart="topicDragStart(tv.tp, $event)"
                  @dragend="dragEnd"
                >
                  <span
                    class="kind-dot"
                    :style="{ borderRadius: tv.dotRadius, background: tv.dotColor }"
                    :title="tv.kindLabel"
                  ></span>
                  <span class="topic-name" :title="tv.tp.name">{{ tv.tp.name }}</span>
                  <span class="topic-kind" :style="{ color: tv.dotColor }">{{ tv.kindLabel }}</span>
                  <span class="topic-hours mono">{{ tv.hours }}</span>
                  <span
                    v-if="tv.t"
                    class="assignee"
                    :title="tv.aTitle"
                    @click.stop="unassign(tv.tp)"
                  >
                    <span
                      class="a-avatar"
                      :style="{ background: tv.aBg, color: tv.t.photo ? 'transparent' : '#FFFFFF' }"
                    >{{ tv.aInit }}</span>
                    <span class="a-name">{{ tv.t.name }}</span>
                  </span>
                  <span
                    v-else
                    class="plus-circle"
                    title="Назначить преподавателя"
                    @click.stop="topicPlus(dv.d, tv.tp, $event)"
                  >＋</span>
                  <span
                    class="topic-rm"
                    title="Удалить тему из плана"
                    @click.stop="removeTopic(dv.d, tv.tp)"
                  >×</span>
                </div>
                <div
                  class="add-topic"
                  title="Добавить тему или занятие в план"
                  @click.stop="dui.addTopic = { discId: dv.d.id, kind: 'lec', name: '', hours: 24 }"
                >
                  <span class="add-circle">＋</span>Добавить тему
                </div>
              </div>
            </div>
          </div>

          <div v-if="groupsList.length === 0" class="pool-empty">
            <span class="empty-circle">∅</span>
            <span>Ничего не найдено</span>
            <button class="btn" style="font-size: 12px; padding: 5px 12px" @click="resetFilters">
              Сбросить поиск и фильтры
            </button>
          </div>
        </div>
      </div>

      <!-- resizer -->
      <div class="resizer" title="Потяните, чтобы изменить ширину панелей" @mousedown="startResize">
        <span class="resizer-bar"></span>
      </div>

      <!-- teachers -->
      <div class="panel teachers">
        <div class="pool-head">
          <div class="pool-title-row">
            <span class="pool-title">Преподаватели</span>
            <InfoDot tip="Здесь — только назначение нагрузки. Состав преподавателей, фото и отпуска ведутся в разделе «Справочники» (левый рейл)." />
            <span class="sp"></span>
          </div>
          <input v-model="dui.tSearch" class="input" placeholder="Поиск преподавателя…" style="font-size: 12.5px">
        </div>
        <div class="t-list">
          <div v-for="tv in teachersList" :key="tv.t.id" class="t-block">
            <div
              class="t-row"
              :class="{ over: tv.over }"
              @click="toggleTeacher(tv.t)"
              @dragover.prevent="dui.dragOver = tv.t.id"
              @dragleave="dui.dragOver === tv.t.id && (dui.dragOver = null)"
              @drop.prevent="teacherDrop(tv.t)"
            >
              <span
                class="t-avatar"
                :style="{ background: tv.avatar, color: tv.avatarColor }"
              >{{ tv.init }}</span>
              <div class="t-name-wrap">
                <span class="t-name">{{ tv.t.name }}</span>
              </div>
              <span class="t-load">
                <span class="t-hours mono" :style="{ color: tv.hoursColor }">{{ tv.hoursLabel }}{{ tv.warnMark }}</span>
                <span class="t-bar"><span class="t-bar-fill" :style="{ width: tv.barPct, background: tv.barColor }"></span></span>
              </span>
              <span class="t-count">{{ tv.countLabel }}</span>
              <span class="t-chev">{{ tv.expanded ? '▴' : '▾' }}</span>
            </div>
            <div v-if="tv.expanded" class="t-assigns">
              <div v-for="(a, i) in tv.assigns" :key="i" class="t-assign">
                <span
                  class="kind-dot"
                  :style="{ borderRadius: dotRadius(a.tp.kind), background: kindColor(a.tp.kind) }"
                ></span>
                <span class="ta-label" :title="a.d.name + ', ' + a.tp.name + ' — ' + a.d.groupId">
                  {{ a.d.name }}, {{ a.tp.name }}
                </span>
                <span class="ta-hours mono">{{ a.tp.hours }} ч</span>
                <span class="ta-rm" title="Снять назначение" @click.stop="unassign(a.tp)">×</span>
              </div>
              <div v-if="tv.assigns.length === 0" class="t-empty">
                Нет назначений — перетащите тему или нажмите ＋ на теме
              </div>
            </div>
          </div>
          <div v-if="teachersList.length === 0" class="pool-empty" style="padding: 50px 20px">
            <span>Преподаватель не найден</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ======= overlays ======= -->
    <AssignMenu />
    <CreateDisciplineModal />
    <AddTopicModal />
    <CurriculumExportModal />
  </div>
</template>

<style scoped>
.view { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.sp { flex: 1; }

.head {
  flex: none;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 9px;
  padding: 9px 12px;
  background: var(--panel);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}
.head-title {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: -0.01em;
  min-width: 60px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.sem-plaque {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #F2F0EB;
  border-radius: 7px;
  padding: 2px 2px 2px 9px;
  flex: none;
}
.plaque-lead { font: 500 9px var(--mono); letter-spacing: 0.07em; color: var(--muted); }
.plaque-btn {
  border: none;
  border-radius: 5px;
  padding: 4px 11px;
  font: 500 12px var(--sans);
  color: var(--muted);
  background: transparent;
  cursor: pointer;
}
.plaque-btn.on { font-weight: 600; color: var(--fg); background: #FFF; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.14); }

.year-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #F2F0EB;
  border-radius: 7px;
  padding: 5px 10px;
  flex: none;
}
.year-chip:hover { background: #ECEAE4; text-decoration: none; }
.yc-year { font-size: 12px; font-weight: 600; color: var(--fg); }
.yc-act { font: 400 9.5px var(--mono); color: var(--faint); }

.progress { display: flex; flex-direction: column; gap: 3px; flex: none; min-width: 150px; }
.progress-label { font-size: 12px; font-weight: 600; white-space: nowrap; }
.progress-track { width: 100%; height: 3px; background: var(--active); border-radius: 2px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--fg); }

.ov-wrap { position: relative; flex: none; }
.ov-btn { font: 600 15px var(--sans); width: 31px; height: 31px; padding: 0; }
.ov-backdrop { position: fixed; inset: 0; z-index: 45; }
.ov-menu {
  position: absolute;
  right: 0;
  top: 37px;
  z-index: 46;
  width: 252px;
  background: var(--panel);
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 9px;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.14);
  padding: 4px;
  display: flex;
  flex-direction: column;
}
.ov-item {
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
  background: transparent;
  padding: 8px 10px;
  border-radius: var(--r-sm);
  cursor: pointer;
  font: 400 12.5px var(--sans);
  text-align: left;
  width: 100%;
}
.ov-item:hover { background: var(--chip); }
.ov-kbd { margin-left: auto; font: 400 10.5px var(--mono); color: var(--faint); }

.work { flex: 1; display: flex; min-height: 0; padding: 12px; gap: 0; }
.pool { flex: none; min-width: 0; }
.teachers { flex: 1; min-width: 0; }

.pool-head {
  flex: none;
  padding: 10px 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-bottom: 1px solid var(--line-soft);
}
.pool-title-row { display: flex; align-items: center; gap: 8px; }
.pool-title { font-size: 13px; font-weight: 600; }
.new-disc { display: inline-flex; align-items: center; gap: 5px; font-size: 12px; padding: 5px 11px; }
.plus { font-size: 13px; line-height: 1; }
.filters { display: flex; gap: 6px; align-items: center; }
.link-btn {
  flex: none;
  border: none;
  background: transparent;
  color: var(--blue);
  font: 500 12px var(--sans);
  padding: 3px 2px;
  border-radius: var(--r-sm);
  cursor: pointer;
}

.pool-list { flex: 1; overflow-y: auto; padding: 10px 12px; position: relative; }
.group-block { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.group-head {
  position: sticky;
  top: -10px;
  z-index: 2;
  background: var(--panel);
  padding: 6px 2px 4px;
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.group-name { font-size: 12px; font-weight: 600; color: #3A382F; }
.group-meta { font: 400 11px var(--mono); color: var(--faint); }

.disc {
  border: 1px solid rgba(0, 0, 0, 0.11);
  background: var(--panel);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  border-radius: var(--r-lg);
  overflow: hidden;
}
.disc.dragging { background: rgba(59, 98, 196, 0.04); }
.disc-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 11px 12px;
  cursor: pointer;
  outline: none;
}
.disc-head:hover { background: var(--hover); }
.chevron { flex: none; color: #7A756C; font-size: 13px; width: 18px; text-align: center; }
.disc-name {
  font-size: 13px;
  font-weight: 600;
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.new-tag {
  font: 500 9.5px var(--mono);
  color: var(--green);
  background: rgba(31, 138, 91, 0.10);
  padding: 1px 6px;
  border-radius: 4px;
  flex: none;
}
.disc-hours { font: 500 12px var(--mono); color: var(--sub); flex: none; }
.disc-badge {
  flex: none;
  font-size: 10.5px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  min-width: 34px;
  text-align: center;
}
.plus-circle {
  flex: none;
  width: 20px;
  height: 20px;
  border: 1.5px dashed rgba(0, 0, 0, 0.25);
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--muted);
  cursor: pointer;
}
.plus-circle:hover { border-color: var(--blue); color: var(--blue); }
.disc-rm { flex: none; color: var(--ghost); cursor: pointer; font-size: 17px; line-height: 1; padding: 0 2px; width: 16px; text-align: center; }
.disc-rm:hover { color: var(--orange-dark); }

.topics { border-top: 1px solid rgba(0, 0, 0, 0.06); background: #FCFBFA; padding: 4px 0; }
.topic-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px 6px 30px;
  cursor: grab;
  outline: none;
}
.topic-row:hover { background: var(--bg); }
.kind-dot { flex: none; width: 8px; height: 8px; }
.topic-name { font-size: 12.5px; flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.topic-kind { font-size: 10.5px; flex: none; }
.topic-hours { font: 500 11.5px var(--mono); color: var(--sub); flex: none; width: 38px; text-align: right; }
.assignee {
  flex: none;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: var(--chip);
  border-radius: 11px;
  padding: 1px 8px 1px 2px;
  cursor: pointer;
}
.assignee:hover { background: #FCE9DC; }
.a-avatar {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #B5B0A6;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 8.5px;
  font-weight: 600;
  background-size: cover !important;
  background-position: center !important;
}
.a-name {
  font-size: 10.5px;
  color: var(--sub);
  max-width: 74px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.topic-rm { flex: none; color: var(--ghost); cursor: pointer; font-size: 15px; line-height: 1; padding: 0 2px; width: 14px; text-align: center; }
.topic-rm:hover { color: var(--orange-dark); }
.add-topic {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px 6px 30px;
  cursor: pointer;
  color: var(--blue);
  font-size: 12px;
  font-weight: 500;
}
.add-topic:hover { background: var(--bg); }
.add-circle {
  width: 20px;
  height: 20px;
  border: 1.5px dashed rgba(59, 98, 196, 0.4);
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex: none;
}

.pool-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 60px 20px;
  color: var(--muted);
  font-size: 13px;
}
.empty-circle {
  width: 36px;
  height: 36px;
  border: 1.5px dashed rgba(0, 0, 0, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.resizer {
  flex: none;
  width: 12px;
  cursor: col-resize;
  display: flex;
  align-items: center;
  justify-content: center;
}
.resizer:hover { background: rgba(0, 0, 0, 0.03); }
.resizer-bar { width: 3px; height: 36px; border-radius: 2px; background: var(--line-strong); }

.t-list { flex: 1; overflow-y: auto; padding: 8px 10px; min-height: 0; }
.t-block { display: flex; flex-direction: column; }
.t-row {
  border: 1px solid var(--line);
  background: var(--panel);
  border-radius: var(--r-lg);
  padding: 6px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  margin-bottom: 5px;
}
.t-row:hover { background: var(--hover); border-color: rgba(0, 0, 0, 0.18); }
.t-row.over {
  background: rgba(59, 98, 196, 0.05);
  border-color: var(--blue);
  box-shadow: inset 0 0 0 1px var(--blue);
}
.t-avatar {
  flex: none;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
  pointer-events: none;
  background-size: cover !important;
  background-position: center !important;
}
.t-name-wrap { display: flex; flex-direction: column; gap: 1px; flex: 1; min-width: 0; pointer-events: none; }
.t-name { font-size: 13px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.t-load { display: flex; flex-direction: column; align-items: flex-end; gap: 3px; flex: none; pointer-events: none; }
.t-hours { font: 500 11.5px var(--mono); }
.t-bar { width: 64px; height: 3px; background: var(--active); border-radius: 2px; overflow: hidden; display: block; }
.t-bar-fill { display: block; height: 100%; }
.t-count {
  flex: none;
  font-size: 11px;
  color: var(--muted);
  background: var(--chip);
  padding: 2px 8px;
  border-radius: 10px;
  min-width: 14px;
  text-align: center;
  pointer-events: none;
}
.t-chev { flex: none; color: #7A756C; font-size: 13px; pointer-events: none; }

.t-assigns {
  margin: -2px 0 8px 14px;
  border-left: 2px solid var(--active);
  padding: 2px 0;
  display: flex;
  flex-direction: column;
}
.t-assign { display: flex; align-items: center; gap: 8px; padding: 4px 12px 4px 16px; font-size: 12.5px; }
.t-assign:hover { background: var(--hover); }
.t-assign .kind-dot { width: 7px; height: 7px; }
.ta-label { flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ta-hours { font: 400 11.5px var(--mono); color: var(--muted); flex: none; }
.ta-rm { color: var(--dim); cursor: pointer; font-size: 14px; flex: none; line-height: 1; }
.ta-rm:hover { color: var(--orange-dark); }
.t-empty { padding: 4px 12px 4px 16px; font-size: 12px; color: var(--dim); }
</style>
