/**
 * Service layer: one function per endpoint of «API — Спецификация ендпоинтов».
 */
import { request } from './client.js'

export const api = {
  /* periods */
  getPeriods: () => request('GET', '/periods'),
  patchPeriod: (id, body) => request('PATCH', `/periods/${id}`, body),

  /* majors & groups */
  getMajors: () => request('GET', '/majors'),
  createMajor: (body) => request('POST', '/majors', body),
  patchMajor: (id, body) => request('PATCH', `/majors/${id}`, body),
  deleteMajor: (id) => request('DELETE', `/majors/${id}`),
  getGroups: () => request('GET', '/groups'),
  createGroup: (majorId, body) => request('POST', `/majors/${majorId}/groups`, body),
  patchGroup: (id, body) => request('PATCH', `/groups/${encodeURIComponent(id)}`, body),
  deleteGroup: (id) => request('DELETE', `/groups/${encodeURIComponent(id)}`),

  /* disciplines & topics */
  getDisciplines: () => request('GET', '/disciplines'),
  createDiscipline: (body) => request('POST', '/disciplines', body),
  patchDiscipline: (id, body) => request('PATCH', `/disciplines/${id}`, body),
  deleteDiscipline: (id) => request('DELETE', `/disciplines/${id}`),
  createTopic: (disciplineId, body) => request('POST', `/disciplines/${disciplineId}/topics`, body),
  patchTopic: (id, body) => request('PATCH', `/topics/${id}`, body),
  deleteTopic: (id) => request('DELETE', `/topics/${id}`),

  /* assignments */
  getAssignments: () => request('GET', '/assignments'),
  assignTopic: (topicId, teacherId) => request('PUT', `/topics/${topicId}/assignment`, { teacherId }),
  unassignTopic: (topicId) => request('DELETE', `/topics/${topicId}/assignment`),
  assignDiscipline: (disciplineId, teacherId) => request('POST', `/disciplines/${disciplineId}/assignment`, { teacherId }),
  batchAssign: (ops) => request('POST', '/assignments/batch', { ops }),

  /* teachers & absences */
  getTeachers: () => request('GET', '/teachers'),
  createTeacher: (body) => request('POST', '/teachers', body),
  patchTeacher: (id, body) => request('PATCH', `/teachers/${id}`, body),
  putTeacherPhoto: (id, dataUrl) => request('PUT', `/teachers/${id}/photo`, { dataUrl }),
  deleteTeacherPhoto: (id) => request('DELETE', `/teachers/${id}/photo`),
  putTeacherConstraints: (id, c) => request('PUT', `/teachers/${id}/constraints`, c),
  createAbsence: (teacherId, body) => request('POST', `/teachers/${teacherId}/absences`, body),
  patchAbsence: (id, body) => request('PATCH', `/absences/${id}`, body),
  deleteAbsence: (id) => request('DELETE', `/absences/${id}`),

  /* rooms */
  getRooms: () => request('GET', '/rooms'),
  createRoom: (body) => request('POST', '/rooms', body),
  patchRoom: (id, body) => request('PATCH', `/rooms/${encodeURIComponent(id)}`, body),
  deleteRoom: (id) => request('DELETE', `/rooms/${encodeURIComponent(id)}`),

  /* lessons */
  getLessons: () => request('GET', '/lessons'),
  createLesson: (body) => request('POST', '/lessons', body),
  patchLesson: (id, body) => request('PATCH', `/lessons/${id}`, body),
  deleteLesson: (id) => request('DELETE', `/lessons/${id}`),
  pinLesson: (id) => request('PUT', `/lessons/${id}/pin`),
  unpinLesson: (id) => request('DELETE', `/lessons/${id}/pin`),

  /* generation */
  getReadiness: (period) => request('GET', `/schedule/readiness?period=${period}`),
  startGeneration: (period, mode) => request('POST', '/schedule/generate', { period, mode }),
  getGenerationStatus: (jobId) => request('GET', `/schedule/generate/${jobId}`),
  cancelGeneration: (jobId) => request('POST', `/schedule/generate/${jobId}/cancel`),
  acceptGeneration: (jobId) => request('POST', `/schedule/generate/${jobId}/accept`),
  rollbackGeneration: (jobId) => request('POST', `/schedule/generate/${jobId}/rollback`),

  /* conflicts */
  getConflicts: (period) => request('GET', `/schedule/conflicts?period=${period}`),

  /* exports */
  exportCurriculum: (period) => request('POST', '/exports/curriculum', { period }),
  exportSchedule: (body) => request('POST', '/exports/schedule', body),
  getExport: (id) => request('GET', `/exports/${id}`),
}
