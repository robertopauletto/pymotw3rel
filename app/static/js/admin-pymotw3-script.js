document.addEventListener('DOMContentLoaded', function () {
  const elems = document.querySelectorAll('.sidenav')
  const instances = M.Sidenav.init(elems)

  const fabElems = document.querySelectorAll('.fixed-action-btn')
  const fabInstances = M.FloatingActionButton.init(fabElems, {hoverEnabled: false})

  const ddElems = document.querySelectorAll('.dropdown-trigger')
  const ddInstances = M.Dropdown.init(ddElems, {hover: false})

  const ddCateg = document.querySelectorAll('.dropdown-categ-trigger')
  const ddCategInstances = M.Dropdown.init(ddCateg)

  const configTabElems = document.getElementById("configTabs")
  const configTabInstance = M.Tabs.init(configTabElems)

  const selectItems = document.querySelectorAll('select')
  const selectInstances = M.FormSelect.init(selectItems)

  loadModuleAutocompletion(populateModuleAutocompletion)


})

function populateModuleAutocompletion(cdata) {
  const autoComp = document.querySelector('.autocomplete')
  // console.log(cdata)
  const autoCompInstances = M.Autocomplete.init(autoComp, {
    data: cdata
  })
  // console.log({autoCompInstances})
}

function loadModuleAutocompletion(callback) {
  const httpRequest = new XMLHttpRequest();
  httpRequest.onload = function () { // When the request is loaded
    callback(httpRequest.responseText);// We're calling our method
  };
  httpRequest.open('GET', "/static/js/autocomp.json");
  httpRequest.send();
}

/*
  Dismiss the div containing the flashmessage with id = elementID
 */
function closeMsg(elementId) {
  console.log("dismissible")
  const flashMessage = document.getElementById(elementId)
  const parent = flashMessage.parentNode
  parent.removeChild(flashMessage)
}

function sortModuleList() {
  const modList = document.getElementById('modlist')
  const elements = modList.innerHTML.split('\n')
  const elemSorted = elements.sort((a, b) =>
    a.toLocaleLowerCase().localeCompare(b.toLocaleLowerCase())
  )
  modList.innerHTML = elemSorted.join('\n')
}

function muduleListStringify1() {
  const modList = document.getElementById('modlist')
  const elements = modList.innerHTML.split('\n').join(',')
  console.log(elements)
  document.execCommand("copy")
}

async function muduleListStringify(charsep=' ') {
  const modList = document.getElementById('modlist')
  const elements = modList.innerHTML.split('\n').join(charsep)
  console.log(elements)
  try {
    await navigator.clipboard.writeText(elements)
    // M.Toast({html: 'Stringa moduli copiata'})
  } catch {
    console.log("Pasting error!")
  }
}
