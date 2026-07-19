<script setup>
import { reactive, computed, onMounted, onUnmounted } from 'vue'
import { store } from '../../store/index.js'
import { initials, avatarBg, plural } from '../../utils/format.js'
import RoomsEditor from '../../components/RoomsEditor.vue'
import AvailabilityEditor from '../../components/AvailabilityEditor.vue'
import AbsenceEditor from '../../components/AbsenceEditor.vue'
import AddTeacherModal from './AddTeacherModal.vue'
import AddMajorModal from './AddMajorModal.vue'

const ui = reactive({
  sec: 'majors', // majors | teachers | rooms
  mid: 'm1',
  mq: '',
  gf: { name: '', course: '1', err: '' },
  tid: 't1',
  q: '',
  addTeacher: false,
  addMajor: false,
})

const secBtns = computed(() => [
  { k: 'majors', label: 'Специальности · ' + store.state.majors.length },
  { k: 'teachers', label: 'Преподаватели · ' + store.state.teachers.length },
  { k: 'rooms', label: 'Аудитории · ' + store.state.rooms.length },
])

/* ================= majors ================= */

const groupsOf = (mid) => store.state.groups.filter((g) => g.majorId === mid)

const groupUsage = computed(() => {
  const m = {}
  store.state.disciplines.forEach((d) => { m[d.groupId] = (m[d.groupId] || 0) + 1 })
  return m
})

const mShown = computed(() => {
  const q = ui.mq.trim().toLowerCase()
  return store.state.majors.filter((m) => !q
    || m.name.toLowerCase().includes(q)
    || m.code.toLowerCase().includes(q)
    || groupsOf(m.id).some((g) => g.id.toLowerCase().includes(q)))
})

const mList = computed(() => mShown.value.map((m) => {
  const n = groupsOf(m.id).length
  return {
    m,
    cnt: n ? n + ' ' + plural(n, 'группа', 'группы', 'групп') : 'нет групп',
    hasGroups: n > 0,
    on: m.id === ui.mid,
  }
}))

const curM = computed(() => store.state.majors.find((m) => m.id === ui.mid) || store.state.majors[0] || null)
const curMGroups = computed(() => (curM.value ? groupsOf(curM.value.id) : []))

const grpRows = computed(() => curMGroups.value.map((g) => {
  const used = groupUsage.value[g.id] || 0
  const hasLessons = store.state.lessons.some((l) => l.groupId === g.id)
  const locked = used > 0 || hasLessons
  return {
    g, used, locked,
    usage: used ? used + ' ' + plural(used, 'дисциплина', 'дисциплины', 'дисциплин') : 'не используется',
    delTip: locked ? 'Нельзя удалить: у группы есть дисциплины в плане' : 'Удалить группу',
  }
}))

const courseOpts = [1, 2, 3, 4].map((c) => ({ v: String(c), label: c + ' курс' }))

async function addGroup() {
  const name = ui.gf.name.trim()
  if (!name) { ui.gf.err = 'Укажите название группы'; return }
  const clash = store.state.groups.find((g) => g.id.toLowerCase() === name.toLowerCase())
  if (clash) {
    const m = store.state.majors.find((x) => x.id === clash.majorId)
    ui.gf.err = 'Группа «' + name + '» уже есть' + (m ? ' (' + m.code + ')' : '')
    return
  }
  await store.createGroup(curM.value.id, { name, course: parseInt(ui.gf.course, 10) })
  ui.gf.name = ''
  ui.gf.err = ''
}

const majCanDel = computed(() => !!curM.value && curMGroups.value.length === 0)
async function delMajor() {
  if (!majCanDel.value) return
  await store.deleteMajor(curM.value.id)
  ui.mid = store.state.majors[0] ? store.state.majors[0].id : null
}

/* ================= teachers ================= */

const tShown = computed(() => {
  const q = ui.q.trim().toLowerCase()
  return store.state.teachers.filter((t) => !q || t.name.toLowerCase().includes(q))
})

const tList = computed(() => tShown.value.map((t) => {
  const abs = (t.absences || []).length
  const meta = []
  if (t.c) meta.push('еженедельно')
  if (abs) meta.push('отсутствий ' + abs)
  return {
    t,
    init: t.photo ? '' : initials(t.name),
    bg: avatarBg(t.photo),
    meta: meta.length ? meta.join(' · ') : 'без отметок',
    status: t.c ? 'заданы' : 'не заданы',
    on: t.id === ui.tid,
  }
}))

