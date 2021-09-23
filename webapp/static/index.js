/*******************************************************************/
/************************** RENDERING ******************************/
/*******************************************************************/

/*******************************************************************/
/* Function Name: 	cleanForm			
/* Purpose: 		Clean all the fields and table of a transaction
/*******************************************************************/
function cleanForm()
{
	var form = document.getElementById("transaction_form");
	var client_name = document.getElementById("client_name");
	var payment_id = document.getElementById("input_payment");
	var comments = document.getElementById("comments");
	var items_table = document.getElementById("items_table");
	var row_count = items_table.tBodies[0].rows.length;
	var balance_cell = document.getElementById("items_table").getElementsByTagName('tfoot')[0].rows[0].cells[1];

	form.reset();
	client_name.value = "";
	payment_id.value = 0;
	comments.value = "";
	for (let i = 0; i < row_count; i++){
		items_table.deleteRow(1);
	}
	balance_cell.innerHTML = "$0.00";
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




/*******************************************************************/
/************************** SESSION ********************************/
/*******************************************************************/

/*******************************************************************/
/* Function Name: 	openTransaction
/* Purpose: 		Opens a new transaction
/*******************************************************************/
function openTransaction()
{
	var form = document.getElementById("transaction_form");
	var new_btn = document.getElementById("new_button");
	var cancel_btn = document.getElementById("cancel_button");
	cleanForm();
	fetch("/open-transaction", {
		method:	"POST",
		body: JSON.stringify({}),
	})
	.then(() => {
		form.hidden = false;
		cancel_btn.hidden = false;
		new_btn.hidden = true;
	})
	.catch(error => {
		console.log("Error!");
		console.error(error);
	});
}

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
	var client_name = document.getElementById("client_name").value;
	var payment_id = document.getElementById("input_payment").value;
	var comments = document.getElementById("comments").value;

	if (serviceId == '0' || subserviceId == '0')
		alert("Oops! Please, choose a valid service and subservice combination.");
	else if (total == "" || isNaN(total))
		alert("Oops! Please, insert a numerical value.");
	else
	{
		fetch("/add-item", {
			method: "POST",
			body: JSON.stringify({serviceId: serviceId, subserviceId: subserviceId,
				total: total, client_name: client_name, payment_id: payment_id,
				comments: comments}),
		})
		.then(response => response.json())
		.then(json => printTable(json))
		.then(() => {
			serviceId.value = '0';
			subserviceId.value = '0';
			total.value = '';
		})
		.catch(error => {
			console.log('Error!');
			console.error(error);
		  });
	}
}

/*******************************************************************/
/* Function Name: 	printInvoice
/* Purpose: 		Generate the invoice to be printed
/*******************************************************************/
function printInvoice(){
	var client_name = document.getElementById("client_name").value;
	var payment_id = document.getElementById("input_payment").value;
	var comments = document.getElementById("comments").value;

	if (client_name == "")
		alert("The client name is empty!");
	else if (payment_id == "0")
		alert("No payment method was selected!");
	else
	{
		fetch("/set-invoice-info", {
			method: "POST",
			body: JSON.stringify({client_name: client_name, payment_id: payment_id, 
				comments: comments}),
		})
		.then(response => response.json())
		.then(json => {
			if (json["flag"] == 1)
				alert("Oops, there are not items to register!");
			else if (json["flag"] == 2)
				alert("Oops, the balance is $0.00!");
			else
			{
				window.open("/print-invoice", '_blank');
			}
		})
		.catch(error => {
			console.log('Error!');
			console.error(error);
		});
	}
}

/***********************************************************************************/
/* Function Name: 	closeTransaction
/* Purpose: 		Closes a transaction and stores it in the database
/***********************************************************************************/
function closeTransaction(){
	var client_name = document.getElementById("client_name").value;
	var payment_id = document.getElementById("input_payment").value;
	var comments = document.getElementById("comments").value;

	if (client_name == "")
		alert("The client name is empty!");
	else if (payment_id == "0")
		alert("No payment method was selected!");
	else
	{
		fetch("close-transaction", {
			method:	"POST",
			body: JSON.stringify({client_name: client_name, payment_id: payment_id, 
				comments: comments}),
		})
		.then(response => response.json())
		.then(json => {
			if (json["flag"] == 1)
				alert("Oops, there are not items to register!");
			else if (json["flag"] == 2)
				alert("Oops, the balance is $0.00!");
			else
			{
				let form = document.getElementById("transaction_form");
				let new_btn = document.getElementById("new_button");
				let cancel_btn = document.getElementById("cancel_button");
		
				alert("Transaction finished succesfully!");
				form.hidden = true;
				cancel_btn.hidden = true;
				new_btn.hidden = false;
				cleanSession();
				cleanForm();
			}
		})
		.catch(error => {
			console.log('Error!');
			console.error(error);
		});
	}
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
/************************** CONFIGURATION **************************/
/*******************************************************************/

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
  /* Function Name: deletePayment
  /* Purpose: 		Deletes a payment from the payment list
  /***********************************************************************************/
  function deletePayment(payment_id) {
	fetch("/delete-payment-method", {
	  method: "POST",
	  body: JSON.stringify({ payment_id: payment_id }),
	})
	.then(response => {
	  window.location.href = "/payment-config";
	})
	.catch(error => {
	  console.log('Error!');
	  console.error(error);
	});
  }
