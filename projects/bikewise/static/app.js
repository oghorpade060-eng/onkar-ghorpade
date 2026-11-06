"use strict";
const $ = (id) => document.getElementById(id);
const format = new Intl.NumberFormat("en-US");
const svgNS = "http://www.w3.org/2000/svg";
let report;
const chartSpecs = new Map();
let resizeTimer;

function svg(tag, attrs = {}, text) {
  const el = document.createElementNS(svgNS, tag);
  for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, String(value));
  if (text !== undefined) el.textContent = text;
  return el;
}
function showError(id, message) { $(id).textContent = message; $(id).hidden = !message; }
function route() {
  const id = ["overview", "scenario", "models", "learn"].includes(location.hash.slice(1)) ? location.hash.slice(1) : "overview";
  for (const view of document.querySelectorAll(".view")) view.hidden = view.id !== id;
  for (const item of document.querySelectorAll(".nav-item")) {
    const active = item.hash === `#${id}`;
    item.classList.toggle("active", active);
    if (active) item.setAttribute("aria-current", "page"); else item.removeAttribute("aria-current");
  }
  requestAnimationFrame(redrawVisibleCharts);
}
window.addEventListener("hashchange", route);
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(redrawVisibleCharts, 100);
});
route();

function redrawVisibleCharts() {
  for (const [id, args] of chartSpecs) {
    if ($(id).offsetParent !== null) lineChart(id, ...args);
  }
}

function lineChart(id, data, series, title, xLabel) {
  const container = $(id);
  chartSpecs.set(id, [data, series, title, xLabel]);
  container.replaceChildren();
  const width = Math.max(280, Math.round(container.clientWidth));
  const height = id === "actual-chart" ? 230 : 190;
  const pad = {left: 40, right: 12, top: 12, bottom: 29};
  const w = width - pad.left - pad.right, h = height - pad.top - pad.bottom;
  const max = Math.max(1, ...data.flatMap(row => series.map(s => row[s.key])));
  const ceiling = Math.ceil(max / 100) * 100;
  const drawing = svg("svg", {viewBox: `0 0 ${width} ${height}`, role: "img", "aria-label": title});
  drawing.append(svg("title", {}, title));
  for (let i=0; i<=4; i++) {
    const y = pad.top + h * i/4;
    drawing.append(svg("line", {x1:pad.left, y1:y, x2:width-pad.right, y2:y, stroke:"#e6ebe2", "stroke-dasharray":"3 4"}));
    drawing.append(svg("text", {x:pad.left-8, y:y+3, "text-anchor":"end"}, Math.round(ceiling*(1-i/4))));
  }
  const ticks = id === "actual-chart" && width > 600 ? 7 : 5;
  for(let i=0;i<ticks;i++) {
    const index = Math.round((data.length-1)*i/(ticks-1));
    drawing.append(svg("text", {x:pad.left+w*index/(data.length-1),y:height-6,"text-anchor": i===0?"start":i===ticks-1?"end":"middle"}, xLabel(data[index])));
  }
  for (const s of series) {
    const points = data.map((d,i)=>`${pad.left+w*i/(data.length-1)},${pad.top+h-h*d[s.key]/ceiling}`).join(" ");
    drawing.append(svg("polyline", {points, stroke:s.color, class:"line"}));
  }
  container.append(drawing);
}

