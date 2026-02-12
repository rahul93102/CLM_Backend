(function () {
  const el = document.getElementById('dashboard-data');
  if (!el) return;

  const dashboard = JSON.parse(el.textContent || '{}');

  const totals = dashboard.totals || {};
  const series = dashboard.series || {};
  const featureBreakdown = dashboard.feature_breakdown || {};

  const setText = (id, value) => {
    const node = document.getElementById(id);
    if (node) node.textContent = String(value ?? '—');
  };

  setText('kpi-users', totals.users ?? 0);
  setText('kpi-uploads', totals.uploads ?? 0);
  setText('kpi-searches', totals.searches ?? 0);

  const labels = (series.users && series.users.labels) || [];

  const engagementRoot = document.querySelector('#chart-engagement');
  if (engagementRoot) {
    new ApexCharts(engagementRoot, {
      chart: {
        type: 'area',
        height: 280,
        toolbar: { show: false },
        animations: { enabled: true, easing: 'easeinout', speed: 700 },
        foreColor: 'rgba(255,255,255,0.78)'
      },
      stroke: { curve: 'smooth', width: 3 },
      dataLabels: { enabled: false },
      grid: { borderColor: 'rgba(255,255,255,0.10)' },
      colors: ['#7c3aed', '#22c55e', '#f97316'],
      fill: { type: 'gradient', gradient: { opacityFrom: 0.25, opacityTo: 0.06 } },
      xaxis: { categories: labels },
      yaxis: { labels: { formatter: v => Math.round(v) } },
      legend: { position: 'top', horizontalAlign: 'right' },
      series: [
        { name: 'Users', data: (series.users && series.users.series) || [] },
        { name: 'Uploads', data: (series.uploads && series.uploads.series) || [] },
        { name: 'Searches', data: (series.searches && series.searches.series) || [] },
      ],
      tooltip: { theme: 'dark' },
    }).render();
  }

  const registrationsRoot = document.querySelector('#chart-registrations');
  if (registrationsRoot) {
    new ApexCharts(registrationsRoot, {
      chart: {
        type: 'line',
        height: 260,
        toolbar: { show: false },
        animations: { enabled: true, easing: 'easeinout', speed: 700 },
        foreColor: 'rgba(255,255,255,0.78)'
      },
      stroke: { curve: 'smooth', width: 3 },
      grid: { borderColor: 'rgba(255,255,255,0.10)' },
      colors: ['#60a5fa'],
      xaxis: { categories: labels },
      series: [{ name: 'Registrations', data: (series.users && series.users.series) || [] }],
      tooltip: { theme: 'dark' },
    }).render();
  }

  const aiRoot = document.querySelector('#chart-ai');
  if (aiRoot) {
    const aiPct = Number(dashboard.ai_adoption_pct || 0);
    new ApexCharts(aiRoot, {
      chart: { type: 'radialBar', height: 260, animations: { enabled: true, speed: 800 } },
      series: [aiPct],
      labels: ['AI Adoption'],
      colors: ['#7c3aed'],
      plotOptions: {
        radialBar: {
          hollow: { size: '62%' },
          dataLabels: {
            name: { color: 'rgba(255,255,255,0.70)' },
            value: { fontSize: '28px', fontWeight: 700, color: 'rgba(255,255,255,0.92)' },
          }
        }
      },
    }).render();
  }

  const featuresRoot = document.querySelector('#chart-features');
  if (featuresRoot) {
    const featureLabels = Object.keys(featureBreakdown);
    const featureValues = featureLabels.map(k => featureBreakdown[k] || 0);
    new ApexCharts(featuresRoot, {
      chart: { type: 'donut', height: 260, animations: { enabled: true, speed: 800 } },
      labels: featureLabels,
      series: featureValues,
      legend: { position: 'bottom' },
      dataLabels: { enabled: false },
      stroke: { width: 0 },
      colors: ['#22c55e', '#60a5fa', '#f97316', '#7c3aed', '#f43f5e', '#14b8a6', '#a3e635', '#eab308'],
      plotOptions: { pie: { donut: { size: '70%' } } },
      tooltip: { theme: 'dark' },
    }).render();
  }

  const list = document.getElementById('popular-templates');
  const templates = dashboard.popular_templates || [];
  if (list) {
    if (!templates.length) {
      list.innerHTML = "<div class='clm-list-item'><div class='clm-item-name'>No template usage yet</div><div class='clm-pill'>—</div></div>";
    } else {
      list.innerHTML = templates
        .map(t => {
          const name = String(t.name || '').replace(/</g, '&lt;');
          const type = String(t.type || '').replace(/</g, '&lt;');
          const count = t.count ?? 0;
          return `
          <div class="clm-list-item">
            <div>
              <div class="clm-item-name">${name}</div>
              <div class="clm-card-subtitle">${type}</div>
            </div>
            <div class="clm-item-meta">
              <span class="clm-pill">${count} uses</span>
            </div>
          </div>`;
        })
        .join('');
    }
  }

  // Month-wise feature usage
  const usageRoot = document.querySelector('#chart-feature-usage');
  const usage = (series.feature_usage) || { labels: [], series: [] };
  if (usageRoot) {
    const usageSeries = (usage.series || []).map(s => ({ name: s.name, data: s.data }));
    new ApexCharts(usageRoot, {
      chart: {
        type: 'area',
        height: 280,
        stacked: true,
        toolbar: { show: false },
        animations: { enabled: true, easing: 'easeinout', speed: 800 },
        foreColor: 'rgba(255,255,255,0.78)'
      },
      dataLabels: { enabled: false },
      stroke: { curve: 'smooth', width: 2 },
      fill: { type: 'gradient', gradient: { opacityFrom: 0.35, opacityTo: 0.08 } },
      grid: { borderColor: 'rgba(255,255,255,0.10)' },
      xaxis: { categories: usage.labels || [] },
      legend: { position: 'top', horizontalAlign: 'right' },
      tooltip: { theme: 'dark' },
      series: usageSeries,
    }).render();
  }
})();
