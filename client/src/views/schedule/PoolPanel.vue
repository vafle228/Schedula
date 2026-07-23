<script setup>
import { computed, reactive, ref } from 'vue'
import { store } from '../../store/index.js'
import { kindOf } from '../../utils/kinds.js'
import InfoDot from '../../components/InfoDot.vue'
import { ui, visible, dateFor, openLf, dragPlaced, unplaceToPool, asgOptions } from './useSchedule.js'

const searchEl = ref(null)
defineExpose({ focusSearch: () => searchEl.value && searchEl.value.focus() })

/* Which blocks are expanded — keyed by discipline|kind, open by default. */
const collapsed = reactive({})
function toggle(key) { collapsed[key] = !collapsed[key] }

/* Inline «+ занятие» — creates a lesson silently in the block (Итерация 8):
   тема + учебный вопрос only, discipline / type / teacher come from the block.
   The card lands in the pool; drag it onto a slot to place it. */
const adding = ref(null) // block.key currently in add mode
const addForm = reactive({ topic: '', question: '' })

/* Topic / question suggestions reused from what's already authored. */
const topicBank = computed(() => [...new Set(store.enriched.value.map((l) => l.topic).filter(Boolean))])
const qBank = computed(() => [...new Set(store.enriched.value.map((l) => l.question).filter((q) => q && q !== '—'))])

function startAdd(b) {
  adding.value = b.key
  addForm.topic = ''
  addForm.question = ''
  if (collapsed[b.key]) collapsed[b.key] = false
}
function cancelAdd() { adding.value = null }

async function submitAdd(b) {
  const topic = addForm.topic.trim()
  if (!topic) return
  const asg = asgOptions.value.find((a) => a.discipline.id === b.disciplineId && a.groupId === b.groupId && a.teacherId === b.teacherId)
  if (!asg) return
  const unitTopic = asg.topics.find((tp) => tp.kind === b.addKind) || asg.topics[0]
  if (store.planRemaining(asg.groupId, unitTopic.id) <= 0) return // план исчерпан
  adding.value = null
  const created = await store.createManualLesson({
    topicId: unitTopic.id,
    disciplineId: asg.discipline.id,
    groupId: asg.groupId,
    teacherId: asg.teacherId,
    roomId: asg.defaultRoom,
    kind: b.addKind,
    period: store.state.period,
    week: null, day: null, slot: null,
    subBy: null, pin: false, ni: 1, nt: 1,
    topicLabel: topic,
    question: addForm.question.trim(),
  })
  if (created) ui.flashId = created.id
}

/** Entity lessons grouped course → block(kind) → lessons, with hour accounting. */
const tree = computed(() => {
  const byDisc = {}
  visible.value.forEach((l) => {
    const d = (byDisc[l.disc] = byDisc[l.disc] || { name: l.disc, t: l.t, room: l.room, lessons: [] })
    d.lessons.push(l)
  })
  return Object.values(byDisc).map((d) => {
    const t = store.teacherById(d.t)
    const byKind = {}
    d.lessons.forEach((l) => {
      const b = (byKind[l.kind] = byKind[l.kind] || { kind: l.kind, lessons: [] })
      b.lessons.push(l)
    })
    return {
      name: d.name,
      teacher: t ? t.name : '',
      room: d.room,
      blocks: Object.values(byKind).map((b) => {
        const K = kindOf(b.kind)
        const h = K.acHours
        const authored = b.lessons.length
        const placed = b.lessons.filter((l) => l.d != null).length
        const first = b.lessons[0]
        // The plan cap comes from the topic's hours (one topic per disc + kind).
        // A missing topic (orphaned lesson) has no plan — show what's authored.
        const topicId = first ? first.topicId : null
        const plan = topicId != null ? store.topicPlanCount(topicId) : 0
        const planN = plan || Math.max(authored, 1)
        const full = authored >= planN
        const key = d.name + '|' + b.kind
        const groups = [...new Set(b.lessons.map((l) => l.g))].join(' + ')
        return {
          key,
          name: K.label,
          dot: K.dot,
          color: K.dark,
          groupsLabel: groups + ' · ' + h + ' ак.ч',
          counts: authored + ' / ' + planN + ' зан.',
          open: !collapsed[key],
          disciplineId: first ? first.disciplineId : null,
          groupId: first ? first.groupId : null,
          teacherId: first ? first.t : null,
          full,
          ctx: d.name + ' · ' + K.label + ' · ' + (t ? t.name : ''),
          placedH: placed * h + 'ч',
          authoredH: authored * h + 'ч',
          planH: planN * h + 'ч',
          placedBar: `width:${Math.min(100, planN ? placed / planN * 100 : 0)}%;background:#1F8A5B`,
          pooledBar: `width:${Math.min(100 - (planN ? placed / planN * 100 : 0), planN ? (authored - placed) / planN * 100 : 0)}%;background:#B07C1F`,
          addKind: b.kind,
          lessons: b.lessons
            .slice()
            .sort((a, c) => (a.ni || 0) - (c.ni || 0))
            .map((l, i) => {
              const placedHere = l.d != null
              return {
                l,
                no: 'Занятие ' + (i + 1),
                topic: l.topic || 'тема не указана',
                question: l.question && l.question !== '—' ? l.question : '',
                placed: placedHere,
                sub: !!l.subBy,
                dot: placedHere ? 'placed' : 'pool',
              }
            }),
        }
      }),
    }
  })
})

