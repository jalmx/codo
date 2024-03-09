

(function(){

  //section toast error
  const toastTrigger = document.getElementById("toast-error")
  if (toastTrigger) {
    const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toastLiveExample)
    toastBootstrap.show()
    
  }
})()