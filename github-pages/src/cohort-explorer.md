# Interactive Cohort Explorer
## Aphasia Distribution by Selected Conditions
This interactive graph allows you to explore the post-stroke aphasia patient cohort by selecting various health conditions and medication patterns. The graph will automatically update and show the aphasia distribution within your filtered group (multiple selections are cumulative as patients will match every condition checked). Toggle between raw counts, population prevalence, or within-group prevalence.

```js
const data = await FileAttachment("high_risk_cohort_no_dementia.csv").csv({typed: true});
```
```js
const totalPatients = data.length;
const withAphasia = data.filter(d => d.has_aphasia === 1).length;
const withoutAphasia = data.filter(d => d.has_aphasia === 0).length;
```

---

**Total Patients:** ${totalPatients.toLocaleString()} | **With Aphasia:** ${withAphasia.toLocaleString()} | **Without Aphasia:** ${withoutAphasia.toLocaleString()}

---

```js
// filter and aphasia prevalence
function getFilteredData(data, selectedConditions) {
  let filtered = data;
  
  // AND logic
  if (selectedConditions.length > 0) {
    filtered = data.filter(d => 
      selectedConditions.every(cond => d[cond] === 1)
    );
  }
  
  const withAphasia = filtered.filter(d => d.has_aphasia === 1).length;
  const withoutAphasia = filtered.filter(d => d.has_aphasia === 0).length;
  const total = filtered.length;
  
  // within-group prevalence
  const totalWithAphasia = data.filter(d => d.has_aphasia === 1).length;
  const totalWithoutAphasia = data.filter(d => d.has_aphasia === 0).length;
  
  return [
    {
      group: 'With Aphasia',
      count: withAphasia,
      total: total,
      prevalence: total > 0 ? (withAphasia / total) * 100 : 0,
      withinGroupPrevalence: totalWithAphasia > 0 ? (withAphasia / totalWithAphasia) * 100 : 0,
      groupTotal: totalWithAphasia
    },
    {
      group: 'Without Aphasia',
      count: withoutAphasia,
      total: total,
      prevalence: total > 0 ? (withoutAphasia / total) * 100 : 0,
      withinGroupPrevalence: totalWithoutAphasia > 0 ? (withoutAphasia / totalWithoutAphasia) * 100 : 0,
      groupTotal: totalWithoutAphasia
    }
  ];
}

const conditions = [
  {value: 'has_depression', label: 'Depression'},
  {value: 'has_anxiety', label: 'Anxiety'},
  {value: 'has_bipolar', label: 'Bipolar'},
  {value: 'has_schizophrenia', label: 'Schizophrenia'},
  {value: 'has_ptsd', label: 'PTSD'},
  {value: 'has_psychotic_disorder', label: 'Psychotic Disorder'},
  {value: 'has_seizure', label: 'Seizure'},
  {value: 'has_polypharmacy', label: 'Polypharmacy (PIMs)'},
  {value: 'has_polypharmacy_all_meds', label: 'Polypharmacy (All Meds)'},
  {value: 'has_any_mental_health_condition', label: 'Any Mental Health Condition'},
  {value: 'has_antidepressant', label: 'Antidepressant'},
  {value: 'has_antipsychotic', label: 'Antipsychotic'},
  {value: 'has_anxiolytic', label: 'Anxiolytic'},
  {value: 'has_hypnotic_sedative', label: 'Hypnotic/Sedative'},
  {value: 'is_high_risk', label: 'High Risk'},
  {value: 'antidep_risk', label: 'Antidepressant Risk'},
  {value: 'anxiolytic_risk', label: 'Anxiolytic Risk'},
  {value: 'hyp_sed_risk', label: 'Hypnotic/Sedative Risk'},
  {value: 'antipsych_risk', label: 'Antipsychotic Risk'}
];

```
```js
const conditionInput = Inputs.checkbox(
  conditions.map(c => c.label),
  {label: "Filter by Conditions", value: []}
);
const selectedConditionLabels = Generators.input(conditionInput);
view(conditionInput);
```
```js
const viewModeInput = Inputs.radio(
  ["Counts", "Population Prevalence %", "Within-Group Prevalence %"],
  {label: "Display Mode", value: "Counts"}
);
const currentViewMode = Generators.input(viewModeInput);
view(viewModeInput);
```
```js
const selectedConditions = selectedConditionLabels.map(label => 
  conditions.find(c => c.label === label).value
);

const chartData = getFilteredData(data, selectedConditions);
const totalFiltered = chartData[0].total;
```

**Filtered Cohort Size:** ${totalFiltered.toLocaleString()} patients  
**Filtered by:** ${selectedConditions.length > 0 ? ` ${selectedConditionLabels.join(' AND ')}` : 'Showing all patients'}
```js
Plot.plot({
  width: 600,
  height: 400,
  marginBottom: 60,
  x: {
    label: null
  },
  y: {
    label: currentViewMode === "Counts" ? "Number of Patients" : 
           currentViewMode === "Population Prevalence %" ? "Prevalence (% of filtered cohort)" :
           "Prevalence (% of aphasia/non-aphasia group)",
    grid: true,
    domain: currentViewMode === "Counts" ? [0, Math.max(...chartData.map(d => d.count)) * 1.1] : [0, 100]
  },
  color: {
    domain: ['With Aphasia', 'Without Aphasia'],
    range: ['#ff7f0e', '#1f77b4'] // should be tab:blue and tab:orange, my usual defaults :p
  },
  marks: [
    Plot.barY(chartData, {
      x: "group",
      y: currentViewMode === "Counts" ? "count" : 
         currentViewMode === "Population Prevalence %" ? "prevalence" : "withinGroupPrevalence",
      fill: "group",
      tip: true,
      title: d => currentViewMode === "Counts" 
        ? `${d.group}\nCount: ${d.count.toLocaleString()}\nTotal: ${d.total.toLocaleString()}`
        : currentViewMode === "Population Prevalence %"
        ? `${d.group}\nPopulation Prevalence: ${d.prevalence.toFixed(1)}%\nCount: ${d.count.toLocaleString()} / ${d.total.toLocaleString()}`
        : `${d.group}\nWithin-Group Prevalence: ${d.withinGroupPrevalence.toFixed(1)}%\nCount: ${d.count.toLocaleString()} / ${d.groupTotal.toLocaleString()} total ${d.group.toLowerCase()} patients`
    }),
    Plot.text(chartData, {
      x: "group",
      y: currentViewMode === "Counts" ? "count" : 
         currentViewMode === "Population Prevalence %" ? "prevalence" : "withinGroupPrevalence",
      text: d => currentViewMode === "Counts" 
        ? d.count.toLocaleString()
        : currentViewMode === "Population Prevalence %"
        ? `${d.prevalence.toFixed(1)}%`
        : `${d.withinGroupPrevalence.toFixed(1)}%`,
      dy: -10,
      fill: "black",
      fontSize: 14,
      fontWeight: "bold"
    })
  ]
})
```

---

* Polypharmacy (All Meds) refers to people who have been on 5+ meds for 30+ days concurrently within the observation period. Polypharmacy (PIMs) refers to the same parameters except only within the medications considered PIMs

* Risk conditions consist of those who have been taking a PIM within the observation period, but without any corresponding diagnoses for the mental health conditions associated to that medication. For more information on this, refer to the [Methodology](./methodology#high-risk-methodology) section

* This graph is also modularizable in that as long as you replace the `high_risk_cohort_no_dementia.csv` with a new one (can be created automatically in our repository with the advised makefile commands), changes will automatically be applied.