function dayLabel(l) {
  const dayNames = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
  return 'Н' + l.w + ' ' + dayNames[l.d] + ' ' + dateFor(l.w, l.d)
}

const placedH = computed(() => {
  let placed = 0
  let authored = 0
  visible.value.forEach((l) => {
    const h = kindOf(l.kind).acHours
    authored += h
    if (l.d != null) placed += h
  })
  return { placed, authored, pct: authored ? Math.round(placed / authored * 100) : 0 }
})

function onDragStart(l, e) {
  e.dataTransfer.effectAllowed = 'move'
  ui.dragId = l.id
}

/* return-to-pool drop target — only for a placed lesson */
function onPoolDragOver(e) {
  if (!dragPlaced.value) return
  e.preventDefault()
  e.dataTransfer.dropEffect = 'move'
  if (!ui.poolOver) ui.poolOver = true
}
function onPoolDragLeave(e) {
  if (e.currentTarget.contains(e.relatedTarget)) return
  ui.poolOver = false
}
function onPoolDrop(e) {
  if (!dragPlaced.value) return
  e.preventDefault()
  unplaceToPool(ui.dragId)
}
</script>

<template>
  <div
    ref="searchEl"
    class="panel pool"
    tabindex="-1"
    @dragover="onPoolDragOver"
    @dragleave="onPoolDragLeave"
    @drop="onPoolDrop"
  >
    <div class="pool-head">
      <span class="pool-title">Содержание курсов</span>
      <InfoDot tip="Занятия выбранной группы, преподавателя или аудитории. Перетащите занятие из пула на свободный слот сетки — оно займёт слот целиком. Чтобы снять с сетки, тащите обратно сюда." />
      <span class="sp"></span>
      <span class="pool-lead mono">учёт часов</span>
    </div>
    <div class="pool-summary" title="Итог по выбранной сущности">
      <div class="ps-row">
        <span>разложено · заведено</span>
        <span class="mono">{{ placedH.placed }} / {{ placedH.authored }} ч</span>
      </div>
      <div class="ps-bar">
        <div class="ps-fill" :style="{ width: placedH.pct + '%' }"></div>
      </div>
    </div>

    <div class="pool-list">
      <div v-if="dragPlaced" class="drop-zone" :class="{ over: ui.poolOver }">
        <span class="dz-ico">↩</span> Отпустите, чтобы снять с сетки и вернуть в пул
      </div>

      <div v-for="c in tree" :key="c.name" class="course">
        <div class="course-head">
          <span class="course-name">{{ c.name }}</span>
          <span class="course-teacher mono">{{ c.teacher }}</span>
          <span class="course-room mono" title="аудитория курса по умолчанию">ауд. {{ c.room }}</span>
        </div>
        <div v-for="b in c.blocks" :key="b.key" class="block">
          <div class="block-head" @click="toggle(b.key)">
            <span class="caret">{{ b.open ? '▾' : '▸' }}</span>
            <span class="block-dot" :style="{ background: b.dot }"></span>
            <span class="block-name" :style="{ color: b.color }">{{ b.name }}</span>
            <span class="block-groups mono">{{ b.groupsLabel }}</span>
            <span class="sp"></span>
            <span class="block-counts mono">{{ b.counts }}</span>
          </div>
          <div class="block-bar">
            <div :style="b.placedBar"></div>
            <div :style="b.pooledBar"></div>
          </div>
          <div class="block-legend mono">
            <span><span class="lg-g">▬</span> разлож. {{ b.placedH }}</span>
            <span><span class="lg-a">▬</span> заведено {{ b.authoredH }}</span>
            <span>план {{ b.planH }}</span>
          </div>
          <template v-if="b.open">
            <div class="lessons">
              <div
                v-for="ls in b.lessons"
                :key="ls.l.id"
                class="lesson"
                :class="{ placed: ls.placed }"
                :title="ls.placed ? 'разложено: ' + dayLabel(ls.l) + ' — перетащите, чтобы перенести' : 'перетащите на свободный слот сетки'"
                draggable="true"
                @dragstart="onDragStart(ls.l, $event)"
                @dragend="ui.dragId = null"
                @click="openLf(null, ls.l.id)"
              >
                <div class="lesson-top">
                  <span class="lesson-no mono">{{ ls.no }}</span>
                  <span class="lesson-topic">{{ ls.topic }}</span>
                  <span v-if="ls.sub" class="lesson-tag sub">замена</span>
                  <span v-else-if="ls.placed" class="lesson-tag placed-tag">✓ в сетке</span>
                  <span v-else class="lesson-tag">в пуле</span>
                </div>
                <div v-if="ls.question" class="lesson-q">{{ ls.question }}</div>
              </div>
              <div v-if="adding === b.key" class="add-form">
                <div class="add-ctx mono">{{ b.ctx }} <span class="add-ctx-tag">← контекст</span></div>
                <div class="add-fld">
                  <span class="add-label">Тема</span>
                  <input
                    v-model="addForm.topic"
                    class="input input--white"
                    list="pool-topic-bank"
                    placeholder="начните вводить…"
                    @keydown.enter="submitAdd(b)"
                    @keydown.esc="cancelAdd"
                  >
                </div>
                <div class="add-fld">
                  <span class="add-label">Учебный вопрос</span>
                  <input
                    v-model="addForm.question"
                    class="input input--white"
                    list="pool-q-bank"
                    placeholder="один вопрос на урок…"
                    @keydown.enter="submitAdd(b)"
                    @keydown.esc="cancelAdd"
                  >
                </div>
                <div class="add-btns">
                  <button class="add-submit" :disabled="!addForm.topic.trim()" @click="submitAdd(b)">Добавить</button>
                  <button class="add-cancel" @click="cancelAdd">Отмена</button>
                </div>
              </div>
              <button v-else-if="!b.full" class="add-lesson" @click="startAdd(b)">+ занятие</button>
              <div v-else class="plan-full mono" title="Заведено занятий на все запланированные часы этой темы">
                план исчерпан · {{ b.planH }}
              </div>
            </div>
          </template>
        </div>
      </div>

      <div v-if="tree.length === 0" class="pool-empty">
        <span class="ok-badge">∅</span>
        <span class="pe-title">Нет занятий</span>
        <span class="pe-sub">У выбранной группы, преподавателя или аудитории нет заведённых занятий на этот период.</span>
      </div>
    </div>
    <datalist id="pool-topic-bank"><option v-for="t in topicBank" :key="t" :value="t"></option></datalist>
    <datalist id="pool-q-bank"><option v-for="q in qBank" :key="q" :value="q"></option></datalist>
  </div>
