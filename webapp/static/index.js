function cleanSession()
{
	fetch("/clean-session",{
		method: "POST",
		body: JSON.stringify(),
	})
	.catch(error => {
		console.log('Error!');
		console.error(error);
	});
}

function cleanForm()
{
	var form = document.getElementById("transaction_form");
	var items_table = document.getElementById("items_table")
	var row_count = items_table.tBodies[0].rows.length;
	var balance_cell = document.getElementById("items_table").getElementsByTagName('tfoot')[0].rows[0].cells[1];

	form.reset();
	for (let i = 0; i < row_count; i++){
		items_table.deleteRow(1);
	}
	balance_cell.innerHTML = "$0.00";
}

function newTransaction()
{
	var form = document.getElementById("transaction_form");
	var new_btn = document.getElementById("new_button");
	var cancel_btn = document.getElementById("cancel_button");
	cleanSession();
	cleanForm();
	form.hidden = false;
	cancel_btn.hidden = false;
	new_btn.hidden = true;
}

function cancelTransaction()
{
	var form = document.getElementById("transaction_form");
	var new_btn = document.getElementById("new_button");
	var cancel_btn = document.getElementById("cancel_button");
	form.hidden = true;
	cancel_btn.hidden = true;
	new_btn.hidden = false;
	cleanSession();
	cleanForm();
}

function deleteItem(rowId)
{
	fetch("/delete-item", {
		method:	"POST",
		body: JSON.stringify({rowId: rowId}),
	})
	.then(response => response.json())
	.then(json => printTable(json))
	.catch(error => {
		console.log("Error!");
		console.error(error);
	});
}

function addItem(){
	var serviceId = document.getElementById("input_service").value;
	var subserviceId = document.getElementById("input_subservice").value;
	var total = document.getElementById("total").value;

	fetch("/add-item", {
		method: "POST",
		body: JSON.stringify({serviceId: serviceId, subserviceId: subserviceId, total: total}),
	})
	.then(response => response.json())
    .then(json => printTable(json))
	.catch(error => {
		console.log('Error!');
		console.error(error);
	  });
}

function printTable(json)
{
	var items_tbody = document.getElementById("items_table").getElementsByTagName('tbody')[0];
	var balance_cell = document.getElementById("items_table").getElementsByTagName('tfoot')[0].rows[0].cells[1];
	var rows = json["table"];
	var balance = json["balance"];
	var row_count = items_table.tBodies[0].rows.length;
	var text1 = '<button type="button" class="close" onClick="deleteItem(';
	var text2 = ')"><span aria-hidden="true">&times;</span></button>';

	for (let i = 0; i < row_count; i++){
		items_tbody.deleteRow(0);
	}
	for (let i = 0; i < rows.length; i++)
	{
		let row = items_tbody.insertRow(i);
		let item = row.insertCell(0);
		let total = row.insertCell(1);
		let del_button = row.insertCell(2);
		item.innerHTML = rows[i][0] + "  --  " + rows[i][1];
		total.innerHTML = "$" + rows[i][2];
		del_button.innerHTML = text1 + i + text2;
	}
	balance_cell.innerHTML = "$" + balance;
}

function printInvoice(){
	var client_name = document.getElementById("client_name").value;
	var payment = document.getElementById("input_payment").value;
	var comments = document.getElementById("comments").value;

	//// HAVE TO VALIDATE HERE IF CLIENT NAME OR THE PAYMENT ARE VALID, BEFORE CONTINUIING WITH THE REST OF THE THING.
	fetch("/set-transaction-info", {
		method: "POST",
		body: JSON.stringify({client_name: client_name, payment: payment, comments: comments}),
	})
	.catch(error => {
		console.log('Error!');
		console.error(error);
	});
	//// HAVE TO VALIDATE THE RESPONSE OF THE SERVER, IF THE CLIENT EXISTS!! BEFORE CONTINUING WITH THE REST.
	//// Maybe using Flashes
	try
	{
		window.open("/print-invoice", '_blank');
	}
	catch(error)
	{
		console.log('Error!');
		console.error(error);
	}
}

function deleteSubservice(subserviceId) {
  fetch("/delete-subservice", {
    method: "POST",
    body: JSON.stringify({ subserviceId: subserviceId }),
  })
  .then(response => {
    window.location.href = "/services-config";
  })
  .catch(error => {
    console.log('Error!');
    console.error(error);
  });
}


function getSubServices()
{
  var serviceId = document.getElementById("input_service").value;
  if (serviceId != "0")
    fetch("/get-subservices",{
      method: "POST",
      body: JSON.stringify({ serviceId: serviceId }),
    })
    .then(response => response.json())
    .then(json => loadSubServices(json))
    .catch(error => {
      console.log('Error!');
      console.error(error);
    });
   else{
     loadSubServices("");
   }
}


function loadSubServices(content)
{
  var dropdown = document.getElementById('input_subservice');
  dropdown.length = 1;

    for(let i = 0; i < content.length; i++){
      option = document.createElement('option');
	  option.value = content[i][0];
      option.text = content[i][1];
      dropdown.add(option);
    }
}

function deleteService(serviceId) {
  fetch("/delete-service", {
    method: "POST",
    body: JSON.stringify({ serviceId: serviceId }),
  })
  .then(response => {
    window.location.href = "/services-config";
  })
  .catch(error => {
    console.log('Error!');
    console.error(error);
  });
}

function deletePayment(paymentId) {
  fetch("/delete-payment-method", {
    method: "POST",
    body: JSON.stringify({ paymentId: paymentId }),
  })
  .then(response => {
    window.location.href = "/payment-config";
  })
  .catch(error => {
    console.log('Error!');
    console.error(error);
  });
}
