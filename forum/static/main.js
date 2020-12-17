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

function signupButton(form) {
	if (form["password"].value !== form["password2"].value) {
		document.getElementById('passwords-mismatch').style = "color:red";
		return;
	}
	form.submit();
}

updateTimestamps();
setInterval(updateTimestamps, 1000);
