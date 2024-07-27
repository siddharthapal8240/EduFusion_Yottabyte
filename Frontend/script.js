const webcam = document.getElementById('webcam');

if (navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            webcam.srcObject = stream;
        })
        .catch((error) => {
            console.error('Error accessing webcam:', error);
        });
} else {
    console.error('getUserMedia not supported in this browser.');
}