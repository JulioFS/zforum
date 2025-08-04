let files;
let handleImageSelection = e => {
    files = e.target.files;
    showThumbnail(files);
};

let showThumbnail = files => {
    for(let i=0, file; file=files[i]; i++){
        let imageType = /image.*/;
        if(!file.type.match(imageType)) {
            alert('Not an Image');
        continue;
        }
        let image = document.createElement('img');
        // image.classList.add('...')
        let thumbnailContainer = document.getElementById('thumbnail-container');
        image.file = file;
        thumbnailContainer.appendChild(image);

        let reader = new FileReader()
        reader.onload = (aImg => {
            return e => {
                aImg.src = e.target.result;
            };
        })(image);

        let ret = reader.readAsDataURL(file);
        let canvas = document.createElement('canvas');
        ctx = canvas.getContext('2d');
        image.onload = () => {
            ctx.drawImage(image, 100, 100)
        }
    }
};

document.querySelector('#topic-images').addEventListener('change', handleImageSelection, false);



/* ================== */


const imageUpload = document.getElementById('image-upload');
const thumbnailContainer = document.getElementById('thumbnail-container');

imageUpload.addEventListener('change', handleFiles);

function handleFiles() {
    for (const file of this.files) {
        if (!file.type.startsWith('image/')) {
            continue; // Skip non-image files
        }

        const img = document.createElement('img');
        img.classList.add('thumbnail'); // Add a class for styling
        img.file = file; // Store the file object for later use
        thumbnailContainer.appendChild(img);

        const reader = new FileReader();
        reader.onload = (e) => {
            img.src = e.target.result; // Display the image data as a thumbnail
        };
        reader.readAsDataURL(file); // Read the file as a data URL
    }
}




// Make thumbnails draggable
thumbnailContainer.addEventListener('dragstart', (e) => {
    e.dataTransfer.setData('text/plain', e.target.dataset.index); // Store the index of the dragged thumbnail
    e.target.classList.add('dragging'); // Add a class for visual feedback
});

thumbnailContainer.addEventListener('dragover', (e) => {
    e.preventDefault(); // Prevent default browser behavior
    const draggingElement = document.querySelector('.dragging');
    const afterElement = getDragAfterElement(thumbnailContainer, e.clientX);

    if (afterElement == null) {
        thumbnailContainer.appendChild(draggingElement);
    } else {
        thumbnailContainer.insertBefore(draggingElement, afterElement);
    }
});

thumbnailContainer.addEventListener('dragend', (e) => {
    e.target.classList.remove('dragging'); // Remove the dragging class
    // Update the underlying array representing the image order for persistent reordering
});


function getDragAfterElement(container, x) {
    const draggableElements = [...container.querySelectorAll('.thumbnail:not(.dragging)')];

    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = x - box.left - box.width / 2; // Calculate horizontal offset for reordering
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: -Infinity }).element;
}



// #thumbnail-container {
//     display: flex; /* Arrange thumbnails horizontally */
//     flex-wrap: wrap; /* Wrap thumbnails to the next line if needed */
//     gap: 10px; /* Add spacing between thumbnails */
//     padding: 10px;
//     border: 2px dashed #ccc; /* Add a dashed border to signify a drop zone */
//     min-height: 100px;
// }

// .thumbnail {
//     width: 100px;
//     height: 100px;
//     object-fit: cover; /* Maintain aspect ratio and fill the thumbnail area */
//     border: 1px solid #ddd;
//     cursor: grab; /* Change cursor to indicate draggable items */
// }

// .dragging {
//     opacity: 0.5; /* Reduce opacity for visual feedback during dragging */
// }

