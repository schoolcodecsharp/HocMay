const form = document.querySelector('#estimate-form');
const button = document.querySelector('#submit-button');
const formError = document.querySelector('#form-error');
const emptyState = document.querySelector('#result-empty');
const resultContent = document.querySelector('#result-content');
let revision = 0;
let pendingRequest = null;

function clearErrors() {
  formError.hidden = true;
  formError.textContent = '';
  form.querySelectorAll('input').forEach((input) => input.removeAttribute('aria-invalid'));
  form.querySelectorAll('.field-error').forEach((error) => { error.textContent = ''; });
}

function validateInput(input) {
  const value = Number(input.value);
  let message = '';
  if (input.value.trim() === '') message = 'Vui lòng nhập giá trị.';
  else if (!Number.isFinite(value)) message = 'Giá trị phải là số hữu hạn.';
  else if (value < Number(input.min) || value > Number(input.max)) message = `Giá trị phải từ ${input.min} đến ${input.max}.`;
  else if (input.name === 'Population' && !Number.isInteger(value)) message = 'Dân số phải là số nguyên.';
  else if (input.name === 'AveBedrms' && value > Number(form.elements.AveRooms.value)) message = 'Số phòng ngủ không thể lớn hơn tổng số phòng.';
  if (message) {
    input.setAttribute('aria-invalid', 'true');
    document.querySelector(`#${input.name}-error`).textContent = message;
  }
  return !message;
}

form?.addEventListener('submit', async (event) => {
  event.preventDefault();
  clearErrors();
  const inputs = [...form.querySelectorAll('input')];
  if (!inputs.map(validateInput).every(Boolean)) {
    formError.textContent = 'Hãy sửa các trường được đánh dấu trước khi chạy ước lượng.';
    formError.hidden = false;
    form.querySelector('[aria-invalid="true"]')?.focus();
    return;
  }

  const payload = Object.fromEntries(inputs.map((input) => [input.name, Number(input.value)]));
  pendingRequest?.abort();
  const controller = new AbortController();
  pendingRequest = controller;
  const requestRevision = ++revision;
  const timeout = setTimeout(() => controller.abort(), 15000);
  resultContent.hidden = true;
  emptyState.hidden = false;
  button.disabled = true;
  button.querySelector('span').textContent = 'Đang ước lượng…';
  try {
    const response = await fetch('/api/estimate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    const data = await response.json();
    // Input đã đổi: bỏ response cũ, không gán prediction cho dữ liệu mới.
    if (requestRevision !== revision) return;
    if (!response.ok) {
      if (Array.isArray(data.detail)) {
        data.detail.forEach((item) => {
          const input = form.elements.namedItem(item.field);
          if (input) {
            input.setAttribute('aria-invalid', 'true');
            document.getElementById(`${item.field}-error`).textContent = item.message || item.msg;
          }
        });
      }
      const detail = Array.isArray(data.detail)
        ? data.detail.map((item) => `${item.field || ''}: ${item.message || item.msg}`).join(' ')
        : data.detail;
      throw new Error(detail || 'API từ chối dữ liệu đầu vào.');
    }
    document.querySelector('#prediction-value').textContent = data.prediction.toFixed(3);
    document.querySelector('#usd-value').textContent = `≈ ${new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(data.estimated_usd)}`;
    document.querySelector('#model-name').textContent = data.model.replaceAll('_', ' ');
    document.querySelector('#result-warning').textContent = data.warning;
    emptyState.hidden = true;
    resultContent.hidden = false;
  } catch (error) {
    if (requestRevision !== revision) return;
    formError.textContent = error.name === 'AbortError'
      ? 'Yêu cầu quá thời gian chờ. Kiểm tra server rồi bấm Chạy ước lượng để thử lại.'
      : `Không thể ước lượng: ${error.message}. Kiểm tra dữ liệu hoặc server rồi thử lại.`;
    formError.hidden = false;
  } finally {
    clearTimeout(timeout);
    if (requestRevision === revision) {
      pendingRequest = null;
      button.disabled = false;
      button.querySelector('span').textContent = 'Chạy ước lượng';
    }
  }
});

form?.addEventListener('input', () => {
  revision += 1;
  pendingRequest?.abort();
  pendingRequest = null;
  button.disabled = false;
  button.querySelector('span').textContent = 'Chạy ước lượng';
  clearErrors();
  resultContent.hidden = true;
  emptyState.hidden = false;
});
