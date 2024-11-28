let socket = io()
addEventListener("pageshow", () => {
	socket.disconnect();
	socket.connect();
});


function formatHourMinute(d) {
	return d.toLocaleTimeString([], {timeStyle: 'short'})
}
for (const e of document.querySelectorAll('[data-time]')) {
	e.innerHTML = formatHourMinute(new Date(e.dataset.time*1000));
};

const ua = window.navigator.userAgent

const chat = document.getElementById('chat')
const chat_id = document.getElementById('chat_id').value
const chatline = document.getElementsByClassName('chat-line')[0]
const box = document.getElementById('chat-window')
const ta = document.getElementById('input-text-chat')
const image_preview = document.getElementById('image-preview')

const vid = document.getElementById('vid').value
const slurreplacer = document.getElementById('slurreplacer').value

let is_typing = false;

const blocked_user_ids = document.getElementById('blocked_user_ids').value.split(', ')

const group_names = document.getElementById('group_names').value.replaceAll(', ', '|').replaceAll("'", "")
const group_names_pattern = String.raw`(\s|^)!(` + group_names + String.raw`)(\s|$)`

let keyword_notifs_li = document.getElementById('keyword_notifs_li')
let keyword_notifs_pattern
if (keyword_notifs_li) {
	keyword_notifs_li = keyword_notifs_li.value.replaceAll(', ', '|').replaceAll("'", "")
	keyword_notifs_pattern = String.raw`(\s|^)(` + keyword_notifs_li + String.raw`)(\s|$)`
}

let scrolled_down_var = true;
function scrolled_down() {
	scrolled_down_var = box.scrollHeight - box.scrollTop <= innerHeight
	return scrolled_down_var
}

socket.on('speak', function(json) {
	if (location.href.includes('?m=')) {
		return
	}
	
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
	if (json.user_id != vid && (text_html.includes(`<a href="/id/${vid}"`) || text.match(group_names_pattern) || (keyword_notifs_pattern && text.toLowerCase().match(keyword_notifs_pattern)))) {
		chatline.classList.add('chat-mention');
	}

	if (json.user_id != vid) {
		notifs += 1;
		if (notifs == 1) {
			flash();
		}
	}

	const users = document.getElementsByClassName('user_id');
	const last_user = users[users.length-1].value;

	const msgs = document.getElementsByClassName('chat-line')
	const last_timestamp = msgs[msgs.length-1].dataset.msgTime;

	const make_new_chatgroup = (last_user != json.user_id || json.created_utc - last_timestamp > 600)

	if (make_new_chatgroup) {
		document.getElementsByClassName('avatar-pic')[0].src = '/pp/' + json.user_id

		if (json.hat)
			document.getElementsByClassName('avatar-hat')[0].src = json.hat + "?h=8"
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

		if (json.pride_username)
			username.setAttribute("pride_username", "")
		else
			username.removeAttribute("pride_username")

		document.getElementsByClassName('user_id')[0].value = json.user_id

		document.getElementsByClassName('time')[0].innerHTML = formatHourMinute(new Date(json.created_utc*1000))

		document.getElementsByClassName('link')[0].href = `/chat/${chat_id}?m=${json.id}#${json.id}`
		document.getElementsByClassName('link')[0].innerHTML = `#${json.id}`
	}

	document.getElementsByClassName('chat-line')[0].id = json.id
	document.getElementsByClassName('chat-line')[0].dataset.msgTime = json.created_utc
	document.getElementsByClassName('text')[0].innerHTML = escapeHTML(text)
	document.getElementsByClassName('chat-message')[0].innerHTML = text_html.replace(/data-src/g, 'src').replace(/data-cfsrc/g, 'src').replace(/style="display:none;visibility:hidden;"/g, '').replace(/ loading="lazy"/g, '')

	document.getElementsByClassName('quotes')[0].classList.add("d-none")
	if (json.quotes) {
		const quoted = document.getElementById(json.quotes)
		if (quoted) {
			const quoted_user = quoted.parentElement.querySelector('.user_id').value
			if (quoted_user == vid) {
				chatline.classList.add('chat-mention');
			}
			document.getElementsByClassName('quotes')[0].classList.remove("d-none")
			document.getElementsByClassName('QuotedMessageLink')[0].href = '#' + json.quotes
			document.getElementsByClassName('QuotedUser')[0].innerHTML = quoted.parentElement.querySelector('.userlink').textContent.trim()
			document.getElementsByClassName('QuotedMessage')[0].innerHTML = quoted.querySelector('.text').innerHTML
		}
	}

	let line = document.getElementsByClassName('chat-line')[0].cloneNode(true)
	register_new_elements(line);
	bs_trigger(line)

	if (scrolled_down_var) {
		for (img of line.getElementsByClassName('img')) {
			img.addEventListener("load", () => {
				box.scrollTo(0, box.scrollHeight)
			}, {once : true});
		}
	}

	if (!make_new_chatgroup) {
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

	if (scrolled_down_var && document.getElementsByClassName('chat-message').length > 250) {
		document.getElementById('chat-window').firstElementChild.remove()
		document.getElementById('chat-window').firstElementChild.remove()
	}

	if (scrolled_down_var)
		box.scrollTo(0, box.scrollHeight)

	embed_sites()
})

socket.on('error', function(message) {
	showToast(false, message);
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
			"file_type": sending ? sending.type : '',
			"chat_id": document.getElementById('chat_id').value,
		});
		ta.value = ''
		is_typing = false
		socket.emit('typing', false);
		autoExpand(ta);
		document.getElementById("quotes").classList.add("d-none")
		document.getElementById('quotes_id').value = null;
		oldfiles[ta.id] = new DataTransfer();
		input.value = null;

		input.previousElementSibling.className  = "fas fa-file";
		input.previousElementSibling.textContent = "";
	}

	image_preview.classList.add('d-none');
	image_preview.classList.remove('mr-2');
}


