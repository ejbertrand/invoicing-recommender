function addItem(){
	var serviceId = document.getElementById("input_service").value;
	var subservice = document.getElementById("input_subservice").value;
	var total = document.getElementById("total").value;

	fetch("/add-item", {
		method: "POST",
		body: JSON.stringify({serviceId: serviceId, subservice: subservice, total: total}),
	})
	.then(response => response.json())
    .then(json => console.log("Response: ", json))
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
     loadSubServices("", 0);
   }
}


// function loadSubServices(content, flag)
function loadSubServices(content)
{
  var dropdown = document.getElementById('input_subservice');
  dropdown.length = 1;

//   if (flag != 0)
//   {
    for(let i = 0; i < content.length; i++){
      option = document.createElement('option');
      option.text = content[i];
      option.value = content[i];
      dropdown.add(option);
    }
//   }
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
