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
	var account_cell = document.getElementById("items_table").getElementsByTagName('tfoot')[0].rows[0].cells[1];

	form.reset();
	client_name.value = 0;
	payment_id.value = 0;
	comments.value = "";
	for (let i = 0; i < row_count; i++){
		items_table.deleteRow(1);
	}
	account_cell.innerHTML = "$0.00";
}

/*******************************************************************/
/* Function Name: 	printItemsTable
/* Purpose: 		Prints the transaction table into the HTML object
/*******************************************************************/
function printItemsTable(json)
{
	var items_tbody = document.getElementById("items_table").getElementsByTagName('tbody')[0];
	var account_cell = document.getElementById("items_table").getElementsByTagName('tfoot')[0].rows[0].cells[1];
	var rows = json["table"];
	var account = json["account"];
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
	account_cell.innerHTML = "$" + account;
}


/******************************************************************************/
/* Function Name: 	getSubservices
/* Purpose: 		Get the list of subservices associated to a parent service
/******************************************************************************/
function getSubServices()
{
  var service_parent_id = document.getElementById("input_service").value;
  if (service_parent_id != "0")
    fetch("/get-subservices",{
      method: "POST",
      body: JSON.stringify({ service_parent_id: service_parent_id }),
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
function deleteItem(row_id)
{
	fetch("/delete-item", {
		method:	"POST",
		body: JSON.stringify({row_id: row_id}),
	})
	.then(response => response.json())
	.then(json => printItemsTable(json))
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
	var service_id = document.getElementById("input_service").value;
	var subservice_id = document.getElementById("input_subservice").value;
	var total = document.getElementById("total").value;
	var client_id = document.getElementById("client_name").value;
	var payment_id = document.getElementById("input_payment").value;
	var comments = document.getElementById("comments").value;

	if (service_id == '0' || subservice_id == '0')
		alert("Please, choose a valid Service and Subservice combination.");
	else if (total == "" || isNaN(total))
		alert("Please, insert a numerical value for the Total.");
	else
	{
		fetch("/add-item", {
			method: "POST",
			body: JSON.stringify({service_id: service_id, subservice_id: subservice_id,
				total: total, client_id: client_id, payment_id: payment_id,
				comments: comments}),
		})
		.then(response => response.json())
		.then(json => {
			printItemsTable(json);
			let total = document.getElementById("total");
			let servicebox = document.getElementById("input_service");

			total.value = '';
			servicebox.selectedIndex = 0;
			loadSubservices("");
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
	var client_id = document.getElementById("client_name").value;
	var payment_id = document.getElementById("input_payment").value;
	var comments = document.getElementById("comments").value;
	var payment_amount = document.getElementById("payment_amount").value;

	if (client_id == "0")
		alert("No client was chosen!");
	else if (payment_id == "0")
		alert("No payment method was selected!");
	else
	{
		fetch("/set-invoice-info", {
			method: "POST",
			body: JSON.stringify({client_id: client_id, payment_id: payment_id, 
				comments: comments, payment_amount : payment_amount}),
		})
		.then(response => response.json())
		.then(json => {
			if (json["flag"] == 1)
				alert("Oops!\nThere are no items to register!");
			else if (json["flag"] == 2)
				alert("Oops!\nThe account is $0.00!");
			else if (json["flag"] == 3)
				alert("Please, insert a numerical value for payment.");
			else if (json["flag"] == 4)
				alert("Sorry, there was an error printing the invoice. \nIf it happens again, please report to the administrator.");
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
	//var comments = document.getElementById("comments").value;

	if (client_name == "0")
		alert("The client name is empty!");
	else if (payment_id == "0")
		alert("No payment method was selected!");
	else
	{
		fetch("close-transaction", {
			method:	"POST",
			body: JSON.stringify({}),
		})
		.then(response => response.json())
		.then(json => {
			if (json["flag"] == 3)
				alert("The invoice has to be generated first!");
			else
			{
				let form = document.getElementById("transaction_form");
				let new_btn = document.getElementById("new_button");
				let cancel_btn = document.getElementById("cancel_button");
		
				alert("Transaction saved!");
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
/* Function Name: 	printReceipt
/* Purpose: 		Print a receipt in PDF
/*******************************************************************/
function printReceipt(pending_transaction_no)
{
	fetch("/set-receipt-info", {
		method: "POST",
		body: JSON.stringify({ pending_transaction_no: pending_transaction_no }),
	})
	.then(response => { 
		window.open("/print-receipt", '_blank');
	})
	.catch(error => {
		console.log('Error!');
		console.error(error);
	});
}


/*******************************************************************/
/* Function Name: 	printReceipt
/* Purpose: 		Print a receipt in PDF
/*******************************************************************/
function printReceipt(pending_transaction_no)
{
	window.open("/print-receipt?ptn=" + pending_transaction_no, '_blank');
}


/*******************************************************************/
/* Function Name: 	payReceipt
/* Purpose: 		Pay a receipt
/*******************************************************************/
function payReceipt(pending_transaction_no)
{
	fetch("/pay-receipt", {
		method: "POST",
		body: JSON.stringify({ pending_transaction_no: pending_transaction_no }),
	  })
	  .then(response => {
		window.location.href = "/transactions-pending";
	  })
	  .catch(error => {
		console.log('Error!');
		console.error(error);
	  });
}



/*******************************************************************/
/************************** CONFIGURATION **************************/
/*******************************************************************/

/*******************************************************************/
/* Function Name: 	deleteSubservice
/* Purpose: 		Deletes a subservice from the subservice list
/*******************************************************************/
function deleteSubservice(subservice_id) {
	fetch("/delete-subservice", {
	  method: "POST",
	  body: JSON.stringify({ subservice_id: subservice_id }),
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
function deleteService(service_id) {
	fetch("/delete-service", {
	  method: "POST",
	  body: JSON.stringify({ service_id: service_id }),
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


  /***********************************************************************************/
  /* Function Name: deleteIdentification
  /* Purpose: 		Deletes an ID type from the list
  /***********************************************************************************/
  function deleteIdentification(identification_id) {
	fetch("/delete-identification", {
	  method: "POST",
	  body: JSON.stringify({ identification_id: identification_id }),
	})
	.then(response => {
	  window.location.href = "/identification-config";
	})
	.catch(error => {
	  console.log('Error!');
	  console.error(error);
	});
  }




/*******************************************************************/
/********************** CLIENT CONFIGURATION ***********************/
/*******************************************************************/

	/*******************************************************************/
	/* Function Name: 	addClient
	/* Purpose: 		Adds an item into the transaction table
	/*******************************************************************/
	function addClient(){
		var client_name = document.getElementById("client_name").value;
		var client_address = document.getElementById("client_address").value;
		var client_main_phone = document.getElementById("client_main_phone").value;
		var client_secondary_phone = document.getElementById("client_secondary_phone").value;
		var client_email = document.getElementById("client_email").value;
		var client_identification_id = document.getElementById("choose_identification_id").value;
		var client_identification_number = document.getElementById("client_identification_number").value;

		if (client_name == "")
			alert("The client name is empty!");
		else if (client_address == "")
			alert("The address is empty!");
		else if (client_main_phone == "")
			alert("The telephone number is empty!");
		else
		{
			fetch("/add-client", {
				method: "POST",
				body: JSON.stringify({client_name: client_name, client_address: client_address,
				client_main_phone: client_main_phone, client_secondary_phone: client_secondary_phone,
				client_email: client_email, client_identification_id: client_identification_id, 
				client_identification_number: client_identification_number}),
			})
			.then(response => response.json())
			.then(json => {
				if(json["flag"] == 0)
				{
					alert("The client was added!");
					window.location.href = "/clients";
				}
				else
					alert("Sorry, an error ocurred!");
			})
			.catch(error => {
				console.log('Error!');
				console.error(error);
			});
		}
	}



  /***********************************************************************************/
  /* Function Name: deleteClient
  /* Purpose: 		Deletes a client from the database
  /***********************************************************************************/
  function deleteClient(client_id) {
	fetch("/delete-client", {
	  method: "POST",
	  body: JSON.stringify({ client_id: client_id }),
	})
	.then(response => {
	  window.location.href = "/clients";
	})
	.catch(error => {
	  console.log('Error!');
	  console.error(error);
	});
  }


  /***********************************************************************************/
  /* Function Name: editClient
  /* Purpose: 		Edit client information
  /***********************************************************************************/
  function editClient(client_id) {
	const row = document.getElementById("client-" + client_id).getElementsByTagName('td'); 
	const columns = ['row-client-name', 'row-client-tel', 'row-client-stel', 'row-client-email',
	 				'sel-client-idtyp', 'row-client-idno', 'row-client-address'];
	var new_html = "";
	var chosen_id_type = "";

	disableClientActions();	
	// Creating the input fields on the client's row
	for (let column_index = 0; column_index <= 6; column_index++)
	{
		if (column_index == 4)
		{
			new_html = "<select id='" + columns[column_index] + "-" + client_id + "' class='form-control'></select>";
			chosen_id_type = row[column_index].innerHTML;
		}
		else
			new_html = "<input type='text' id='" + columns[column_index] + "-" + client_id + "' value ='" + 
						row[column_index].innerHTML + "' size='10'>";
		row[column_index].innerHTML = new_html;
	}
	// Setting event listener (Enter key) to the input fields of the row
	for (let column_index = 0; column_index < columns.length; column_index++)
	{
		if (column_index == 4)
			continue;
		let node = document.getElementById(columns[column_index] + "-" + client_id);
		node.addEventListener('keydown', function onEvent(event)
		{
			if (event.key == "Enter")
				saveClientChanges(columns, client_id);
		});
	}
	fetch("/get-id-types", 
	{
		method: "POST",
		body: JSON.stringify({chosen_id_type: chosen_id_type}),
	})
	.then(response => response.json())
	.then(json => {
		loadIDTypes(columns[4] + "-" + client_id, json);
	})
	.catch(error => {
		console.log('Error!');
		console.error(error);
	  });
  }


 /***********************************************************************************/
  /* Function Name: disableClientActions
  /* Purpose: 		Disable New Client form and action buttons
  /***********************************************************************************/
  function disableClientActions()
  {
	var table = document.getElementById("clients_table");
	var form = document.getElementById("client-form");
	var elements = form.elements;

	for (let i = 1; i < table.rows.length; i++)
	{
		document.getElementById("btn-editclient-" + i).disabled = true;
		document.getElementById("btn-delclient-" + i).disabled = true;
	}
	for (var i = 0, len = elements.length; i < len; ++i) 
    	elements[i].readOnly = true;
	document.getElementById("btn-add-client").disabled = true;
	document.getElementById("choose_identification_id").disabled = true;
  }


  /***********************************************************************************/
  /* Function Name: saveClientChanges
  /* Purpose: 		Save the changes made on the client row
  /***********************************************************************************/
  function saveClientChanges(columns, client_id)
  {
	const row = document.getElementById("client-" + client_id).getElementsByTagName('td'); 
	var client_name = document.getElementById(columns[0] + "-" + client_id).value;
	var client_main_phone = document.getElementById(columns[1] + "-" + client_id).value;
	var client_secondary_phone = document.getElementById(columns[2] + "-" + client_id).value;
	var client_email = document.getElementById(columns[3] + "-" + client_id).value;
	var select_idtype = document.getElementById(columns[4] + "-" + client_id);
	var client_identification_type = select_idtype.options[select_idtype.selectedIndex].text;
	var client_identification_number = document.getElementById(columns[5] + "-" + client_id).value;
	var client_address = document.getElementById(columns[6] + "-" + client_id).value;

	if (client_name == "")
		alert("Name cannot be left empty!");
	else if (client_main_phone == "")
		alert("Main phone cannot be left empty!");
	else if (client_address == "")
		alert("Address cannot be left empty!");
	else
	{
		fetch("/edit-client", 
		 {
			method: "POST",
			body: JSON.stringify({client_id: client_id, client_name: client_name,
				client_main_phone: client_main_phone, client_secondary_phone: client_secondary_phone,
				client_email: client_email, client_identification_type: client_identification_type,
				client_identification_number: client_identification_number, client_address: client_address})
		 })
		 .then(response => {
			const client_info = [client_name, client_main_phone, client_secondary_phone, client_email,
				client_identification_type, client_identification_number, client_address];
			var client_modal = document.getElementById("client-" + client_id + "-modal");
			for (let column_index = 0; column_index <= 6; column_index++)
				row[column_index].innerHTML = client_info[column_index];
			client_modal.innerHTML = "Are you sure you want to delete <b>" + client_name + "</b> as a client?";
			alert("Client updated succesfully!");
			enableClientActions();
		 })
		 .catch(error => {
			 console.log('Error!');
			 console.error(error);
		 });
	}
  }


/***********************************************************************************/
/* Function Name: 	loadIDTypes
/* Purpose: 		Loads the option HTML element with the corresponding ID types
/***********************************************************************************/
function loadIDTypes(element_id, content)
{
	var dropdown = document.getElementById(element_id);
	var chosen_id = content[content.length - 1];

    for(let i = 0; i < content.length - 1; i++){
      option = document.createElement('option');
	  option.value = content[i][0];
      option.text = content[i][1];
      dropdown.add(option);
    }
	dropdown.value = chosen_id;
}


  /***********************************************************************************/
  /* Function Name: enableClientActions
  /* Purpose: 		Enable New Client form and action buttons
  /***********************************************************************************/
  function enableClientActions()
  {
	var table = document.getElementById("clients_table");
	var form = document.getElementById("client-form");
	var elements = form.elements;

	for (let i = 1; i < table.rows.length; i++)
	{
		document.getElementById("btn-editclient-" + i).disabled = false;
		document.getElementById("btn-delclient-" + i).disabled = false;
	}
	for (var i = 0, len = elements.length; i < len; ++i) 
    	elements[i].readOnly = false;
	document.getElementById("btn-add-client").disabled = false;
	document.getElementById("choose_identification_id").disabled = false;
  }
