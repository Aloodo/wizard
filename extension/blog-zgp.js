function doDialog() {
	if(confirm("Your quest has succeeded, O mighty wizard! You may get your new spell now.")) {
		window.location = "https://wizard.aloodo.org/";
	}
}

function checkMessage() {
	var ps = document.querySelectorAll("p");
	for (var i = 0; i < ps.length; i++) {
		if ("You have opted out of the sale of your personal information." == ps[i].textContent) {
			doDialog();
			break;
		}
	}
}

window.addEventListener("load", checkMessage, false);