function quote(t) {
	document.getElementById("quotes").classList.remove("d-none")

	const text = t.parentElement.parentElement.getElementsByClassName("text")[0].innerHTML.replace(/\*/g,"\\*").split('\n').pop()
	document.getElementById('QuotedMessage').innerHTML = text

	const username = t.parentElement.parentElement.parentElement.parentElement.parentElement.getElementsByClassName('userlink')[0].textContent
	document.getElementById('QuotedUser').innerHTML = username.trim()

	const id = t.parentElement.parentElement.parentElement.parentElement.id
	document.getElementById('quotes_id').value = id
	document.getElementById('QuotedMessageLink').href = `#${id}`

	ta.focus()

	if (scrolled_down_var) {
		box.scrollTo(0, box.scrollHeight)
		setTimeout(function() {
			box.scrollTo(0, box.scrollHeight)
		}, 40);
	}
}

ta.addEventListener("keydown", function(e) {
	if (e.key === 'Enter' && !e.shiftKey && inline_carot_modal.style.display == 'none') {
		e.preventDefault();
		send();
	}
})

socket.on('online', function(data) {
	const online_li = data[0]
	if (chat_id != 1) {
		for (const marker of document.getElementsByClassName('online-marker')) {
			marker.classList.add('d-none')
		}
		for (const u of online_li) {
			for (const marker of document.getElementsByClassName(`online-marker-${u[4]}`)) {
				marker.classList.remove('d-none')
				marker.parentElement.parentElement.insertBefore(marker.parentElement, marker.parentElement.parentElement.firstChild);
			}
		}
		return
	}

	const muted_li = Object.keys(data[1])

	for (const el of document.getElementsByClassName('chat-count')) {
		el.innerHTML = online_li.length
	}
	document.getElementById('chat-count-header-bar').innerHTML = online_li.length
	let online = ''
	for (const u of online_li)
	{
		let patron = ''
		if (u[3])
			patron += ` class="patron chat-patron" style="background-color:#${u[2]}"`
		if (u[5])
			patron += " pride_username"

		online += `<li>`
		if (muted_li.includes(u[1].toLowerCase()))
			online += '<b class="text-danger muted" data-bs-toggle="tooltip" title="Muted">X</b> '
		online += `<a class="font-weight-bold" target="_blank" href="/@${u[1]}" style="color:#${u[2]}"><img loading="lazy" class="mr-1" src="/pp/${u[4]}"> <span${patron}>${u[1]}</span></a><i class="ml-2 text-smaller text-success fas fa-circle"></i></li>`
	}

	const online_el = document.getElementById('online')
	if (online_el) {
		online_el.innerHTML = online
		bs_trigger(online_el)
	}

	document.getElementById('online3').innerHTML = online
	bs_trigger(document.getElementById('online3'))
})

