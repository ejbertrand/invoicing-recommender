function deleteService(serviceId) {
  fetch("/delete-service", {
    method: "POST",
    body: JSON.stringify({ serviceId: serviceId }),
  }).then((_res) => {
    window.location.href = "/services-config";
  });
}

function deletePayment(paymentId) {
  fetch("/delete-payment-method", {
    method: "POST",
    body: JSON.stringify({ paymentId: paymentId }),
  }).then((_res) => {
    window.location.href = "/payment-config";
  });
}
