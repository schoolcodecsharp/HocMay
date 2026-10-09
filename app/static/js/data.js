(() => {
  const pageSize = 20;
  let offset = 0, total = 0, requestedOffset = 0, loaded = false;
  const fields = ['row_id', 'MedInc', 'HouseAge', 'AveRooms', 'AveBedrms', 'Population', 'AveOccup', 'Latitude', 'Longitude', 'MedHouseVal'];
  const previous = document.querySelector('#previous');
  const next = document.querySelector('#next');
  const retry = document.querySelector('#data-retry');
  const error = document.querySelector('#data-error');
  const status = document.querySelector('#page-status');
  const table = document.querySelector('#data-table');
  const body = document.querySelector('#data-table tbody');

  function pageLabel() {
    return total === 0 ? 'Train: chưa có dòng dữ liệu' :
      `Train: ${offset + 1}–${Math.min(offset + pageSize, total)} / ${total} dòng`;
  }

  async function load(target = offset) {
    requestedOffset = target;
    previous.disabled = next.disabled = retry.disabled = true;
    error.hidden = retry.hidden = true;
    table.setAttribute('aria-busy', 'true');
    status.textContent = 'Đang đọc CSDL…';
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch(`/api/data?offset=${target}&limit=${pageSize}`, {signal: controller.signal});
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Không đọc được CSDL.');
      const rows = [];
      for (const row of data.rows) {
        const tr = document.createElement('tr');
        for (const field of fields) {
          const td = document.createElement('td');
          td.textContent = Number.isInteger(row[field]) ? row[field] : row[field].toFixed(4);
          tr.append(td);
        }
        rows.push(tr);
      }
      // Chỉ đổi trang khi nhận dữ liệu thành công; lỗi không làm mất trang cũ.
      body.replaceChildren(...rows);
      offset = target;
      total = data.total;
      loaded = true;
      status.textContent = pageLabel();
    } catch (e) {
      error.textContent = e.name === 'AbortError'
        ? 'Đọc dữ liệu quá thời gian. Kiểm tra kết nối rồi nhấn Thử lại.'
        : `Không tải được trang dữ liệu. ${e.message} Nhấn Thử lại sau khi kiểm tra kết nối/CSDL.`;
      error.hidden = retry.hidden = false;
      status.textContent = loaded ? `${pageLabel()} (giữ trang đã tải)` : 'Chưa tải được CSDL';
    } finally {
      clearTimeout(timeout);
      table.setAttribute('aria-busy', 'false');
      retry.disabled = false;
      previous.disabled = !loaded || offset === 0;
      next.disabled = !loaded || offset + pageSize >= total;
    }
  }
  previous.addEventListener('click', () => load(Math.max(0, offset - pageSize)));
  next.addEventListener('click', () => load(offset + pageSize));
  retry.addEventListener('click', () => load(requestedOffset));
  load();
})();