function renderDashboard(data) {
  const m = data.metrics;
  $("rows").textContent = format.format(m.dataset_rows);
  $("mae").textContent = data.selected_test.mae.toFixed(1);
  $("r2").textContent = data.selected_test.r2.toFixed(4);
  $("winner").textContent = m.selected_model;
  lineChart("actual-chart", data.sample, [{key:"actual",color:"#26715b"},{key:"predicted",color:"#a4b346"}], "Actual and predicted rentals for the first test week", row=>row.time.slice(5,10));
  lineChart("hour-chart", data.hourly, [{key:"working",color:"#26715b"},{key:"nonworking",color:"#a89ec8"}], "Average hourly demand for working and non-working days", row=>`${String(row.hour).padStart(2,"0")}:00`);
  const names = {hr:"Hour",temp:"Temperature",workingday:"Working day",mnth:"Month",hum:"Humidity",weekday:"Weekday",yr:"Year",weathersit:"Weather",windspeed:"Wind speed",season:"Season",holiday:"Holiday"};
  const top = data.importance.slice(0,5), maxImportance = Math.max(1,...top.map(x=>x.increase_mae));
  $("importance").replaceChildren();
  for(const item of top) {
    const row=document.createElement("div"); row.className="importance-row";
    const label=document.createElement("span"); label.textContent=names[item.feature] || item.feature;
    const track=document.createElement("div"); track.className="importance-bar";
    const bar=svg("svg",{viewBox:"0 0 100 8",preserveAspectRatio:"none","aria-hidden":"true"});
    bar.append(svg("rect",{x:0,y:0,width:Math.max(0,item.increase_mae/maxImportance*100),height:8,rx:3,fill:"#26715b"}));track.append(bar);
    const value=document.createElement("span");value.textContent=item.increase_mae.toFixed(1);row.append(label,track,value);$("importance").append(row);
  }
  $("model-table").replaceChildren();
  for(const item of m.models) {
    const row=document.createElement("tr");
    const name=document.createElement("td");name.textContent=item.model;
    if(item.model===m.selected_model){row.className="selected";const tag=document.createElement("span");tag.className="selected-mark";tag.textContent="SELECTED ON VALIDATION";name.append(tag);}
    row.append(name);
    for(const value of [item.validation.mae,item.test.mae,item.test.rmse,item.test.r2]){const cell=document.createElement("td");cell.textContent=value.toFixed(3);row.append(cell);}
    $("model-table").append(row);
  }
  $("splits").replaceChildren();
  for(const [name,split] of Object.entries(m.splits)){
    const block=document.createElement("div");block.className="split";
    const title=document.createElement("strong");title.textContent=`${name} · ${format.format(split.rows)} rows`;
    const dates=document.createElement("p");dates.textContent=`${split.start} → ${split.end}`;block.append(title,dates);$("splits").append(block);
  }
}

for(let i=0;i<24;i++){const option=document.createElement("option");option.value=i;option.textContent=`${String(i).padStart(2,"0")}:00`;option.selected=i===8;$("hour").append(option);}
function sliderLabels(){ $("temperature-value").textContent=`${$("temperature").value} °C`;$("humidity-value").textContent=`${$("humidity").value}%`;$("wind-value").textContent=`${$("wind").value} km/h`; }
for(const id of ["temperature","humidity","wind"]) $(id).addEventListener("input",sliderLabels);
const presets={commute:{date:"2012-10-15",hour:8,weather:1,temperature:20,humidity:55,wind:10},rain:{date:"2012-11-12",hour:18,weather:3,temperature:12,humidity:85,wind:20},weekend:{date:"2012-10-14",hour:14,weather:1,temperature:24,humidity:45,wind:8}};
for(const button of document.querySelectorAll("[data-preset]")){button.addEventListener("click",()=>{for(const [key,value] of Object.entries(presets[button.dataset.preset]))$(key).value=value;sliderLabels();$("prediction-context").textContent="Inputs updated. Run Estimate demand to refresh the result.";});}
// Mark a displayed result as stale when its inputs change.
$("prediction-form").addEventListener("input",()=>{$("prediction-context").textContent="Inputs changed. Run Estimate demand to refresh the result.";});
$("prediction-form").addEventListener("submit",async(event)=>{
  event.preventDefault();showError("predict-error","");const button=$("predict-button");button.disabled=true;
  const payload={date:$("date").value};for(const id of ["hour","weather","temperature","humidity","wind"])payload[id]=Number($(id).value);
  try{
    const response=await fetch("/api/predict",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    const data=await response.json();if(!response.ok)throw new Error(data.error||"Prediction unavailable.");
    $("prediction").textContent=format.format(data.prediction);
    $("prediction-context").textContent=`${data.date} · ${String(data.hour).padStart(2,"0")}:00 · ${data.model}`;
    $("prediction-caution").textContent=`Average held-out error: ${data.test_mae.toFixed(1)} bikes/hour. This is not a confidence interval.${data.fitting_period?" This date was in the model-fitting period.":""}`;
    lineChart("scenario-chart",data.curve,[{key:"predicted",color:"#26715b"}],"Estimated demand across 24 hours under fixed weather inputs",row=>`${String(row.hour).padStart(2,"0")}:00`);
  }catch(error){showError("predict-error",error.message);$("prediction-context").textContent="Estimate failed. Check the error and try again.";}finally{button.disabled=false;}
});

async function init(){
  try{
    const [dataResponse,healthResponse]=await Promise.all([fetch("/api/report"),fetch("/api/health")]);
    const data=await dataResponse.json();const health=await healthResponse.json();
    if(!dataResponse.ok)throw new Error(data.error||"Report unavailable.");
    report=data;renderDashboard(report);$("status").textContent=health.model_loaded?"Ready · local model":"Training required";
    if(!health.model_loaded)showError("global-error","The report is available. Run python train.py to enable predictions.");
  }catch(error){$("status").textContent="Setup required";showError("global-error",`${error.message} Start with python train.py, then python app.py.`);}
}
init();
