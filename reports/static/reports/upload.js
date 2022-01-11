const csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value;
const alertBox = document.getElementById("alert-box");

const handleAlerts = (type, msg)=>{
    alertBox.innerHTML = `
        <div class="alert alert-${type}" role="alert">
            ${msg}
        </div>
  `
}


Dropzone.autoDiscover = false;
const myDropzone = new Dropzone('#my-dropzone',{
    url: '/reports/upload/',
    init: ()=>{
        this.on('sending', (file, xhr, formData)=>{
            console.log('sending');
            formData.append('csrfmiddlewaretoken',csrf);
        })
        this.on("success", (file,response)=>{
            console.log(response);
            const ex = response;
            if (ex){
                handleAlerts('danger', 'File already exists');
            }
            else{
                handleAlerts('success', 'File Uploaded');
            }
        })
    },
    maxFiles: 3,
    maxFileSize: 3,
    acceptedFiles: '.csv'
})