/*******************************************************************/
/* Function Name: 	cleanSession
/* Purpose: 		Clean session variables
/*******************************************************************/
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

/*******************************************************************/
/* Function Name: 	cleanForm			
/* Purpose: 		Clean all the fields and table of a transaction
/*******************************************************************/
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

/*******************************************************************/
/* Function Name: 	openTransaction
/* Purpose: 		Opens a new transaction
/*******************************************************************/
function openTransaction()
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

/*******************************************************************/
/* Function Name: 	cancelTransaction
/* Purpose: 		Cancels the ongoing transaction
/*******************************************************************/
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

/*******************************************************************/
/* Function Name: 	deleteItem
/* Purpose: 		Deletes an item from the transaction table
/*******************************************************************/
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

/*******************************************************************/
/* Function Name: 	addItem
/* Purpose: 		Adds an item into the transaction table
/*******************************************************************/
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

/*******************************************************************/
/* Function Name: 	printTable
/* Purpose: 		Prints the transaction table into the HTML object
/*******************************************************************/
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

/*******************************************************************/
/* Function Name: 	printInvoice
/* Purpose: 		Generate the invoice to be printed
/*******************************************************************/
function printInvoice(){
	var client_name = document.getElementById("client_name").value;
	var payment = document.getElementById("input_payment").value;
	var comments = document.getElementById("comments").value;

	//// HAVE TO VALIDATE HERE IF CLIENT NAME OR THE PAYMENT ARE VALID, BEFORE CONTINUIING WITH THE REST OF THE THING.
	fetch("/set-invoice-info", {
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

/*******************************************************************/
/* Function Name: 	deleteSubservice
/* Purpose: 		Deletes a subservice from the subservice list
/*******************************************************************/
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

/******************************************************************************/
/* Function Name: 	getSubservices
/* Purpose: 		Get the list of subservices associated to a parent service
/******************************************************************************/
function getSubServices()
{
  var serviceId = document.getElementById("input_service").value;
  if (serviceId != "0")
    fetch("/get-subservices",{
      method: "POST",
      body: JSON.stringify({ serviceId: serviceId }),
    })
    .then(response => response.json())
    .then(json => loadSubservices(json))
    .catch(error => {
      console.log('Error!');
      console.error(error);
    });
   else{
     loadSubservices("");
   }
}

/***********************************************************************************/
/* Function Name: 	loadSubservices
/* Purpose: 		Loads the option HTML element with the corresponding subservices
/***********************************************************************************/
function loadSubservices(content)
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

/***********************************************************************************/
/* Function Name: 	deleteService
/* Purpose: 		Deletes a service from the services list
/***********************************************************************************/
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

/***********************************************************************************/
/* Function Name: 	deletePayment
/* Purpose: 		Deletes a payment from the payment list
/***********************************************************************************/
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

/***********************************************************************************/
/* Function Name: 	closeTransaction
/* Purpose: 		Closes a transaction and stores it in the database
/***********************************************************************************/
function closeTransaction(){
	var client_name = document.getElementById("client_name").value;
	var payment = document.getElementById("input_payment").value;
	var comments = document.getElementById("comments").value;

	//// HAVE TO VALIDATE HERE IF CLIENT NAME OR THE PAYMENT ARE VALID, BEFORE CONTINUIING WITH THE REST OF THE THING.
	// VALIDATE IF THE PAYMENT WAS SELECTED
	fetch("close-transaction", {
		method:	"POST",
		body: JSON.stringify({client_name: client_name, payment: payment, comments: comments}),
	})
	.then(response => response.json())
    .then(json => {
		if (json == 0){
			let form = document.getElementById("transaction_form");
			let new_btn = document.getElementById("new_button");
			let cancel_btn = document.getElementById("cancel_button");

			console.log("New record");
			form.hidden = true;
			cancel_btn.hidden = true;
			new_btn.hidden = false;
			cleanSession();
			cleanForm();
		}
		else if (json == 1)
			console.log("No client was selected.");
		else if (json == 2)
			console.log("No payment method was selected.");
		else if (json == 3)
			console.log("No items registered.");
		else if (json == 4)
			console.log("Nothing on balance.");
	})
	.catch(error => {
		console.log('Error!');
		console.error(error);
	});
}
