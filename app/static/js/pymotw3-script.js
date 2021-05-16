document.addEventListener('DOMContentLoaded', function () {
 console.log("Hello!")

  const elems = document.querySelectorAll('.sidenav')
  const instances = M.Sidenav.init(elems)

  const ddElems = document.querySelectorAll('.dropdown-trigger')
  const ddInstances = M.Dropdown.init(ddElems, { hover: false })

  const ddCateg = document.querySelectorAll('.dropdown-categ-trigger')
  const ddCategInstances = M.Dropdown.init(ddCateg)

  const configTabElems = document.getElementById("configTabs")
  const configTabInstance = M.Tabs.init(configTabElems)

  const selectItems = document.querySelectorAll('select')
  const selectInstances = M.FormSelect.init(selectItems)

})

