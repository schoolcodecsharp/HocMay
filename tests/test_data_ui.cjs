// Không cần npm dependency: giả lập DOM tối thiểu để test logic phân trang.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../app/static/js/data.js'), 'utf8');

function element() {
  return {
    hidden: false, disabled: false, textContent: '', children: [], events: {}, attrs: {},
    addEventListener(name, action) { this.events[name] = action; },
    setAttribute(name, value) { this.attrs[name] = value; },
    append(child) { this.children.push(child); },
    replaceChildren(...children) { this.children = children; },
  };
}
const flush = () => new Promise(resolve => setImmediate(resolve));
function setup(responses) {
  const nodes = new Map();
  const calls = [];
  let timer;
  const document = {
    querySelector(key) { if (!nodes.has(key)) nodes.set(key, element()); return nodes.get(key); },
    createElement: element,
  };
  vm.runInNewContext(source, {
    document, AbortController,
    setTimeout: fn => { timer = fn; return 1; }, clearTimeout() {},
    fetch: async (url, options) => {
      calls.push(url);
      const response = responses.shift();
      if (response instanceof Error) throw response;
      if (typeof response === 'function') return response(options);
      return {ok: true, json: async () => response};
    },
  });
  return {get: key => nodes.get(key), calls, expire: () => timer()};
}
function page(offset = 0, total = 14448) {
  const fields = ['MedInc','HouseAge','AveRooms','AveBedrms','Population','AveOccup','Latitude','Longitude','MedHouseVal'];
  return {total, rows: Array.from({length: Math.min(20, total)}, (_, i) =>
    ({row_id: offset + i, ...Object.fromEntries(fields.map(key => [key, 1.23456]))}))};
}

test('next/previous commit rows and offset after successful response', async () => {
  const ui = setup([page(), page(20), page()]);
  await flush();
  assert.equal(ui.get('#previous').disabled, true);
  await ui.get('#next').events.click();
  assert.match(ui.get('#page-status').textContent, /21–40/);
  assert.equal(ui.get('#data-table tbody').children.length, 20);
  await ui.get('#previous').events.click();
  assert.match(ui.get('#page-status').textContent, /1–20/);
});

test('failed next preserves current rows and retries the same requested page', async () => {
  const ui = setup([page(), new Error('Network unavailable'), page(20)]);
  await flush();
  const rows = ui.get('#data-table tbody').children;
  await ui.get('#next').events.click();
  assert.equal(ui.get('#data-table tbody').children, rows);
  assert.match(ui.get('#page-status').textContent, /1–20.*giữ trang/);
  assert.equal(ui.get('#data-retry').hidden, false);
  await ui.get('#data-retry').events.click();
  assert.match(ui.calls[2], /offset=20/);
  assert.match(ui.get('#page-status').textContent, /21–40/);
  assert.equal(ui.get('#data-error').hidden, true);
});

test('initial failure can recover without reloading the whole page', async () => {
  const ui = setup([new Error('Offline'), page()]);
  await flush();
  assert.equal(ui.get('#next').disabled, true);
  assert.equal(ui.get('#data-retry').hidden, false);
  await ui.get('#data-retry').events.click();
  assert.equal(ui.get('#next').disabled, false);
});

test('empty data is explicit and both pagination controls are disabled', async () => {
  const ui = setup([page(0, 0)]);
  await flush();
  assert.match(ui.get('#page-status').textContent, /chưa có dòng/);
  assert.equal(ui.get('#previous').disabled, true);
  assert.equal(ui.get('#next').disabled, true);
});

test('timeout exposes retry and clears busy state', async () => {
  const ui = setup([({signal}) => new Promise((resolve, reject) => {
    signal.addEventListener('abort', () => {
      const error = new Error('Timeout'); error.name = 'AbortError'; reject(error);
    });
  })]);
  ui.expire();
  await flush();
  assert.match(ui.get('#data-error').textContent, /quá thời gian/);
  assert.equal(ui.get('#data-retry').hidden, false);
  assert.equal(ui.get('#data-table').attrs['aria-busy'], 'false');
});
