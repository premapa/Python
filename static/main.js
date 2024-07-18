document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.try-on');
    const videoFeed = document.getElementById('videoFeed');
    const mainContainer = document.querySelector('.main-container');
    const capturedImage = document.getElementById('capturedImage');
    const resultImg = document.getElementById('result-img');

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            const param_path = button.parentNode.parentNode.getElementsByClassName("product-image")[0].src;
            const image_path = param_path.split("path=")[1]
            open_video(image_path)
            // const srcPath = '/video_feed';
            // window.open.document.write('<iframe height="450"  allowTransparency="true" frameborder="0" scrolling="yes" style="width:100%;" src="'+srcPath+'" type= "text/javascript"></iframe>');
        })
        // button.addEventListener('click', () => {
        //     const product = button.getAttribute('data-product');
        //     mainContainer.style.display = 'flex';

        //     // Start the webcam feed
        //     // videoFeed.src = '/video_feed';

        //     // Wait for a moment to ensure the video feed starts
        //     setTimeout(() => {
        //         fetch('/capture_imagexx', {
        //             method: 'POST',
        //             headers: {
        //                 'Content-Type': 'application/json',
        //             },
        //             body: JSON.stringify({
        //                 'tx': 0,
        //                 'ty': 0,
        //                 'product': product
        //             })
        //         })
        //             .then(response => response.json())
        //             .then(data => {
        //                 if (data.image_path) {
        //                     capturedImage.src = data.image_path;
        //                     resultImg.src = data.image_path;
        //                 } else {
        //                     alert('Error: ' + data.error);
        //                 }
        //             })
        //             .catch(error => {
        //                 alert('Error: ' + error.message);
        //             });
        //     }, 1000);  // Adjust the timeout as necessary
        // });
    });

    open_video = (pName) => {
        const newWindow = window.open("/feed?pid=" + pName, "Capture Image", 'height=550,width=900');
        if (window.focus) { newWindow.focus() }
        return false;
    }
});
document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('stop-webcam').addEventListener('click', () => {
      fetch('/stop_webcam', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          alert('Webcam stopped successfully');
        } else {
          alert('Failed to stop webcam: ' + data.error);
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Error stopping webcam');
      });
    });
  });
  