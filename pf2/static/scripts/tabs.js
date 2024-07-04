const tabBtns = document.querySelectorAll(".tablink")
const tabContents = document.querySelectorAll(".tab-content")
const tabGroupId = document.querySelector('div.tabs-panel')
var activeBtn = document.querySelector('.tablink')
const tabHrefs = document.querySelectorAll(".tablink--href")

tabBtns.forEach(onTabClick);
tabHrefs.forEach(tabClickRedirect);

function setActiveBtn (activeTabGroup,activeTab) {
    localStorage.setItem(activeTabGroup,activeTab);
}

function onTabClick(item) {

    item.addEventListener("click", function() {
        let currentBtn = item;
        let tabId = currentBtn.getAttribute("data-tab");
        let currentTab = document.querySelector(tabId);

        if (!currentBtn.classList.contains('tablink--active')) {
            tabBtns.forEach(function (item) {
                item.classList.remove('tablink--active');
            });
            tabContents.forEach((item) => {
                item.classList.remove('tab-content--active');
            });
            currentBtn.classList.add('tablink--active');
            if (currentTab) {
                currentTab.classList.add('tab-content--active');
            }
            localStorage.setItem(tabGroupId.id, currentBtn.getAttribute('data-tab'))
        }
    });           
}

const searchParams = new URLSearchParams(window.location.search);
    if (searchParams.get('tab')) {
       localStorage.setItem(tabGroupId.id, '#'+searchParams.get('tab'));
    }

if (tabGroupId != null) {
    if (localStorage.getItem(tabGroupId.id) != null) {
        activeBtn = document.querySelector("[data-tab="+"\'"+ localStorage.getItem(tabGroupId.id)+"\']")
    } else {
        activeBtn = document.querySelector('.tablink')
    }

    activeBtn.click()
}

function tabClickRedirect(item) {
    item.addEventListener('click', function() {
        const tabHref = item.getAttribute('href');
        if (tabHref) {
            window.location.href = tabHref;
        }
    })
}
