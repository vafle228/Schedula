/**
 * Чтение файла фото преподавателя.
 *
 * Наверх уходит оригинал файла — обрезку в квадрат, уменьшение и перевод в JPEG
 * делает сервер (Pillow), обратно приходит готовый data-URL. Здесь только
 * быстрые проверки, чтобы не гонять заведомо негодный файл по сети.
 */

/** Совпадает с MAX_UPLOAD_BYTES на сервере. */
export const MAX_PHOTO_BYTES = 12 * 1024 * 1024

/**
 * Прочитать выбранный файл в data-URL.
 *
 * @param {File|null|undefined} file — файл из <input type="file">.
 * @returns {Promise<string>} data-URL для отправки на сервер.
 * @throws {Error} с текстом для пользователя, если файл не подходит.
 */
export function readPhotoFile(file) {
  return new Promise((resolve, reject) => {
    if (!file) {
      reject(new Error('Файл не выбран'))
      return
    }
    if (!file.type || !file.type.startsWith('image/')) {
      reject(new Error('Нужен файл изображения — JPEG, PNG или WebP'))
      return
    }
    if (file.size > MAX_PHOTO_BYTES) {
      reject(new Error('Файл слишком большой — максимум 12 МБ'))
      return
    }
    const r = new FileReader()
    r.onload = () => resolve(r.result)
    r.onerror = () => reject(new Error('Не удалось прочитать файл'))
    r.readAsDataURL(file)
  })
}
