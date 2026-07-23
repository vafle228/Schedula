/**
 * Service layer: one function per endpoint of «API — Спецификация ендпоинтов».
 */
import { request } from './client.js'

export const api = {
  /* per-year semester settings (schedule grid) */
  getSettings: (yearId) => request('GET', `/settings?yearId=${yearId}`),
  patchSettings: (yearId, period, body) => request('PATCH', `/settings/${period}?yearId=${yearId}`, body),

  /* academic years */
  getYears: () => request('GET', '/years'),
  createYear: (body) => request('POST', '/years', body),
  activateYear: (id) => request('POST', `/years/${id}/activate`),
  deleteYear: (id) => request('DELETE', `/years/${id}`),
  rolloverYear: (id, body) => request('POST', `/years/${id}/rollover`, body),

  /* topic types */
  getTopicTypes: () => request('GET', '/topic-types'),
  createTopicType: (body) => request('POST', '/topic-types', body),
  patchTopicType: (k, body) => request('PATCH', `/topic-types/${encodeURIComponent(k)}`, body),
  deleteTopicType: (k) => request('DELETE', `/topic-types/${encodeURIComponent(k)}`),

  /* majors & groups */
  getMajors: () => request('GET', '/majors'),
  createMajor: (body) => request('POST', '/majors', body),
  patchMajor: (id, body) => request('PATCH', `/majors/${id}`, body),
  deleteMajor: (id) => request('DELETE', `/majors/${id}`),
  getGroups: (yearId) => request('GET', `/groups?yearId=${yearId}`),
  createGroup: (majorId, body) => request('POST', `/majors/${majorId}/groups`, body),
  patchGroup: (id, body) => request('PATCH', `/groups/${id}`, body),
  deleteGroup: (id) => request('DELETE', `/groups/${id}`),

  /* disciplines & topics */
  getDisciplines: (yearId) => request('GET', `/disciplines?yearId=${yearId}`),
  createDiscipline: (body) => request('POST', '/disciplines', body),
  patchDiscipline: (id, body) => request('PATCH', `/disciplines/${id}`, body),
  deleteDiscipline: (id) => request('DELETE', `/disciplines/${id}`),
  createTopic: (disciplineId, body) => request('POST', `/disciplines/${disciplineId}/topics`, body),
  patchTopic: (id, body) => request('PATCH', `/topics/${id}`, body),
  deleteTopic: (id) => request('DELETE', `/topics/${id}`),

  /* assignments (keyed by group + topic) */
  getAssignments: (yearId) => request('GET', `/assignments?yearId=${yearId}`),
  assignTopic: (groupId, topicId, teacherId) => request('PUT', `/topics/${topicId}/assignment`, { groupId, teacherId }),
  unassignTopic: (groupId, topicId) => request('DELETE', `/topics/${topicId}/assignment?groupId=${groupId}`),
  assignDiscipline: (groupId, disciplineId, teacherId) => request('POST', `/disciplines/${disciplineId}/assignment`, { groupId, teacherId }),
  batchAssign: (yearId, ops) => request('POST', '/assignments/batch', { yearId, ops }),

  /* teachers & absences */
  getTeachers: () => request('GET', '/teachers'),
  createTeacher: (body) => request('POST', '/teachers', body),
  patchTeacher: (id, body) => request('PATCH', `/teachers/${id}`, body),
  deleteTeacher: (id) => request('DELETE', `/teachers/${id}`),
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
  getLessons: (yearId) => request('GET', `/lessons?yearId=${yearId}`),
  createLesson: (body) => request('POST', '/lessons', body),
  patchLesson: (id, body) => request('PATCH', `/lessons/${id}`, body),
  deleteLesson: (id) => request('DELETE', `/lessons/${id}`),
  pinLesson: (id) => request('PUT', `/lessons/${id}/pin`),
  unpinLesson: (id) => request('DELETE', `/lessons/${id}/pin`),

  /* generation */
  getReadiness: (yearId, period) => request('GET', `/schedule/readiness?yearId=${yearId}&period=${period}`),
  startGeneration: (yearId, period, mode) => request('POST', '/schedule/generate', { yearId, period, mode }),
  getGenerationStatus: (jobId) => request('GET', `/schedule/generate/${jobId}`),
  cancelGeneration: (jobId) => request('POST', `/schedule/generate/${jobId}/cancel`),
  acceptGeneration: (jobId) => request('POST', `/schedule/generate/${jobId}/accept`),
  rollbackGeneration: (jobId) => request('POST', `/schedule/generate/${jobId}/rollback`),

  /* conflicts */
  getConflicts: (yearId, period) => request('GET', `/schedule/conflicts?yearId=${yearId}&period=${period}`),

  /* exports */
  exportCurriculum: (yearId, period) => request('POST', '/exports/curriculum', { yearId, period }),
  exportSchedule: (body) => request('POST', '/exports/schedule', body),
  getExport: (id) => request('GET', `/exports/${id}`),
}
