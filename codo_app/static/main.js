

(function(){

  //section toast error
  const toastTrigger = document.getElementById("toast-error")
  if (toastTrigger) {
    const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toastLiveExample)
    toastBootstrap.show()
    
  }
})()

 if(window.location.hash) {
      var hash = window.location.hash.substring(1); //Puts hash in variable, and removes the # character
      console.log(hash)
      // hash found
  } else {
      // No hash found
  }