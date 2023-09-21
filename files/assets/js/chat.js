function formatDate(d) {
	const hour = ("0" + d.getHours()).slice(-2);
	const minute = ("0" + d.getMinutes()).slice(-2);
	const second = ("0" + d.getSeconds()).slice(-2);
	return hour + ":" + minute + ":" + second;
}

for (const e of timestamps) {
	e.innerHTML = formatDate(new Date(e.dataset.time*1000));
};

const ua=window.navigator.userAgent
let socket

socket=io()

const chatline = document.getElementsByClassName('chat-line')[0]
const box = document.getElementById('chat-window')
const ta = document.getElementById('input-text')
const icon = document.querySelector("link[rel~='icon']")

const vid = document.getElementById('vid').value
const site_name = document.getElementById('site_name').value
const slurreplacer = document.getElementById('slurreplacer').value

let notifs = 0;
let focused = true;
let is_typing = false;
let alert=true;

const page_title = document.getElementsByTagName('title')[0].innerHTML;

function flash(){
	let title = document.getElementsByTagName('title')[0]
	if (notifs >= 1 && !focused){
		title.innerHTML = `[+${notifs}] ${page_title}`;
		if (alert) {
			icon.href = `/i/${site_name}/alert.ico?v=3009`
			alert=false;
		}
		else {
			icon.href = `/i/${site_name}/icon.webp?x=6`
			alert=true;
		}
		setTimeout(flash, 500)
	}
	else {
		icon.href = `/i/${site_name}/icon.webp?x=6`
		notifs = 0
		title.innerHTML = page_title;
	}

	if (is_typing) {
		is_typing = false
		socket.emit('typing', false);
	}
}


const blocked_user_ids = document.getElementById('blocked_user_ids').value.split(', ')

socket.on('speak', function(json) {
	if (blocked_user_ids.includes(json.user_id.toString())) {
		return
	}

	let text
	let text_html

	if (slurreplacer != '0') {
		text = json.text_censored
		text_html = json.text_html_censored
	}
	else {
		text = json.text
		text_html = json.text_html
	}

	chatline.classList.remove('chat-mention');
	if (text_html.includes(`<a href="/id/${vid}"`)){
		chatline.classList.add('chat-mention');
	}

	notifs = notifs + 1;
	if (notifs == 1) {
		setTimeout(flash, 500);
	}

	const users = document.getElementsByClassName('user_id');
	const last_user = users[users.length-1].value;
	const scrolled_down = (box.scrollHeight - box.scrollTop <= window.innerHeight)

	if (last_user != json.user_id) {
		document.getElementsByClassName('avatar-pic')[0].src = '/pp/' + json.user_id

		if (json.hat)
			document.getElementsByClassName('avatar-hat')[0].src = json.hat + "?h=7"
		else
			document.getElementsByClassName('avatar-hat')[0].removeAttribute("src")

		const userlink = document.getElementsByClassName('userlink')[0]

		userlink.href = '/@' + json.username
		userlink.style.color = '#' + json.namecolor

		const username = document.getElementsByClassName('username')[0]
		username.textContent = json.username
		if (json.patron) {
			username.classList.add('patron')
			username.style.backgroundColor = '#' + json.namecolor
		}
		else {
			username.classList.remove('patron')
			username.style.backgroundColor = null
		}

		document.getElementsByClassName('user_id')[0].value = json.user_id

		document.getElementsByClassName('time')[0].innerHTML = formatDate(new Date(json.time*1000))
	}

	document.getElementsByClassName('chat-line')[0].id = json.id
	document.getElementsByClassName('text')[0].innerHTML = escapeHTML(text)
	document.getElementsByClassName('chat-message')[0].innerHTML = text_html.replace(/data-src/g, 'src').replace(/data-cfsrc/g, 'src').replace(/style="display:none;visibility:hidden;"/g, '').replace(/ loading="lazy"/g, '')

	document.getElementsByClassName('quotes')[0].classList.add("d-none")
	if (json.quotes) {
		const quoted = document.getElementById(json.quotes)
		if (quoted) {
			const quoted_user = quoted.parentElement.querySelector('.user_id').value
			if (quoted_user == vid){
				chatline.classList.add('chat-mention');
			}
			document.getElementsByClassName('quotes')[0].classList.remove("d-none")
			document.getElementsByClassName('QuotedMessageLink')[0].href = '#' + json.quotes
			document.getElementsByClassName('QuotedUser')[0].innerHTML = quoted.parentElement.querySelector('.userlink').textContent
			document.getElementsByClassName('QuotedMessage')[0].innerHTML = quoted.querySelector('.text').innerHTML
		}
	}

	let line = document.getElementsByClassName('chat-line')[0].cloneNode(true)
	register_new_elements(line);
	bs_trigger(line)
	if (last_user == json.user_id) {
		box.querySelector('.chat-group:last-child').append(line)
	}
	else {
		const chatgroup = document.getElementsByClassName('chat-group')[0].cloneNode(true)
		chatgroup.append(line)
		box.append(chatgroup)
	}

	const line2 = document.getElementById(json.id)
	register_new_elements(line2);
	bs_trigger(line2)

	if (scrolled_down || json.user_id == vid) {
		box.scrollTo(0, box.scrollHeight)
		setTimeout(function () {
			box.scrollTo(0, box.scrollHeight)
		}, 200);
		setTimeout(function () {
			box.scrollTo(0, box.scrollHeight)
		}, 500);
	}
})

