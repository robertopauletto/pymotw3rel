document.addEventListener('DOMContentLoaded', function () {
  const elems = document.querySelectorAll('.sidenav')
  const instances = M.Sidenav.init(elems)

  const ddElems = document.querySelectorAll('.dropdown-trigger')
  const ddInstances = M.Dropdown.init(ddElems, {hover: false})

  const ddCateg = document.querySelectorAll('.dropdown-categ-trigger')
  const ddCategInstances = M.Dropdown.init(ddCateg)

  const toolTipped = document.querySelectorAll('.tooltipped')
  const toolTippedInstances = M.Tooltip.init(toolTipped)

  const btnGoTop = document.getElementById('btn-gotop')

  window.onscroll = function () {
    scrollf()
  }

  function scrollf() {
    if (
      document.body.scrollTop > 120 ||
      document.documentElement.scrollTop > 120
    ) {
      btnGoTop.style.display = 'block'
    } else {
      btnGoTop.style.display = 'none'
    }
  }

  const autoComp = document.querySelector('.autocomplete-modules')
  const autoCompInstances = M.Autocomplete.init(autoComp)
})

function gotoTop() {
  document.body.scrollTop = 0
  document.documentElement.scrollTop = 0
}
