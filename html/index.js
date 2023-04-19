var params,serverTime,d_stat,weather;
var errors = '';
var parModel = document.getElementById('par_mdl_elem');
var loader = document.getElementById('loader_elem');
var auto_checkboxes = document.getElementById('auto_checkboxes')
var door_btn_div = document.getElementById('doorbtndiv')
var setting_nodes = document.getElementById('setting_nodes')
var parForm = document.forms.par_form;

parModel.open = async function () {
  var data = await get_params();
  parForm.par_chbx_op_tm.value = data.open_method;
  parForm.par_chbx_cl_tm.value = data.close_method;
  if (data.open_method == 'sun') {
    parForm.par_open_sn.value = data.open;
  }
  if (data.open_method == 'time') {
    parForm.par_open_tm.value = data.open;
  }
  if (data.close_method == 'sun') {
    parForm.par_close_sn.value = data.close;
  }
  if (data.close_method == 'time') {
    parForm.par_close_tm.value = data.close;
  }
  parForm.par_min_temp.value = data.min_temp;
  parForm.par_sm_door_temp.value = data.sm_door_temp;
  parForm.open_state.value = data.open_state;
  parForm.weather_cords.value = data.location.lat+", "+data.location.lon
  var div = document.createElement('div')
  for (let [node, value] of Object.entries(d_stat)){
    var checked = (params.auto[node] == 'true' ? true : false)
    div.append(createCheckbox(node,checked))
  }
  auto_checkboxes.innerHTML = ''
  auto_checkboxes.append(div)
  setting_nodes.innerHTML = ''
  for (let [key, value] of Object.entries(data.nodes)){
    setting_nodes.append(createNodeSetInput(key,value))
  }
  this.classList.remove('no-display');
}
parModel.close = function () {this.classList.add('no-display')}
loader.show = function () {
  loader.timeout = setTimeout(() => {loader.classList.remove('no-display')},1000)
}
loader.hide = function () {
  clearTimeout(loader.timeout)
  this.classList.add('no-display')
}
document.getElementById('get_params_btn').onclick = () => parModel.open();
document.getElementById('par_mdl_btn').onclick = () => {
  var e = parForm.elements;
  var auto = {}
  parForm.querySelectorAll('.auto_checkboxes').forEach((item, i) => {
    auto[item.id] = (item.checked ? 'true' : 'false')
  });
  var nds = {}
  setting_nodes.querySelectorAll('.setting_node_div').forEach((item, i) => {
    nds[String(item.querySelector('input[name="node_name"]').value)] = item.querySelector('input[name="node_ip"]').value
  });
  var loc = {}
  var latlon = e.weather_cords.value.split(", ")
  loc.lat = latlon[0]
  loc.lon = latlon[1]
  var obj = {
    min_temp : parseInt(e.par_min_temp.value),
    sm_door_temp: parseInt(e.par_sm_door_temp.value),
    auto: auto,
    nodes : nds,
    location: loc
  };
  if (e.par_chbx_op_tm.value == 'time'){
    if (e.par_open_tm.value.length !== 5) {
      alert("You need to fill out open time");
      return;
    }else {
      obj.open_method = 'time';
      obj.open = e.par_open_tm.value;
    }
  }
  if (e.par_chbx_op_tm.value == 'sun') {
    obj.open_method = 'sun';
    obj.open = e.par_open_sn.value;
  }
  if (e.par_chbx_cl_tm.value == 'time'){
    if (e.par_close_tm.value.length !== 5) {
      alert("You need to fill out close time");
      return;
    }else {
      obj.close_method = 'time';
      obj.close = e.par_close_tm.value;
    }
  }
  if (e.par_chbx_cl_tm.value == 'sun') {
    obj.close_method = 'sun';
    obj.close = e.par_close_sn.value;
  }
  obj.open_state = e.open_state.value;
  put_params(obj);
}
document.getElementById('clx1').onclick = () => parModel.close();
document.getElementById('edit_nodes').onclick = function () {
  this.nextElementSibling.classList.toggle('no-display')
}
document.getElementById('num_of_nodes').onchange = function () {
  var current_nodes = setting_nodes.querySelectorAll('.setting_node_div')
  if (current_nodes.length > this.value) {
    var rn = current_nodes.length - this.value
    for (var i = 0; i < rn; i++) {
      setting_nodes.lastChild.remove()
    }
  }
  if (current_nodes.length < this.value) {
    var rn = this.value - current_nodes.length
    for (var i = 0; i < rn; i++) {
      setting_nodes.append(createNodeSetInput())
    }
  }
}
document.addEventListener('visibilitychange',() => {
  if (document.visibilityState == 'hidden') {
    poll.pause();
  }else {
    poll.paused = false;
    poll.start();
  }
})
window.onclick = (e) => {
  if (e.target == parModel) {parModel.close()}
}
var poll = {
  paused: false,
  start: async function () {
    if (poll.paused) {return}
      await get_conditions();
      update_elements()
      poll.timer = setTimeout(poll.start,5000);
    },
  pause: () => {
    poll.paused = true;
    clearTimeout(poll.timer);
  }
}
async function door_btn_click() {
  var fd = new FormData();
  fd.append('relay',this.relay);
  fd.append('node',this.node);
  fd.append('action',this.action);
  fd.append('method',"move_door");
  loader.show();
  await send_data(fd).then(() => {
    loader.hide();
    this.classList.toggle('btn_active')
    this.action = (this.action == 'close' ? 'open' : 'close')
  });
}
async function send_data(request) {
  return fetch(
      window.location.href+'/api',
      // 'http://10.0.3.133/api',
      {method: 'POST',body: request}
    )
    .then((response) => {return response.json()})
    .catch(() => {return})
}
async function get_params() {
  loader.show();
  var f = new FormData();
  f.append("method","get_params");
  return send_data(f).then(loader.hide());
}
async function put_params(obj) {
  loader.show();
  var f = new FormData();
  f.append('method','put_params');
  f.append('params',JSON.stringify(obj))
  send_data(f).then(() => {parModel.close();loader.hide()});
}
async function get_status() {
  var f = new FormData();
  f.append("method","get_status");
  return send_data(f);
}
async function get_conditions() {
  var status = await get_status();
  if (!status) {
    loader.show()
    return
  }
  loader.hide()
  params = JSON.parse(status.params)
  weather = JSON.parse(status.weather)
  d_stat = JSON.parse(status.d_stat)
  errors = (!status.errors ? '' : status.errors)
  serverTime = status.time
}
function update_elements() {
  document.getElementById('temp_elem').innerText = weather.feels_like;
  document.getElementById('wind_sp_elem').innerText = weather.wind_speed;
  document.getElementById('wind_dir_elem').innerText = weather.wind_dir;
  document.getElementById('rain_elem').innerText = (weather.rain == 'true' ? "Yes": "No");
  document.getElementById('time_elem').innerText = serverTime;
  document.getElementById('error_message').innerText = errors;
  for (let [node, state] of Object.entries(d_stat)){
    var element = document.getElementById(node+'fieldset')
    if ((!state && !element.not_online) || (element.not_online && state)) {
      createAllNodes()
      return update_elements()
    }
    if (!state) {continue}
    if (params.auto[node] == "true") {
      element.classList.add('in_auto')
    }else {
      element.classList.remove('in_auto')
    }
    state.forEach((item, i) => {
      var el = document.getElementById(node+i);
      if (item == 'on') {
        el.classList.add("btn_active");
        el.action = 'close'
      }else {
        el.classList.remove('btn_active');
        el.action = 'open'
      }
    });
  }
  var d = new Date();
  document.getElementById('last_time').innerText = d.toLocaleTimeString();
}
function createCheckbox(name, checked) {
  var div = document.createElement('div')
  var label = document.createElement('label')
  var input = document.createElement('input')
  div.classList.add('row')
  input.type = 'checkbox'
  input.id = name
  input.checked = checked
  input.classList.add('auto_checkboxes')
  label.htmlFor = name
  label.innerText = name.charAt(0).toUpperCase()+name.substring(1)
  div.append(label,input)
  return div
}
function createNodeFieldset(node,online) {
  var fieldset = document.createElement('fieldset')
  var legend = document.createElement('legend')
  fieldset.classList.add('btn_fieldset')
  fieldset.id = node+'fieldset'
  legend.classList.add('btn_legend')
  legend.innerText = node
  fieldset.append(legend)
  if (!online) {
    var p = document.createElement('p')
    p.innerText = 'Node not online..'
    fieldset.append(p)
    fieldset.not_online = true
  }else {
    fieldset.append(createBtn('Main',node,0),createBtn('Small',node,1))
  }
  var span = document.createElement('span')
  span.classList.add('auto_span')
  span.innerText = 'Auto'
  fieldset.append(span)
  return fieldset
}
function createBtn(name,node,relay) {
  var btn = document.createElement('button')
  btn.classList.add('btn_light','dbtn')
  btn.innerText = name
  btn.onclick = door_btn_click
  btn.action = 'close'
  btn.relay = relay
  btn.node = node.replace('node','')
  btn.id = node+relay
  return btn
}
function createAllNodes() {
  var div = document.createElement('div')
  for (let [key, value] of Object.entries(d_stat)){
    div.append(createNodeFieldset(key,value))
  }
  door_btn_div.innerHTML = ''
  door_btn_div.append(div)
}
function createNodeSetInput(name,ip) {
  var node_name = document.createElement('input')
  var node_ip = document.createElement('input')
  var div = document.createElement('div')
  div.name = 'node_set_div'
  div.classList.add('setting_node_div')
  node_name.type = 'text'
  node_name.name = 'node_name'
  node_ip.type = 'text'
  node_ip.name = 'node_ip'
  if (name) {
    node_name.value = name
    node_ip.value = ip
  }else {
    node_name.placeholder = 'Node name'
    node_ip.placeholder = 'Node ip'
  }
  div.append(node_name,node_ip)
  return div
}
async function init() {
  await get_conditions()
  createAllNodes()
  update_elements()
  poll.start()
}
document.addEventListener('DOMContentLoaded',init)
