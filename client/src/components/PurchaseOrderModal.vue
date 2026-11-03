<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && backlogItem" class="modal-overlay" @click="close">
        <div class="modal-container" role="dialog" aria-modal="true" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">
              {{ mode === 'view' ? t('purchaseOrders.viewTitle') : t('purchaseOrders.createTitle') }}
            </h3>
            <button type="button" class="close-button" :aria-label="t('purchaseOrders.close')" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <!-- View mode: read-only details of the existing PO -->
          <template v-if="mode === 'view'">
            <div class="modal-body">
              <div class="item-header">
                <h4 class="item-name">{{ translateProductName(backlogItem.item_name) }}</h4>
                <div class="item-sku">{{ t('purchaseOrders.sku') }}: {{ backlogItem.item_sku }}</div>
              </div>

              <div v-if="showExistsNotice" class="form-notice" role="status">{{ t('purchaseOrders.alreadyExists') }}</div>

              <div v-if="viewLoading" class="state-message">{{ t('purchaseOrders.loading') }}</div>
              <div v-else-if="viewError" class="form-error" role="alert">{{ viewError }}</div>
              <div v-else-if="purchaseOrder" class="info-grid">
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrders.poId') }}</div>
                  <div class="info-value mono">{{ purchaseOrder.id }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrders.status') }}</div>
                  <div class="info-value">
                    <span class="status-badge">{{ statusLabel }}</span>
                  </div>
                </div>

                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrders.supplier') }}</div>
                  <div class="info-value">{{ purchaseOrder.supplier_name }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrders.quantity') }}</div>
                  <div class="info-value">{{ purchaseOrder.quantity }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrders.unitCost') }}</div>
                  <div class="info-value">{{ formatMoney(purchaseOrder.unit_cost) }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrders.total') }}</div>
                  <div class="info-value total-value">{{ formatMoney(purchaseOrder.quantity * purchaseOrder.unit_cost) }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrders.expectedDelivery') }}</div>
                  <div class="info-value">{{ formatDateOnly(purchaseOrder.expected_delivery_date) }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrders.createdDate') }}</div>
                  <div class="info-value">{{ formatCreatedDate(purchaseOrder.created_date) }}</div>
                </div>

                <div class="info-item full-width">
                  <div class="info-label">{{ t('purchaseOrders.notes') }}</div>
                  <div class="info-value notes-text">{{ purchaseOrder.notes || t('purchaseOrders.noNotes') }}</div>
                </div>
              </div>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-secondary" @click="close">{{ t('purchaseOrders.close') }}</button>
            </div>
          </template>

          <!-- Create mode: backlog summary plus the PO form -->
          <form v-else class="modal-form" novalidate @submit.prevent="submit">
            <div class="modal-body">
              <div class="item-header">
                <h4 class="item-name">{{ translateProductName(backlogItem.item_name) }}</h4>
                <div class="item-sku">{{ t('purchaseOrders.sku') }}: {{ backlogItem.item_sku }}</div>
              </div>

              <div class="info-grid summary-grid">
                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrders.orderId') }}</div>
                  <div class="info-value mono">{{ backlogItem.order_id }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrders.quantityNeeded') }}</div>
                  <div class="info-value">{{ backlogItem.quantity_needed }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrders.quantityAvailable') }}</div>
                  <div class="info-value">{{ backlogItem.quantity_available }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">{{ t('purchaseOrders.shortfall') }}</div>
                  <div class="info-value shortfall-value">{{ shortfall }}</div>
                </div>
              </div>

              <div class="form-grid">
                <div class="form-group full-width">
                  <label for="po-supplier">
                    {{ t('purchaseOrders.supplierName') }}
                    <span class="required" aria-hidden="true">*</span>
                  </label>
                  <input
                    id="po-supplier"
                    ref="supplierInput"
                    v-model="form.supplierName"
                    type="text"
                    maxlength="200"
                    autocomplete="off"
                    class="po-input"
                    :class="{ invalid: showError('supplierName') }"
                    :placeholder="t('purchaseOrders.supplierPlaceholder')"
                    :aria-invalid="showError('supplierName') ? 'true' : 'false'"
                    @blur="touched.supplierName = true"
                  />
                  <div v-if="showError('supplierName')" class="field-error">{{ fieldErrors.supplierName }}</div>
                </div>

                <div class="form-group">
                  <label for="po-quantity">
                    {{ t('purchaseOrders.quantity') }}
                    <span class="required" aria-hidden="true">*</span>
                  </label>
                  <input
                    id="po-quantity"
                    v-model="form.quantity"
                    type="number"
                    min="1"
                    step="1"
                    inputmode="numeric"
                    class="po-input"
                    :class="{ invalid: showError('quantity') }"
                    :aria-invalid="showError('quantity') ? 'true' : 'false'"
                    @blur="touched.quantity = true"
                  />
                  <div v-if="showError('quantity')" class="field-error">{{ fieldErrors.quantity }}</div>
                </div>

                <div class="form-group">
                  <label for="po-unit-cost">
                    {{ t('purchaseOrders.unitCostIn', { currency: currentCurrency }) }}
                    <span class="required" aria-hidden="true">*</span>
                  </label>
                  <div class="input-with-prefix">
                    <span class="input-prefix" aria-hidden="true">{{ currencySymbol }}</span>
                    <input
                      id="po-unit-cost"
                      v-model="form.unitCost"
                      type="number"
                      min="0"
                      :step="unitCostStep"
                      inputmode="decimal"
                      class="po-input has-prefix"
                      :class="{ invalid: showError('unitCost') }"
                      :aria-invalid="showError('unitCost') ? 'true' : 'false'"
                      @blur="touched.unitCost = true"
                    />
                  </div>
                  <div v-if="showError('unitCost')" class="field-error">{{ fieldErrors.unitCost }}</div>
                </div>

                <div class="form-group">
                  <label for="po-delivery-date">
                    {{ t('purchaseOrders.expectedDelivery') }}
                    <span class="required" aria-hidden="true">*</span>
                  </label>
                  <input
                    id="po-delivery-date"
                    v-model="form.expectedDeliveryDate"
                    type="date"
                    max="9999-12-31"
                    class="po-input"
                    :class="{ invalid: showError('expectedDeliveryDate') }"
                    :aria-invalid="showError('expectedDeliveryDate') ? 'true' : 'false'"
                    @blur="touched.expectedDeliveryDate = true"
                  />
                  <div v-if="showError('expectedDeliveryDate')" class="field-error">{{ fieldErrors.expectedDeliveryDate }}</div>
                </div>

                <div class="form-group order-total-group">
                  <div class="field-label">{{ t('purchaseOrders.orderTotal') }}</div>
                  <div class="order-total" aria-live="polite">{{ orderTotalDisplay }}</div>
                </div>

                <div class="form-group full-width">
                  <label for="po-notes">{{ t('purchaseOrders.notesOptional') }}</label>
                  <textarea
                    id="po-notes"
                    v-model="form.notes"
                    rows="3"
                    maxlength="1000"
                    class="po-input"
                    :placeholder="t('purchaseOrders.notesPlaceholder')"
                  ></textarea>
                </div>
              </div>

              <div v-if="submitError" class="form-error" role="alert">{{ submitError }}</div>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-secondary" @click="close">{{ t('purchaseOrders.cancel') }}</button>
              <button type="submit" class="btn-primary" :disabled="!isValid || submitting">
                {{ submitting ? t('purchaseOrders.submitting') : t('purchaseOrders.submit') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onBeforeUnmount } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrencyWithDecimals, convertToUsd, convertFromUsd } from '../utils/currency'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  backlogItem: {
    type: Object,
    default: null
  },
  mode: {
    type: String,
    default: 'create',
    validator: (value) => ['create', 'view'].includes(value)
  }
})

// po-exists: the server answered 409 (this backlog item already has a PO); payload is the backlog item id.
const emit = defineEmits(['close', 'po-created', 'po-exists'])

const { t, currentLocale, currentCurrency, translateProductName } = useI18n()

// Maps API field names (from 422 errors) to the label key used in the form.
const FIELD_LABEL_KEYS = {
  supplier_name: 'supplierName',
  quantity: 'quantity',
  unit_cost: 'unitCost',
  expected_delivery_date: 'expectedDelivery',
  notes: 'notes'
}

const ISO_DATE_PATTERN = /^(\d{4})-(\d{2})-(\d{2})$/

// Form state. Number inputs are kept as strings so a blank field is
// distinguishable from 0; they are parsed in the computed values below.
const form = reactive({
  supplierName: '',
  quantity: '1',
  unitCost: '',
  expectedDeliveryDate: '',
  notes: ''
})

// Field errors only show once the field has been blurred (or a submit was tried).
const touched = reactive({
  supplierName: false,
  quantity: false,
  unitCost: false,
  expectedDeliveryDate: false
})

const submitting = ref(false)
const submitError = ref('')
// True after a 409 from create: view mode then explains that the PO already existed.
const showExistsNotice = ref(false)
const supplierInput = ref(null)

const purchaseOrder = ref(null)
const viewLoading = ref(false)
const viewError = ref('')

// Bumped every time the modal opens, closes or switches item. Async results
// (view fetch, create request) compare against it so a slow response for a
// previous session can't overwrite the state of the current one.
let sessionId = 0

const shortfall = computed(() => {
  if (!props.backlogItem) return 0
  return props.backlogItem.quantity_needed - props.backlogItem.quantity_available
})

// v-model on an <input type="number"> casts what the user types to a number
// (Vue applies .number automatically), but an empty field stays ''. So the form
// value can be a string (the reset defaults) or a number. Normalize to a string first.
const parseNumericField = (value) => {
  const raw = String(value ?? '').trim()
  return raw === '' ? NaN : Number(raw)
}

const parsedQuantity = computed(() => parseNumericField(form.quantity))

// The unit cost is typed in the active display currency (yen in Japanese mode),
// not USD. It is converted to USD only for the POST payload.
const parsedUnitCost = computed(() => parseNumericField(form.unitCost))

const isJpy = computed(() => currentCurrency.value === 'JPY')
const currencySymbol = computed(() => (isJpy.value ? '¥' : '$'))
// Whole yen per step; USD goes to the cent.
const unitCostStep = computed(() => (isJpy.value ? '1' : '0.01'))

const roundTo = (value, decimals) => {
  const factor = 10 ** decimals
  return Math.round(value * factor) / factor
}

// If the language (and with it the currency) changes while the form is open,
// convert the typed unit cost so it keeps its value instead of being silently
// reinterpreted (1000 yen would otherwise become $1000).
// The converters never round, so a bare round trip leaves float noise
// (x / 150 * 150 misses x by a float ulp for ~10% of whole-yen amounts). Tidy the result
// for the input field: 6 decimals for USD, 2 for yen (the most the app displays).
// The yen rounding absorbs the USD rounding error (<= 7.5e-5 yen), so
// yen -> USD -> yen returns the original amount.
watch(currentCurrency, (next, prev) => {
  const typed = parsedUnitCost.value
  if (!Number.isFinite(typed)) return // empty or invalid: nothing to carry over
  const converted = convertFromUsd(convertToUsd(typed, prev), next)
  form.unitCost = String(roundTo(converted, next === 'JPY' ? 2 : 6))
})

// Returns an error message per invalid field; an empty object means valid.
const fieldErrors = computed(() => {
  const errors = {}

  const supplier = form.supplierName.trim()
  if (supplier.length === 0) {
    errors.supplierName = t('purchaseOrders.errors.supplierRequired')
  } else if (supplier.length > 200) {
    errors.supplierName = t('purchaseOrders.errors.supplierTooLong')
  }

  if (!Number.isSafeInteger(parsedQuantity.value) || parsedQuantity.value <= 0) {
    errors.quantity = t('purchaseOrders.errors.quantityInvalid')
  }

  if (!Number.isFinite(parsedUnitCost.value) || parsedUnitCost.value <= 0) {
    errors.unitCost = t('purchaseOrders.errors.unitCostInvalid')
  }

  // The date input yields '' for an incomplete date. The pattern also rejects
  // 5+ digit years, which the server's date parser would refuse.
  const date = form.expectedDeliveryDate
  if (!ISO_DATE_PATTERN.test(date)) {
    errors.expectedDeliveryDate = t('purchaseOrders.errors.deliveryRequired')
  }

  if (form.notes.length > 1000) {
    errors.notes = t('purchaseOrders.errors.notesTooLong')
  }

  return errors
})

const isValid = computed(() => Object.keys(fieldErrors.value).length === 0)

const showError = (field) => Boolean(touched[field] && fieldErrors.value[field])

// For USD amounts from the server (view mode); converts to JPY in Japanese mode.
const formatMoney = (amount) => formatCurrencyWithDecimals(amount, currentCurrency.value, 2)

// For an amount already in the active currency (what the user typed). Unlike
// formatMoney it must not convert again, or the total would stop matching the input.
const formatEnteredAmount = (amount) =>
  `${currencySymbol.value}${amount.toLocaleString(isJpy.value ? 'ja-JP' : 'en-US', {
    minimumFractionDigits: isJpy.value ? 0 : 2,
    maximumFractionDigits: 2
  })}`

const orderTotalDisplay = computed(() => {
  if (!Number.isFinite(parsedQuantity.value) || !Number.isFinite(parsedUnitCost.value)) return '-'
  if (parsedQuantity.value <= 0 || parsedUnitCost.value <= 0) return '-'
  return formatEnteredAmount(parsedQuantity.value * parsedUnitCost.value)
})

const dateLocale = computed(() => (currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'))

// 'YYYY-MM-DD' strings are parsed as local dates. new Date('2026-05-01') is UTC
// midnight and would render as the previous day in timezones behind UTC.
const formatDateOnly = (value) => {
  const match = ISO_DATE_PATTERN.exec(value || '')
  if (!match) return value || '-'
  const date = new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]))
  if (isNaN(date.getTime())) return value
  return date.toLocaleDateString(dateLocale.value, { year: 'numeric', month: 'long', day: 'numeric' })
}

const formatCreatedDate = (value) => {
  if (!value) return '-'
  const date = new Date(value)
  if (isNaN(date.getTime())) return value
  return date.toLocaleDateString(dateLocale.value, { year: 'numeric', month: 'long', day: 'numeric' })
}

// Shows the translated status when one exists, otherwise the raw server value
// (t() returns the key itself when a translation is missing).
const statusLabel = computed(() => {
  const status = purchaseOrder.value?.status
  if (!status) return '-'
  const key = `purchaseOrders.statuses.${status.toLowerCase()}`
  const translated = t(key)
  return translated === key ? status : translated
})

const resetForm = () => {
  form.supplierName = ''
  // Default to covering the shortfall; never below 1.
  form.quantity = String(Math.max(1, shortfall.value))
  form.unitCost = ''
  form.expectedDeliveryDate = ''
  form.notes = ''
  Object.keys(touched).forEach((field) => {
    touched[field] = false
  })
  submitError.value = ''
  submitting.value = false
}

// Turns a FastAPI error body into a message. `detail` is a string for 404/409
// and an array of { loc, msg } objects for 422 validation errors.
const extractErrorMessage = (err) => {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string' && detail) return detail

  if (Array.isArray(detail)) {
    const messages = detail
      .filter((entry) => entry && typeof entry.msg === 'string')
      .map((entry) => {
        const field = Array.isArray(entry.loc) ? entry.loc[entry.loc.length - 1] : null
        const labelKey = FIELD_LABEL_KEYS[field]
        const label = labelKey ? t(`purchaseOrders.${labelKey}`) : field
        return label ? `${label}: ${entry.msg}` : entry.msg
      })
    if (messages.length > 0) return messages.join('; ')
  }

  return null
}

const loadPurchaseOrder = async () => {
  const session = sessionId
  viewLoading.value = true
  viewError.value = ''
  purchaseOrder.value = null

  try {
    const po = await api.getPurchaseOrderByBacklogItem(props.backlogItem.id)
    if (session !== sessionId) return
    purchaseOrder.value = po
  } catch (err) {
    if (session !== sessionId) return
    console.error('Failed to load purchase order:', err)
    viewError.value = err?.response?.status === 404
      ? t('purchaseOrders.errors.notFound')
      : t('purchaseOrders.errors.loadFailed')
  } finally {
    if (session === sessionId) viewLoading.value = false
  }
}

const submit = async () => {
  if (submitting.value) return

  if (!isValid.value) {
    // Reached via Enter in a field: reveal what is wrong instead of doing nothing.
    Object.keys(touched).forEach((field) => {
      touched[field] = true
    })
    return
  }

  const session = sessionId
  // Captured now: props.backlogItem may point elsewhere by the time the request fails.
  const backlogItemId = props.backlogItem.id
  submitting.value = true
  submitError.value = ''

  const payload = {
    backlog_item_id: backlogItemId,
    supplier_name: form.supplierName.trim(),
    quantity: parsedQuantity.value,
    // The API stores USD; the field holds the active currency. Not rounded (see convertToUsd).
    unit_cost: convertToUsd(parsedUnitCost.value, currentCurrency.value),
    expected_delivery_date: form.expectedDeliveryDate
  }
  const notes = form.notes.trim()
  if (notes) payload.notes = notes

  try {
    const created = await api.createPurchaseOrder(payload)
    // Emit even if the modal was closed while the request was in flight: the
    // PO exists on the server, so the dashboard still needs to learn about it.
    emit('po-created', created)
  } catch (err) {
    // 409: the item already has a PO (e.g. created from another tab). Tell the
    // dashboard so it can flip the button and switch this modal to view mode.
    // Like po-created, emitted even if the modal was closed while in flight.
    if (err?.response?.status === 409) {
      // Only flag the notice if this form is still on screen; otherwise it would
      // linger and show up the next time the modal opens in view mode.
      if (session === sessionId) showExistsNotice.value = true
      emit('po-exists', backlogItemId)
    }
    if (session !== sessionId) return
    console.error('Failed to create purchase order:', err)
    submitError.value = extractErrorMessage(err) || t('purchaseOrders.errors.createFailed')
  } finally {
    if (session === sessionId) submitting.value = false
  }
}

const close = () => {
  emit('close')
}

const onKeydown = (event) => {
  if (event.key === 'Escape') close()
}

// (Re)initialise whenever the modal opens or is pointed at another item/mode.
watch(
  () => [props.isOpen, props.backlogItem?.id, props.mode],
  () => {
    sessionId++
    // The "already existed" notice belongs to the view session a 409 switches to;
    // it must not outlive closing the modal or going back to the form.
    if (!props.isOpen || props.mode !== 'view') showExistsNotice.value = false
    if (!props.isOpen || !props.backlogItem) return

    if (props.mode === 'view') {
      loadPurchaseOrder()
    } else {
      resetForm()
      // The input only exists after the modal has rendered.
      nextTick(() => supplierInput.value?.focus())
    }
  },
  { immediate: true }
)

// Escape-to-close is only listened for while the modal is open.
watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      document.addEventListener('keydown', onKeydown)
    } else {
      document.removeEventListener('keydown', onKeydown)
    }
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
  max-width: 640px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.close-button {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.close-button:hover {
  background: #f1f5f9;
  color: #0f172a;
}

/* The create-mode form wraps body + footer; keep them laid out like view mode. */
.modal-form {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.item-header {
  padding-bottom: 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 1.5rem;
}

.item-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.5rem 0;
}

.item-sku {
  font-size: 0.875rem;
  color: #64748b;
  font-family: 'Monaco', 'Courier New', monospace;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1.5rem;
}

.summary-grid {
  margin-bottom: 1.75rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 0;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-label,
.field-label {
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.info-value {
  font-size: 0.938rem;
  color: #0f172a;
  font-weight: 500;
  overflow-wrap: anywhere;
}

.info-value.mono {
  font-family: 'Monaco', 'Courier New', monospace;
  color: #2563eb;
}

.info-value.total-value {
  font-size: 1.125rem;
  color: #2563eb;
  font-weight: 700;
}

.info-value.shortfall-value {
  color: #dc2626;
  font-weight: 700;
}

.info-value.notes-text {
  white-space: pre-wrap;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.813rem;
  font-weight: 600;
  background: #fed7aa;
  color: #92400e;
}

.state-message {
  padding: 2rem 0;
  text-align: center;
  color: #64748b;
  font-size: 0.938rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 0;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.required {
  color: #dc2626;
  margin-left: 0.125rem;
}

.po-input {
  width: 100%;
  padding: 0.625rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.938rem;
  font-family: inherit;
  color: #0f172a;
  background: white;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  box-sizing: border-box;
}

.po-input::placeholder {
  color: #94a3b8;
}

.po-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.po-input.invalid {
  border-color: #ef4444;
}

textarea.po-input {
  resize: vertical;
  min-height: 72px;
}

.input-with-prefix {
  position: relative;
}

.input-prefix {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  font-size: 0.938rem;
  pointer-events: none;
}

.po-input.has-prefix {
  padding-left: 1.75rem;
}

.field-error {
  font-size: 0.813rem;
  color: #dc2626;
}

.order-total-group {
  justify-content: flex-end;
}

.order-total {
  padding: 0.625rem 0.75rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  font-size: 1.125rem;
  font-weight: 700;
  color: #2563eb;
}

/* Informational banner (not an error): a duplicate create fell back to this view. */
.form-notice {
  margin-bottom: 1.25rem;
  padding: 0.75rem 1rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  color: #1e40af;
  font-size: 0.875rem;
}

.form-error {
  margin-top: 1.25rem;
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #991b1b;
  font-size: 0.875rem;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-secondary {
  padding: 0.625rem 1.25rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-secondary:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.btn-primary {
  padding: 0.625rem 1.25rem;
  background: #3b82f6;
  border: 1px solid #3b82f6;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  color: white;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  border-color: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 560px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .modal-body {
    padding: 1.25rem;
  }
}

/* Modal transition animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
