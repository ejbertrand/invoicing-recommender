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
	client_name.value = "";
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
	var serviceId = document.getElementById("input_service").value;
	var subserviceId = document.getElementById("input_subservice").value;
	var total = document.getElementById("total").value;
	var client_id = document.getElementById("client_name").value;
	var payment_id = document.getElementById("input_payment").value;
	var comments = document.getElementById("comments").value;

	if (serviceId == '0' || subserviceId == '0')
		alert("Oops!\nPlease, choose a valid Service and Subservice combination.");
	else if (total == "" || isNaN(total))
		alert("Please, insert a numerical value for the Total.");
	else
	{
		fetch("/add-item", {
			method: "POST",
			body: JSON.stringify({serviceId: serviceId, subserviceId: subserviceId,
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

	if (client_name == "")
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
	var newHTML = "";
	var chosenIdType = "";

	disableClientActions();	
	// Creating the input fields on the client's row
	for (let column_index = 0; column_index <= 6; column_index++)
	{
		if (column_index == 4)
		{
			newHTML = "<select id='" + columns[column_index] + "-" + client_id + "' class='form-control'></select>";
			chosenIdType = row[column_index].innerHTML;
		}
		else
			newHTML = "<input type='text' id='" + columns[column_index] + "-" + client_id + "' value ='" + 
						row[column_index].innerHTML + "' size='10'>";
		row[column_index].innerHTML = newHTML;
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
		body: JSON.stringify({chosenIdType: chosenIdType}),
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
	document.getElementById("choose_id").disabled = true;
  }


  /***********************************************************************************/
  /* Function Name: saveClientChanges
  /* Purpose: 		Save the changes made on the client row
  /***********************************************************************************/
  function saveClientChanges(columns, client_id)
  {
	const row = document.getElementById("client-" + client_id).getElementsByTagName('td'); 
	const client_info = [];

	for (let i = 0; i <= 6; i++)
	{
		if (i == 4)
		{
			let idtype_select = document.getElementById(columns[i] + "-" + client_id);
			client_info[i] = idtype_select.options[idtype_select.selectedIndex].text;
		}
		else
			client_info[i] = document.getElementById(columns[i] + "-" + client_id).value;
	}
	fetch("/edit-client", {
		method: "POST",
		body: JSON.stringify({ client_id: client_id, client_name: client_info[0],
			client_tel: client_info[1], client_stel: client_info[2], client_email: client_info[3],
			client_idtype: client_info[4], client_idno: client_info[5], client_address: client_info[6]}),
	 })
	 .then(response => {
		for (let column_index = 0; column_index <= 6; column_index++)
			row[column_index].innerHTML = client_info[column_index];
		alert("Client information was updated succesfully");
		enableClientActions();
	 })
	 .catch(error => {
		 console.log('Error!');
		 console.error(error);
	 });
  }


/***********************************************************************************/
/* Function Name: 	loadIDTypes
/* Purpose: 		Loads the option HTML element with the corresponding ID types
/***********************************************************************************/
function loadIDTypes(elementId, content)
{
	var dropdown = document.getElementById(elementId);
	var chosenId = content[content.length - 1];

    for(let i = 0; i < content.length - 1; i++){
      option = document.createElement('option');
	  option.value = content[i][0];
      option.text = content[i][1];
      dropdown.add(option);
    }
	dropdown.value = chosenId;
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
	document.getElementById("choose_id").disabled = false;
  }