const curT = computed(() => store.teacherById(ui.tid) || store.state.teachers[0] || null)
const curAbs = computed(() => (curT.value ? curT.value.absences || [] : []))

function uploadPhoto(e) {
  const f = e.target.files && e.target.files[0]
  if (!f || !curT.value) return
  const r = new FileReader()
  r.onload = () => store.setTeacherPhoto(curT.value.id, r.result)
  r.readAsDataURL(f)
}

/* ================= shared ================= */

function onKey(e) {
  if (e.key === 'Escape') {
    ui.addTeacher = false
    ui.addMajor = false
  }
}
onMounted(() => document.addEventListener('keydown', onKey))
onUnmounted(() => document.removeEventListener('keydown', onKey))
</script>

<template>
  <div class="view">
    <!-- ======= header ======= -->
    <div class="head">
      <span class="head-title">Справочники</span>
      <div class="seg">
        <button
          v-for="s in secBtns"
          :key="s.k"
          :class="{ on: ui.sec === s.k }"
          style="padding: 5px 14px; font-size: 12.5px"
          @click="ui.sec = s.k"
        >{{ s.label }}</button>
      </div>
      <div class="sp"></div>
      <span class="head-note mono">мастер-данные · меняются нечасто</span>
    </div>

    <!-- ======= MAJORS ======= -->
    <div v-if="ui.sec === 'majors'" class="work">
      <div class="panel side">
        <div class="side-head">
          <div class="side-title-row">
            <span class="side-title">Специальности</span>
            <button class="btn add-btn" title="Добавить специальность" @click="ui.addMajor = true">
              <span class="plus">＋</span>Добавить
            </button>
          </div>
          <input v-model="ui.mq" class="input" placeholder="Поиск: код, название, группа…" style="font-size: 12.5px">
        </div>
        <div class="side-list">
          <div
            v-for="row in mList"
            :key="row.m.id"
            class="m-row"
            :class="{ on: row.on }"
            @click="ui.mid = row.m.id; ui.gf = { name: '', course: '1', err: '' }"
          >
            <div class="m-top">
              <span class="m-code mono">{{ row.m.code }}</span>
              <span class="sp"></span>
              <span class="m-cnt mono" :class="{ warn: !row.hasGroups }">{{ row.cnt }}</span>
            </div>
            <span class="m-name" :style="{ fontWeight: row.on ? 600 : 400 }">{{ row.m.name }}</span>
          </div>
          <div v-if="mList.length === 0" class="side-empty">Не найдено</div>
        </div>
      </div>

      <div v-if="curM" class="panel card">
        <div class="card-head">
          <div class="card-head-main">
            <span class="card-name">{{ curM.name }}</span>
            <div class="chips">
              <span class="chip-tag mono">код: {{ curM.code }}</span>
              <span class="chip-tag mono" :class="curMGroups.length ? 'ok' : 'warn'">
                групп: {{ curMGroups.length || 'нет' }}
              </span>
            </div>
          </div>
        </div>
        <div class="card-body">
          <div class="sect narrow">
            <div class="micro">РЕКВИЗИТЫ</div>
            <div class="req-row">
              <div class="fld" style="flex: none; width: 130px">
                <span class="field-label">КОД</span>
                <input
                  class="input mono"
                  style="font-weight: 500; font-size: 12.5px"
                  :value="curM.code"
                  placeholder="09.02.07"
                  @change="store.patchMajor(curM.id, { code: $event.target.value })"
                >
              </div>
              <div class="fld" style="flex: 1; min-width: 0">
                <span class="field-label">НАЗВАНИЕ</span>
                <input
                  class="input"
                  style="font-size: 12.5px"
                  :value="curM.name"
                  placeholder="Название специальности"
                  @change="store.patchMajor(curM.id, { name: $event.target.value })"
                >
              </div>
            </div>
          </div>

          <div class="sect narrow bordered">
            <div class="sect-head-row">
              <span class="micro">ГРУППЫ СПЕЦИАЛЬНОСТИ</span>
              <span class="sect-note">создаются здесь — сразу видны в «Распределении» и «Расписании»</span>
            </div>
            <div class="gf-row">
              <input
                v-model="ui.gf.name"
                class="input"
                style="flex: none; width: 170px; font-size: 12.5px"
                placeholder="Название, напр. ИС-27"
                @input="ui.gf.err = ''"
                @keydown.enter="addGroup"
              >
              <div class="select-wrap" style="flex: none; width: 110px">
                <select v-model="ui.gf.course">
                  <option v-for="o in courseOpts" :key="o.v" :value="o.v">{{ o.label }}</option>
                </select>
                <span class="chev">▾</span>
              </div>
              <button class="btn-primary" @click="addGroup">＋ Добавить группу</button>
            </div>
            <div v-if="ui.gf.err" class="form-err"><span>⚠</span><span>{{ ui.gf.err }}</span></div>
            <div class="grp-table">
              <div class="grp-thead mono">
                <span>ГРУППА</span><span>КУРС</span><span>ИСПОЛЬЗОВАНИЕ</span><span></span>
              </div>
              <div v-for="row in grpRows" :key="row.g.id" class="grp-row">
                <span class="grp-name">{{ row.g.id }}</span>
                <div class="select-wrap">
                  <select
                    :value="String(row.g.course)"
                    style="padding: 5px 24px 5px 9px; font-size: 12px; border-radius: 6px"
                    @change="store.patchGroup(row.g.id, { course: parseInt($event.target.value, 10) })"
                  >
                    <option v-for="o in courseOpts" :key="o.v" :value="o.v">{{ o.label }}</option>
                  </select>
                  <span class="chev">▾</span>
                </div>
                <span class="grp-usage" :class="{ free: !row.used }">{{ row.usage }}</span>
                <button
                  class="grp-del"
                  :class="{ off: row.locked }"
                  :title="row.delTip"
                  @click="!row.locked && store.deleteGroup(row.g.id)"
                >✕</button>
              </div>
              <div v-if="grpRows.length === 0" class="grp-empty">
                Групп пока нет — добавьте первую в форме выше.
              </div>
            </div>
          </div>

          <div class="card-foot narrow">
            <span class="foot-note">
              Группа удаляется, только если на ней нет дисциплин. Специальность — только без групп.
              Селекты групп в пуле и расписании читают этот справочник.
            </span>
            <span
              class="maj-del"
              :class="{ off: !majCanDel }"
              :title="majCanDel ? 'Удалить специальность' : 'Нельзя удалить: сначала удалите или переведите группы'"
              @click="delMajor"
            >Удалить специальность</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ======= TEACHERS ======= -->
    <div v-else-if="ui.sec === 'teachers'" class="work">
      <div class="panel side">
        <div class="side-head">
          <div class="side-title-row">
            <span class="side-title">Преподаватели</span>
            <button class="btn add-btn" title="Добавить преподавателя" @click="ui.addTeacher = true">
              <span class="plus">＋</span>Добавить
            </button>
          </div>
          <input v-model="ui.q" class="input" placeholder="Поиск преподавателя…" style="font-size: 12.5px">
        </div>
        <div class="side-list">
          <div
            v-for="row in tList"
            :key="row.t.id"
            class="t-row"
            :class="{ on: row.on }"
            @click="ui.tid = row.t.id"
          >
            <span class="t-avatar" :style="{ background: row.bg }">{{ row.init }}</span>
            <div class="t-info">
              <span class="t-name" :style="{ fontWeight: row.on ? 600 : 400 }">{{ row.t.name }}</span>
              <span class="t-meta">{{ row.meta }}</span>
            </div>
            <span class="t-status mono" :class="row.t.c ? 'ok' : 'warn'">{{ row.status }}</span>
          </div>
          <div v-if="tList.length === 0" class="side-empty">Не найдено</div>
        </div>
      </div>

      <div v-if="curT" class="panel card">
        <div class="card-head">
          <label
            class="photo"
            :style="{ background: avatarBg(curT.photo) }"
            title="Нажмите, чтобы загрузить или заменить фото"
          >
            {{ curT.photo ? '' : initials(curT.name) }}
            <input type="file" accept="image/*" style="display: none" @change="uploadPhoto">
          </label>
          <div class="card-head-main">
            <span class="card-name">{{ curT.name }}</span>
            <div class="chips">
              <span class="chip-tag mono" :class="curT.c ? 'ok' : 'warn'">
                еженедельно: {{ curT.c ? 'заданы' : 'не заданы' }}
              </span>
              <span class="chip-tag mono" :class="curAbs.length ? 'orange' : ''">
                отсутствий: {{ curAbs.length || 'нет' }}
              </span>
            </div>
          </div>
          <div class="photo-actions">
            <label class="photo-link">
              {{ curT.photo ? 'Заменить фото' : 'Загрузить фото' }}
              <input type="file" accept="image/*" style="display: none" @change="uploadPhoto">
            </label>
            <span
              v-if="curT.photo"
              class="photo-clear"
              @click="store.setTeacherPhoto(curT.id, null)"
            >Убрать</span>
          </div>
        </div>
        <div class="card-body">
          <div class="sect">
            <div class="micro">ЕЖЕНЕДЕЛЬНАЯ ДОСТУПНОСТЬ · клик циклит: свободно → недоступно → нежелательно</div>
            <AvailabilityEditor :teacher="curT" />
          </div>
          <div class="sect narrow bordered">
            <div class="sect-head-row">
              <span class="micro">ПЕРИОДЫ ОТСУТСТВИЯ</span>
              <span class="sect-note">отпуск, больничный, командировка — все блокируют даты в расписании</span>
            </div>
            <AbsenceEditor :teacher="curT" />
          </div>
          <div class="foot-hint narrow">
            Жёсткие ограничения генератор не нарушает; нежелательные слоты постарается избежать.
            Периоды отсутствия исключают эти даты из расписания.
            Изменения сразу учитываются в проверке конфликтов «Расписания».
          </div>
        </div>
      </div>
    </div>

    <!-- ======= ROOMS ======= -->
    <div v-else class="work">
      <div class="panel rooms-panel">
        <RoomsEditor />
      </div>
    </div>

    <!-- ======= modals ======= -->
    <AddTeacherModal
      v-if="ui.addTeacher"
      @close="ui.addTeacher = false"
      @created="(t) => { ui.addTeacher = false; ui.tid = t.id; ui.sec = 'teachers' }"
    />
    <AddMajorModal
      v-if="ui.addMajor"
      @close="ui.addMajor = false"
      @created="(m) => { ui.addMajor = false; ui.mid = m.id }"
    />
  </div>