</template>

<style scoped>
.pool { order: 1; flex: none; width: 340px; outline: none; }
.pool-head { flex: none; display: flex; align-items: center; gap: 7px; padding: 10px 12px 8px; border-bottom: 1px solid var(--line-soft); }
.pool-title { font-size: 13.5px; font-weight: 600; }
.pool-lead { font: 500 10px var(--mono); color: var(--muted); }
.sp { flex: 1; }

.pool-summary { flex: none; padding: 8px 12px 9px; border-bottom: 1px solid var(--line-soft); background: #FBFAF8; display: flex; flex-direction: column; gap: 4px; }
.ps-row { display: flex; justify-content: space-between; gap: 10px; font: 500 10px var(--mono); color: var(--sub); }
.ps-bar { height: 5px; background: #ECEAE4; border-radius: 3px; overflow: hidden; }
.ps-fill { height: 100%; background: #1F8A5B; }

.pool-list { flex: 1; overflow-y: auto; padding: 10px; display: flex; flex-direction: column; gap: 8px; }

.drop-zone {
  flex: none;
  display: flex;
  align-items: center;
  gap: 7px;
  justify-content: center;
  text-align: center;
  border: 1.5px dashed rgba(31, 138, 91, 0.5);
  background: rgba(31, 138, 91, 0.05);
  color: #166A45;
  border-radius: 8px;
  padding: 11px 10px;
  font-size: 11.5px;
  font-weight: 600;
}
.drop-zone.over { border-color: #1F8A5B; background: rgba(31, 138, 91, 0.14); }
.dz-ico { font-size: 14px; line-height: 1; }

.course { flex: none; border: 1px solid rgba(0, 0, 0, 0.1); border-radius: 9px; overflow: hidden; background: #FFF; }
.course-head { padding: 9px 11px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid var(--line-soft); }
.course-name { font-size: 13px; font-weight: 600; flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.course-teacher { font: 500 10px var(--mono); color: var(--muted); }
.course-room { font: 500 9px var(--mono); color: var(--faint); background: var(--chip); border-radius: 4px; padding: 2px 6px; }

.block { padding: 9px 11px; border-bottom: 1px solid rgba(0, 0, 0, 0.05); }
.block:last-child { border-bottom: none; }
.block-head { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.caret { color: var(--faint); font-size: 10px; width: 9px; }
.block-dot { width: 9px; height: 9px; border-radius: 50%; flex: none; }
.block-name { font-size: 12.5px; font-weight: 600; }
.block-groups { font: 500 9px var(--mono); color: var(--faint); }
.block-counts { font: 500 10px var(--mono); color: var(--muted); }
.block-bar { margin: 7px 0 0 17px; display: flex; height: 6px; border-radius: 3px; overflow: hidden; background: #ECEAE4; }
.block-legend { margin: 4px 0 0 17px; display: flex; gap: 11px; font: 500 9.5px var(--mono); color: var(--muted); }
.lg-g { color: #166A45; }
.lg-a { color: #B07C1F; }

.lessons { margin: 9px 0 2px 17px; display: flex; flex-direction: column; gap: 5px; }
.lesson { border: 1px solid rgba(0, 0, 0, 0.09); border-radius: 6px; padding: 6px 8px; background: #FBFAF8; cursor: grab; display: flex; flex-direction: column; gap: 3px; }
.lesson.placed { background: #FFF; }
.lesson-top { display: flex; align-items: center; gap: 6px; }
.lesson-no { font: 400 9.5px var(--mono); color: var(--faint); }
.lesson-topic { font-size: 11.5px; font-weight: 600; color: #2A4B9E; flex: 1; min-width: 0; line-height: 1.25; }
.lesson-tag { font: 500 8.5px var(--mono); color: #8A6A28; background: rgba(176, 124, 31, 0.14); border-radius: 3px; padding: 1px 5px; }
.lesson-tag.sub { color: #8A6A28; }
.lesson-tag.placed-tag { color: #166A45; background: rgba(31, 138, 91, 0.12); }
.lesson-q { padding-left: 14px; font-size: 10px; color: #5C574E; }
.add-lesson { text-align: left; background: transparent; border: 1px dashed rgba(0, 0, 0, 0.2); border-radius: 6px; padding: 6px 10px; font-size: 11.5px; color: var(--blue); cursor: pointer; }
.plan-full { text-align: center; border: 1px dashed rgba(31, 138, 91, 0.4); border-radius: 6px; padding: 6px 10px; font: 500 10px var(--mono); color: #166A45; background: rgba(31, 138, 91, 0.05); }

.add-form {
  border: 1.5px solid rgba(31, 138, 91, 0.45);
  border-radius: 7px;
  padding: 9px 10px;
  background: #FFF;
  display: flex;
  flex-direction: column;
  gap: 7px;
}
.add-ctx { font-size: 10px; color: var(--sub); background: var(--active); border-radius: 5px; padding: 5px 8px; }
.add-ctx-tag { color: var(--faint); }
.add-fld { display: flex; flex-direction: column; gap: 3px; }
.add-label { font-size: 10.5px; color: var(--muted); }
.add-fld .input { font-size: 12px; padding: 7px 9px; }
.add-btns { display: flex; gap: 6px; margin-top: 1px; }
.add-submit {
  flex: 1;
  background: var(--fg);
  color: #FFF;
  border: none;
  border-radius: 6px;
  padding: 7px 0;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.add-submit:disabled { background: #C9C4BA; cursor: not-allowed; }
.add-cancel {
  background: #FFF;
  border: 1px solid rgba(0, 0, 0, 0.16);
  border-radius: 6px;
  padding: 7px 12px;
  font-size: 12px;
  color: var(--sub);
  cursor: pointer;
}

.pool-empty { display: flex; flex-direction: column; align-items: center; gap: 9px; padding: 48px 16px; color: var(--muted); text-align: center; }
.ok-badge { width: 38px; height: 38px; border-radius: 50%; background: var(--chip); display: flex; align-items: center; justify-content: center; font-size: 16px; }
.pe-title { font-size: 13px; font-weight: 600; }
.pe-sub { font-size: 11.5px; color: var(--muted); line-height: 1.5; }
</style>
