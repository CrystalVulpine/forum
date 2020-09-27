function expandReply(e) {
	e.onclick = null;
	let comment = e.parentNode.parentNode;
	comment.innerHTML += '<form id="comment-' + comment.id + '" action="/api/comment" method="post"><input type="text" name="body" placeholder="Comment" class="search-bar" maxlength="10000"><input type="hidden" name="post" value="{{ p.id }}"><input type="hidden" name="parent" value="' + comment.id + '"><input type="hidden" name="community" value="{{ c.id if c else 0 }}"><a onclick="document.getElementById(\'comment-' + comment.id + '\').submit()" class="submit-button" href="javascript:void(0)" style="margin-right:-15px">Submit</a><a onclick="document.getElementById(\'comment-' + comment.id + '\').outerHTML = '';let rbutton = document.getElementById(' + comment.id + ').getElementsByClassName(\'reply-button\')[0];rbutton.onclick=\"expandReply(this)\"" class="submit-button" href="javascript:void(0)" style="margin-right:-15px">Cancel</a></form>';
}

function updateTimestamps() {
	let timestamps = document.getElementsByClassName('timestamp');
	let now = Math.floor(Date.now() / 1000);
	for (const stamp of timestamps) {
		let age = Math.floor(now - (Date.parse(stamp.getAttribute('datetime')) / 1000));
		if (age < 60) {
			stamp.innerHTML = "just now";
		} else if (age < 3600) {
			let minutes = Math.floor(age / 60);
			if (minutes == 1) {
				stamp.innerHTML = "1 minute ago";
			} else {
				stamp.innerHTML = minutes + " minutes ago";
			}
		} else if (age < 86400) {
			let hours = Math.floor(age / 3600);
			if (hours == 1) {
				stamp.innerHTML = "1 hour ago";
			} else {
				stamp.innerHTML = hours + " hours ago";
			}
		} else if (age < 2592000) {
			let days = Math.floor(age / 86400);
			if (days == 1) {
				stamp.innerHTML = "1 day ago";
			} else {
				stamp.innerHTML = days + " days ago";
			}
		} else if (age < 31536000) {
			let months = Math.floor(age / 2592000);
			if (months == 1) {
				stamp.innerHTML = "1 month ago";
			} else {
				stamp.innerHTML = months + " months ago";
			}
		} else {
			let years = Math.floor(age / 31536000);
			if (years == 1) {
				stamp.innerHTML = "1 year ago";
			} else {
				stamp.innerHTML = years + " years ago";
			}
		}
	}
}

updateTimestamps();
setInterval(updateTimestamps, 1000);