</template>

<style scoped>
.view { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.sp { flex: 1; }

.head {
  flex: none;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 16px;
  background: var(--panel);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}
.head-title { font-size: 15px; font-weight: 600; letter-spacing: -0.01em; flex: none; }
.head-note { font: 400 11px var(--mono); color: var(--faint); }

.work { flex: 1; display: flex; min-height: 0; padding: 12px; gap: 12px; }

.side { flex: none; width: 290px; }
.side-head {
  flex: none;
  padding: 10px 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-bottom: 1px solid var(--line-soft);
}
.side-title-row { display: flex; align-items: center; gap: 8px; }
.side-title { font-size: 13px; font-weight: 600; flex: 1; }
.add-btn { display: inline-flex; align-items: center; gap: 5px; font-size: 12px; padding: 5px 11px; }
.plus { font-size: 13px; line-height: 1; }
.side-list { flex: 1; overflow-y: auto; padding: 6px; }
.side-empty { padding: 40px 16px; text-align: center; font-size: 12.5px; color: var(--muted); }

.m-row { display: flex; flex-direction: column; gap: 3px; padding: 8px 9px; border-radius: var(--r-md); cursor: pointer; }
.m-row:hover { background: var(--chip); }
.m-row.on { background: var(--active); }
.m-top { display: flex; align-items: center; gap: 8px; }
.m-code { font: 500 10px var(--mono); color: var(--muted); }
.m-cnt { font: 500 9.5px var(--mono); color: var(--sub); background: var(--chip); border-radius: 4px; padding: 1px 6px; }
.m-cnt.warn { color: var(--amber); background: rgba(176, 124, 31, 0.08); }
.m-name { font-size: 12.5px; line-height: 1.35; }

.t-row { display: flex; align-items: center; gap: 9px; padding: 7px 9px; border-radius: var(--r-md); cursor: pointer; }
.t-row:hover { background: var(--chip); }
.t-row.on { background: var(--active); }
.t-avatar {
  flex: none;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  color: var(--sub);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 9.5px;
  font-weight: 600;
  background-size: cover !important;
  background-position: center !important;
}
.t-info { display: flex; flex-direction: column; gap: 1px; flex: 1; min-width: 0; }
.t-name { font-size: 12.5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.t-meta { font-size: 10px; color: var(--faint); }
.t-status { flex: none; font: 500 9.5px var(--mono); border-radius: 4px; padding: 1px 6px; }
.t-status.ok { color: var(--green); background: rgba(31, 138, 91, 0.08); }
.t-status.warn { color: var(--amber); background: rgba(176, 124, 31, 0.08); }

.card { flex: 1; min-width: 0; }
.card-head {
  flex: none;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--line-soft);
}
.card-head-main { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 0; }
.card-name { font-size: 16px; font-weight: 600; }
.chips { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.chip-tag { font: 500 10px var(--mono); color: var(--sub); background: var(--chip); border-radius: 4px; padding: 2px 7px; }
.chip-tag.ok { color: var(--green); background: rgba(31, 138, 91, 0.08); }
.chip-tag.warn { color: var(--amber); background: rgba(176, 124, 31, 0.08); }
.chip-tag.orange { color: var(--orange-dark); background: rgba(217, 119, 6, 0.08); }

.photo {
  flex: none;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  color: var(--sub);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background-size: cover !important;
  background-position: center !important;
}
.photo-actions { display: flex; flex-direction: column; gap: 3px; align-items: flex-end; flex: none; }
.photo-link { font-size: 11.5px; color: var(--blue); cursor: pointer; }
.photo-clear { font-size: 11.5px; color: var(--muted); cursor: pointer; }

.card-body { flex: 1; overflow-y: auto; padding: 18px; display: flex; flex-direction: column; gap: 22px; }
.sect { display: flex; flex-direction: column; gap: 12px; }
.sect .micro { margin-bottom: -4px; }
.narrow { max-width: 560px; }
.bordered { border-top: 1px solid rgba(0, 0, 0, 0.08); padding-top: 18px; }
.sect-head-row { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
.sect-note { font-size: 11px; color: var(--faint); }

.req-row { display: flex; gap: 8px; }
.fld { display: flex; flex-direction: column; gap: 5px; }

.gf-row { display: flex; gap: 8px; align-items: center; }

.grp-table { display: flex; flex-direction: column; }
.grp-thead, .grp-row {
  display: grid;
  grid-template-columns: 1fr 110px 160px 30px;
  gap: 6px;
  align-items: center;
}
.grp-thead { padding: 4px 0; font: 500 10px var(--mono); letter-spacing: 0.06em; color: var(--faint); }
.grp-row { padding: 6px 0; border-top: 1px solid rgba(0, 0, 0, 0.06); }
.grp-name { font-size: 12.5px; font-weight: 600; }
.grp-usage { font-size: 11.5px; color: var(--sub); }
.grp-usage.free { color: var(--faint); }
.grp-del { border: none; background: transparent; color: var(--red); font-size: 13px; cursor: pointer; padding: 2px 6px; }
.grp-del.off { color: #C9C5BB; cursor: not-allowed; }
.grp-empty { font-size: 12px; color: var(--faint); padding: 8px 0; border-top: 1px solid rgba(0, 0, 0, 0.06); }

.card-foot {
  border-top: 1px dashed rgba(0, 0, 0, 0.12);
  padding-top: 10px;
  display: flex;
  align-items: baseline;
  gap: 12px;
}
.foot-note { font-size: 11.5px; color: var(--muted); line-height: 1.55; flex: 1; }
.maj-del { flex: none; font-size: 11.5px; color: var(--red); cursor: pointer; }
.maj-del.off { color: #C9C5BB; cursor: not-allowed; }

.foot-hint {
  border-top: 1px dashed rgba(0, 0, 0, 0.12);
  padding-top: 10px;
  font-size: 11.5px;
  color: var(--muted);
  line-height: 1.55;
}

.rooms-panel { flex: 1; max-width: 720px; }
</style>
