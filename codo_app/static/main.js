

(function(){
  const myModal = document.getElementById('myModal')
  const myInput = document.getElementById('myInput')
  
  myModal.addEventListener('shown.bs.modal', () => {
    myInput.focus()
  })
  

  //section toast error
  const toastTrigger = document.getElementById("toast-error")
  if (toastTrigger) {
    const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toastLiveExample)
    toastBootstrap.show()
    
  }
})()