function send() {
	const text = ta.value.trim();
	const input = document.getElementById('file');
	const files = input.files;
	if (text || files)
	{
		let sending;
		if (files[0]) sending = files[0]
		else sending = ''
		socket.emit('speak', {
			"message": text,
			"quotes": document.getElementById('quotes_id').value,
			"file": sending,
		});
		ta.value = ''
		is_typing = false
		socket.emit('typing', false);
		autoExpand(ta);
		document.getElementById("quotes").classList.add("d-none")
		document.getElementById('quotes_id').value = null;
		oldfiles[ta.id] = new DataTransfer();
		input.value = null;
		input.previousElementSibling.innerHTML = '<i class="fas fa-image" style="font-size:1.3rem!important"></i>'

		box.scrollTo(0, box.scrollHeight);
		setTimeout(function () {
			box.scrollTo(0, box.scrollHeight)
		}, 200);
		setTimeout(function () {
			box.scrollTo(0, box.scrollHeight)
		}, 500);
	}
}


function quote(t) {
	document.getElementById("quotes").classList.remove("d-none")

	const text = t.parentElement.parentElement.getElementsByClassName("text")[0].innerHTML.replace(/\*/g,"\\*").split('\n').pop()
	document.getElementById('QuotedMessage').innerHTML = text

	const username = t.parentElement.parentElement.parentElement.parentElement.parentElement.getElementsByClassName('userlink')[0].textContent
	document.getElementById('QuotedUser').innerHTML = username

	const id = t.parentElement.parentElement.parentElement.parentElement.id
	document.getElementById('quotes_id').value = id
	document.getElementById('QuotedMessageLink').href = `#${id}`

	ta.focus()
}

ta.addEventListener("keydown", function(e) {
	if (e.key === 'Enter' && !current_word) {
		e.preventDefault();
		send();
	}
})

socket.on('online', function(data){
	document.getElementsByClassName('board-chat-count')[0].innerHTML = data[0].length
	document.getElementById('chat-count-header-bar').innerHTML = data[0].length
	const admin_level = parseInt(document.getElementById('admin_level').value)
	let online = ''
	let online2 = '<b>Users Online</b>'
	for (const u of data[0])
	{
		let patron = ''
		if (u[3])
			patron = ` class="patron" style="background-color:#${u[2]}"`

		online += `<li>`
		if (admin_level && Object.keys(data[1]).includes(u[0].toLowerCase()))
			online += '<b class="text-danger muted" data-bs-toggle="tooltip" title="Muted">X</b> '
		online += `<a class="font-weight-bold" target="_blank" href="/@${u[0]}" style="color:#${u[2]}"><img loading="lazy" class="mr-1" src="/pp/${u[1]}"><span${patron}>${u[0]}</span></a></li>`
		online2 += `<br>@${u[0]}`
	}

	const online_el = document.getElementById('online')
	if (online_el) {
		online_el.innerHTML = online
		bs_trigger(online_el)
	}

	document.getElementById('online2').setAttribute("data-bs-original-title", online2);
	document.getElementById('online3').innerHTML = online
	bs_trigger(document.getElementById('online3'))
})

