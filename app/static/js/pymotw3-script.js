document.addEventListener('DOMContentLoaded', function () {
 console.log("Hello!")

  let elems = document.querySelectorAll('.sidenav')
  let instances = M.Sidenav.init(elems)

  let ddElems = document.querySelectorAll('.dropdown-trigger')
  let ddInstances = M.Dropdown.init(ddElems, { hover: false })

  let ddCateg = document.querySelectorAll('.dropdown-categ-trigger')
  let ddCategInstances = M.Dropdown.init(ddCateg)

  let configTabElems = document.getElementById("configTabs")
  let configTabInstance = M.Tabs.init(configTabElems)
  console.log({configTabInstance})


})

/*
  Cismiss the div containing the flashmessage with id = elementID
 */
function closeMsg(elementId) {
  const flashMessage = document.getElementById(elementId)
  console.log({flashMessage})
  const parent = flashMessage.parentNode
  parent.removeChild(flashMessage)
}
