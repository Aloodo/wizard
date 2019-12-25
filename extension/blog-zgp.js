var host = "http://localhost:5000";
// var host = "https://wizard.aloodo.org/";

function doDialog() {
	if(confirm("Your quest has succeeded, O mighty wizard! You may obtain your new spell now.")) {
		window.location = host + '/add-spell?url=' + encodeURI(window.location);
	}
}

function checkMessage() {
	var ps = document.querySelectorAll("p");
	for (var i = 0; i < ps.length; i++) {
		console.log(ps[i]);
		if ("You have opted out of the sale of your personal information." == ps[i].textContent) {
			doDialog();
			break;
		}
	}
}

checkMessage();