addEventListener('blur', function(){
	focused = false
})
addEventListener('focus', function(){
	focused = true
})

let timer_id;
function remove_typing() {
	is_typing = false;
	socket.emit('typing', false);
}

ta.addEventListener("input", function() {
	clearTimeout(timer_id)

	text = ta.value
	if (!text && is_typing){
		is_typing = false;
		socket.emit('typing', false);
	}
	else if (text && !is_typing) {
		is_typing = true;
		socket.emit('typing', true);
		timer_id = setTimeout(remove_typing, 2000);
	}
})


socket.on('typing', function (users){
	if (users.length==0){
		document.getElementById('typing-indicator').innerHTML = '';
		document.getElementById('loading-indicator').classList.add('d-none');
	}
	else if (users.length==1){
		document.getElementById('typing-indicator').innerHTML = '<b>'+users[0]+"</b> is typing...";
		document.getElementById('loading-indicator').classList.remove('d-none');
	}
	else if (users.length==2){
		document.getElementById('typing-indicator').innerHTML = '<b>'+users[0]+"</b> and <b>"+users[1]+"</b> are typing...";
		document.getElementById('loading-indicator').classList.remove('d-none');
	}
	else {
		document.getElementById('typing-indicator').innerHTML = '<b>'+users[0]+"</b>, <b>"+users[1]+"</b>, and <b>"+users[2]+"</b> are typing...";
		document.getElementById('loading-indicator').classList.remove('d-none');
	}
})


function del(t) {
	const chatline = t.parentElement.parentElement.parentElement.parentElement
	socket.emit('delete', chatline.id);
	chatline.remove()
}

socket.on('delete', function(text) {
	const text_spans = document.getElementsByClassName('text')
	for(const span of text_spans) {
		if (span.innerHTML == text)
		{
			span.parentElement.parentElement.parentElement.parentElement.parentElement.remove()
		}
	}
})

document.addEventListener('click', function (e) {
	if (e.target.classList.contains('delconfirm')) {
		e.target.nextElementSibling.classList.remove('d-none');
		e.target.classList.add('d-none');
	}
	else {
		for (const btn of document.querySelectorAll('.delmsg:not(.d-none)')) {
			btn.classList.add('d-none');
			btn.previousElementSibling.classList.remove('d-none');
		}
	}

	if (e.target.id == "cancel") {
		document.getElementById("quotes").classList.add("d-none");
		document.getElementById('quotes_id').value = null;
	}
});


const input = document.getElementById('file')
function handle_files() {
	if (!input.files.length) return
	const char_limit = screen_width >= 768 ? 50 : 5;
	input.previousElementSibling.textContent = input.files[0].name.substr(0, char_limit);
}

input.onchange = handle_files

document.onpaste = function(event) {
	input.files = structuredClone(event.clipboardData.files);
	handle_files()
}

box.scrollTo(0, box.scrollHeight)
setTimeout(function () {
	box.scrollTo(0, box.scrollHeight)
}, 200);
setTimeout(function () {
	box.scrollTo(0, box.scrollHeight)
}, 500);
setTimeout(function () {
	box.scrollTo(0, box.scrollHeight)
}, 1000);
setTimeout(function () {
	box.scrollTo(0, box.scrollHeight)
}, 1500);
document.addEventListener('DOMContentLoaded', function () {
	box.scrollTo(0, box.scrollHeight)
});

if (location.pathname == '/orgy') {
	const now = new Date();
	const day_of_week = now.getUTCDay()

	if (day_of_week == 5 || day_of_week == 7) {
		let hour
		if (day_of_week == 5) hour = 0
		else hour = 20

		let millis = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), hour, 0, 10) - now;
		if (millis < 0)
			millis += 86400000;

		const minutes = Math.round(millis/1000/60*10)/10
		console.log(`Refreshing page in ${minutes} minutes`)
		setTimeout(() => location.reload(), millis);
	}
}
