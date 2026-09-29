const form = document.querySelector('#estimate-form');
const button = document.querySelector('#submit-button');
const formError = document.querySelector('#form-error');
const emptyState = document.querySelector('#result-empty');
const resultContent = document.querySelector('#result-content');

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
  if (!inputs.every(validateInput)) {
    formError.textContent = 'Hãy sửa các trường được đánh dấu trước khi chạy ước lượng.';
    formError.hidden = false;
    return;
  }

  const payload = Object.fromEntries(inputs.map((input) => [input.name, Number(input.value)]));
  button.disabled = true;
  button.querySelector('span').textContent = 'Đang ước lượng…';
  try {
    const response = await fetch('/api/estimate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      const detail = Array.isArray(data.detail)
        ? data.detail.map((item) => item.msg).join(' ')
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
    formError.textContent = `Không thể ước lượng: ${error.message}`;
    formError.hidden = false;
  } finally {
    button.disabled = false;
    button.querySelector('span').textContent = 'Chạy ước lượng';
  }
});
