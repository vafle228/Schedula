/**
 * Shared UI state for «Справочники» — which tab is open, which entity is
 * selected, and the inline add-group form.
 *
 * Module-scoped (like `useDistribution.js`'s `dui` and `useSchedule.js`'s `ui`)
 * so it survives view remounts and can be driven from outside — the onboarding
 * tour switches tabs through it instead of synthesising DOM clicks.
 */
import { reactive } from 'vue'

export const dirUi = reactive({
  sec: 'majors', // types | majors | teachers | rooms
  mid: 'm1',
  mq: '',
  gf: { name: '', course: '1', err: '' },
  tid: 't1',
  q: '',
  photoErr: '', // ошибка последней загрузки фото на карточке преподавателя
  addTeacher: false,
  addMajor: false,
})