socket.on('add', function(added_li) {
	let added_html = ''
	for (const u of added_li)
	{
		let patron = ''
		if (u[3])
			patron += ` class="patron chat-patron" style="background-color:#${u[1]}"`
		if (u[5])
			patron += " pride_username"

		added_html += `<li class="user-${u[3]}"><a class="font-weight-bold" target="_blank" href="/@${u[0]}" style="color:#${u[1]}"><img loading="lazy" class="mr-1" src="/pp/${u[3]}"> <span${patron}>${u[0]}</span></a></li>`
	}

	for (const el of document.getElementsByClassName('members')) {
		el.insertAdjacentHTML('afterbegin', added_html);
	}
})

socket.on('kick', function(kicked_li) {
	for (const uid of kicked_li)
	{
		for (const el of document.querySelectorAll(`.user-${uid}`)) {
			el.remove()
		}
	}
})


let timer_id;
function remove_typing() {
	is_typing = false;
	socket.emit('typing', false);
}

ta.addEventListener("input", function() {
	text = ta.value
	if (!text && is_typing) {
		is_typing = false;
		socket.emit('typing', false);
	}
	else if (text && !is_typing) {
		is_typing = true;
		socket.emit('typing', true);
		clearTimeout(timer_id)
		timer_id = setTimeout(remove_typing, 2000);
	}
})


socket.on('typing', function(users) {
	if (users.length==0) {
		document.getElementById('typing-indicator').innerHTML = '';
	}
	else if (users.length==1) {
		document.getElementById('typing-indicator').innerHTML = '<b>'+users[0]+"</b> is typing...";
	}
	else if (users.length==2) {
		document.getElementById('typing-indicator').innerHTML = '<b>'+users[0]+"</b> and <b>"+users[1]+"</b> are typing...";
	}
	else {
		document.getElementById('typing-indicator').innerHTML = '<b>'+users[0]+"</b>, <b>"+users[1]+"</b>, and <b>"+users[2]+"</b> are typing...";
	}
})


function del(t) {
	const chatline = t.parentElement.parentElement.parentElement.parentElement
	socket.emit('delete', chatline.id);
	chatline.remove()
}

socket.on('delete', function(text) {
	const text_spans = document.getElementsByClassName('text')
	for (const span of text_spans) {
		if (span.innerHTML == text)
		{
			span.parentElement.parentElement.parentElement.parentElement.parentElement.remove()
		}
	}
})

socket.on('refresh_chat', () => {
	setTimeout(function() {
		location.reload()
	}, 1000);
})

document.addEventListener('click', function(e) {
	if (e.target.id == "cancel") {
		document.getElementById("quotes").classList.add("d-none");
		document.getElementById('quotes_id').value = null;
	}
});


const input = document.getElementById('file')
function handle_files() {
	if (!input.files.length) return
	if (check_file_size(input, input.files[0])) {
		const char_limit = innerWidth >= 768 ? 50 : 15;
		input.previousElementSibling.className  = "";
		input.previousElementSibling.textContent = input.files[0].name.substr(0, char_limit);

		if (input.files[0].type.startsWith('image/')) {
			const fileReader = new FileReader();
			fileReader.readAsDataURL(input.files[0]);
			fileReader.onload = function() {
				image_preview.setAttribute('src', this.result);
				image_preview.classList.remove('d-none');
				image_preview.classList.add('mr-2');
				image_preview.addEventListener('load', () => {
					box.scrollTo(0, box.scrollHeight)
				})
			};
		}
		else {
			image_preview.classList.add('d-none');
			image_preview.classList.remove('mr-2');
		}
	}
	ta.focus()
}

input.onchange = handle_files

document.onpaste = function(event) {
	files = structuredClone(event.clipboardData.files);
	if (!files.length) return
	input.files = files
	handle_files()
}

function send_hearbeat() {
	socket.emit('heartbeat')
}
send_hearbeat()
setInterval(send_hearbeat, 20000);

addEventListener("DOMContentLoaded", () => {
	box.scrollTo(0, box.scrollHeight)
})

visualViewport.addEventListener('resize', () => {
	if (scrolled_down_var)
		box.scrollTo(0, box.scrollHeight)
});

const observer = new ResizeObserver(function() {
	if (scrolled_down_var) {
		box.scrollTo(0, box.scrollHeight)
	}
});
for (const child of box.children) {
	observer.observe(child);
}

box.addEventListener("scroll", () => {
	scrolled_down()
});
