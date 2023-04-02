document.addEventListener("DOMContentLoaded", function () {
	// Use buttons to toggle between views
	document
		.querySelector("#inbox")
		.addEventListener("click", () => load_mailbox("inbox"));
	document
		.querySelector("#sent")
		.addEventListener("click", () => load_mailbox("sent"));
	document
		.querySelector("#archived")
		.addEventListener("click", () => load_mailbox("archive"));
	document
		.querySelector("#compose")
		.addEventListener("click", () => compose_email());
	document
		.querySelector("#compose-form")
		.addEventListener("submit", send_email);

	// By default, load the inbox
	load_mailbox("inbox");
});

function compose_email(send_to = "", subject = "", body = "") {
	// Show compose view and hide other views
	document.querySelector("#emails-view").style.display = "none";
	document.querySelector("#email-view").style.display = "none";
	document.querySelector("#compose-view").style.display = "block";

	// Clear out composition fields
	document.querySelector("#compose-recipients").value = send_to;
	document.querySelector("#compose-subject").value = subject;
	document.querySelector("#compose-body").value = body;
}

function load_mailbox(mailbox) {
	// Show the mailbox and hide other views
	document.querySelector("#emails-view").style.display = "block";
	document.querySelector("#email-view").style.display = "none";
	document.querySelector("#compose-view").style.display = "none";

	// Show the mailbox name
	document.querySelector("#emails-view").innerHTML = `<h3>${
		mailbox.charAt(0).toUpperCase() + mailbox.slice(1)
	}</h3>`;

	// fetch the emails for the selected box
	fetch(`/emails/${mailbox}`)
		.then((response) => response.json())
		.then((emails) => {
			// iterate the emails and create divs for each
			emails.forEach((email) => {
				const element = document.createElement("div");

				// different background for read/unread
				element.style.cssText = "border-bottom-style: solid";
				if (email.read) {
					element.style.cssText = "background-color: grey";
				}
				element.innerHTML = `${email.sender} Subject: ${email.subject} Time: ${email.timestamp}`;

				// clicking on an email fetches it
				element.addEventListener("click", function () {
					load_email(email);
				});
				document.querySelector("#emails-view").append(element);
			});
		});
}

function send_email(event) {
	event.preventDefault();

	fetch("/emails", {
		method: "POST",
		body: JSON.stringify({
			recipients: document.querySelector("#compose-recipients").value,
			subject: document.querySelector("#compose-subject").value,
			body: document.querySelector("#compose-body").value,
		}),
	}).then(() => load_mailbox("inbox"));
}

function load_email(email) {
	// show the email and hid other views
	document.querySelector("#emails-view").style.display = "none";
	document.querySelector("#email-view").style.display = "block";
	document.querySelector("#compose-view").style.display = "none";

	// clear out any previous email views
	document.querySelector("#email-view").innerHTML = "";

	// fetch the email
	fetch(`/emails/${email.id}`)
		.then((response) => response.json())
		.then((email) => {
			// create elements for email
			const sender = document.createElement("div");
			const recipients = document.createElement("div");
			const subject = document.createElement("div");
			const timestamp = document.createElement("div");
			const body = document.createElement("div");

			// add content to elements
			sender.innerHTML = `Sender: ${email.sender}`;
			recipients.innerHTML = `Recipients: ${email.recipients}`;
			subject.innerHTML = `Subject: ${email.subject}`;
			timestamp.innerHTML = `Timestamp: ${email.timestamp}`;
			body.innerHTML = `${email.body}`;

			//style
			body.style.cssText = "border-top: solid;";

			// add it all to the document
			document
				.querySelector("#email-view")
				.append(sender, recipients, timestamp, subject, body);

			// add an archive/unarchive button based on whether email is currently archived
			const btn = document.createElement("button");
			if (email.archived) {
				btn.innerHTML = "Unarchive";
				btn.addEventListener("click", () => {
					fetch(`emails/${email.id}`, {
						method: "PUT",
						body: JSON.stringify({
							archived: false,
						}),
					}).then(() => load_mailbox("inbox"));
				});
			} else {
				btn.innerHTML = "Archive";
				btn.addEventListener("click", () => {
					fetch(`emails/${email.id}`, {
						method: "PUT",
						body: JSON.stringify({
							archived: true,
						}),
					}).then(() => load_mailbox("inbox"));
				});
			}
			document.querySelector("#email-view").append(btn);

			// add reply button
			const reply = document.createElement("button");
			reply.innerHTML = "Reply";
			reply.addEventListener("click", () =>
				compose_email(
					email.sender,
					`Re: ${email.subject}`,
					`On ${email.timestamp}, ${email.sender} wrote: ${email.body}\n`
				)
			);
			document.querySelector("#email-view").append(reply);
		});

	// mark email as read
	fetch(`/emails/${email.id}`, {
		method: "PUT",
		body: JSON.stringify({
			read: true,
		}),
	});
}
