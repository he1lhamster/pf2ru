const MenuExpanders = document.querySelectorAll(".expanded-menu")

for(let menuItem of MenuExpanders) {

    if (sessionStorage.getItem(menuItem.id) == 1) {
        menuItem.classList += "expanded-menu--active"
        document.getElementById(menuItem.id+"-submenu").classList.add('submenu--active')
        document.getElementById(menuItem.id+"-arrow").classList.add('open-menu--active')
        
    } else {
      sessionStorage.setItem(menuItem.id, 0)
    }
    
    clickable = document.getElementById(menuItem.id+"-click")

    clickable.addEventListener("click", () => {
      changeStateMenu(menuItem)
      var childrens = submenu.querySelectorAll(".expanded-menu--active")

      if (childrens) {
        for (let child of childrens) {

          currentState = sessionStorage.getItem(child.id)
          submenu = document.getElementById(child.id+"-submenu")
          arrow = document.getElementById(child.id+"-arrow")

          if (currentState == 1) {
                  child.classList.remove("expanded-menu--active")
                  submenu.classList.remove('submenu--active')
                  arrow.classList.remove('open-menu--active')
                  sessionStorage.setItem(child.id, 0)
          }
        }
      }
    })    
}


function changeStateMenu(item) {
  currentState = sessionStorage.getItem(item.id)
  submenu = document.getElementById(item.id+"-submenu")
  arrow = document.getElementById(item.id+"-arrow")

  if (currentState == 1) {
          item.classList.remove("expanded-menu--active")
          submenu.classList.remove('submenu--active')
          arrow.classList.remove('open-menu--active')
          sessionStorage.setItem(item.id, 0)

  } else {
          arrow.classList.add('open-menu--active')
          item.classList += " expanded-menu--active"
          submenu.classList.add("submenu--active")
          sessionStorage.setItem(item.id, 1)
      }
}


async function setLang(setLanguage) {
        const response = await fetch(`/set_language/${setLanguage}`, {
            method: 'POST',
            mode: 'cors',
        });
        // localStorage.setItem('lang', setLanguage)
        location.reload()
}


// When the user clicks on the button, scroll to the top of the document
function topFunction() {
  document.body.scrollTop = 0; // For Safari
  document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}

window.onscroll = function () { scrollFunction() };

//Get the button:
const mybutton = document.getElementById("back-to-top-button");

// When the user scrolls down 20px from the top of the document, show the button
function scrollFunction() {
   if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
      mybutton.style.display = "block";
   } else {
      mybutton.style.display = "none";
   }
}

//traits
let traits = document.querySelectorAll(".trait")
traits.forEach(onTraitHover);

function onTraitHover(item) {
    item.addEventListener("mouseover", function() {      
      traitText = item.getElementsByClassName('trait-text')[0]
      
      traitText.classList.add('trait-text--active')       
    })
    item.addEventListener("mouseout", function() { 
      traitText = item.getElementsByClassName('trait-text')[0]
      traitText.classList.remove('trait-text--active')
    })

  }


let globalLang
function setLangButton() {
    const currentLang = document.cookie
        .split("; ")
        .find((row) => row.startsWith("lang"))
        ?.split("=")[1];

        globalLang = currentLang

   if (currentLang == 'en') {
      document.getElementById('eng-lang-button').classList.add('lang-button--active')
      document.getElementById('rus-lang-button').classList.remove('lang-button--active')
   }
   else {
      document.getElementById('eng-lang-button').classList.remove('lang-button--active')
      document.getElementById('rus-lang-button').classList.add('lang-button--active')
   }
}

window.onload = function () {
  setLangButton()
    // console.log(globalLang)
}

function openSidenav() {
  // $(".sidenav").toggleClass('active')
    const leftMenu =   document.getElementById('leftMenu')
    let overlay = document.getElementById("overlay")

    leftMenu.classList.toggle('leftmenu--active')
    document.getElementById('leftMenu-burger').classList.toggle('header__burger--active')

    if (leftMenu.classList.contains('leftmenu--active')) {
        overlay.style.display = 'block';
        document.body.classList.add('no-scroll');  // Prevent body scrolling
    } else {
        overlay.style.display = 'none';
        document.body.classList.remove('no-scroll');  // Allow body scrolling
    }
}

document.getElementById('open-search-input-button').addEventListener('click', async function(event) {
    event.preventDefault()

    const dropdown = document.getElementById('search-panel--dropdown');
    dropdown.classList.toggle('show');
});