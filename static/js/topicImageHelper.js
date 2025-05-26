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
