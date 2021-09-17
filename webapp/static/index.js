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
	var items_table = document.getElementById("items-table")
	var row_count = items_table.tBodies[0].rows.length;

	form.reset();
	for (let i = 0; i < row_count; i++){
		items_table.deleteRow(1);
	}
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

function addItem(){
	var serviceId = document.getElementById("input_service").value;
	var subserviceId = document.getElementById("input_subservice").value;
	var total = document.getElementById("total").value;

	fetch("/add-item", {
		method: "POST",
		body: JSON.stringify({serviceId: serviceId, subserviceId: subserviceId, total: total}),
	})
	.then(response => response.json())
    .then(json => console.log(json))
	.catch(error => {
		console.log('Error!');
		console.error(error);
	  });
}

function printInvoice(){
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
