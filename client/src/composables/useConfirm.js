import { reactive } from 'vue'

/* Single global confirm-dialog instance. Call `confirmDelete(...)` from anywhere;
   it returns a Promise that resolves to true (confirmed) or false (cancelled).
   The dialog itself is mounted once in App.vue via <ConfirmDialog>. */

const state = reactive({
  open: false,
  title: 'Удалить элемент?',
  message: 'Это действие необратимо.',
  entityName: '',
  confirmLabel: 'Удалить',
  cancelLabel: 'Отмена',
})

let resolver = null

function settle(result) {
  if (!state.open) return
  state.open = false
  const r = resolver
  resolver = null
  if (r) r(result)
}

export function confirmDelete(opts = {}) {
  // resolve any dialog still pending as cancelled before opening a new one
  settle(false)
  state.title = opts.title || 'Удалить элемент?'
  state.message = opts.message || 'Это действие необратимо.'
  state.entityName = opts.entityName || ''
  state.confirmLabel = opts.confirmLabel || 'Удалить'
  state.cancelLabel = opts.cancelLabel || 'Отмена'
  state.open = true
  return new Promise((resolve) => { resolver = resolve })
}

export function useConfirmDialog() {
  return {
    state,
    confirm: () => settle(true),
    cancel: () => settle(false),
  }
}
