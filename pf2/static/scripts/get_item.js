async function getItem(link) {
    const itemID = link.getAttribute('itemID')
    const itemType = link.getAttribute('itemType')
    const itemLang = link.getAttribute('itemLang')

    const response = await fetch(`/viewbox/${itemType}/${itemID}?lang=${itemLang}`, {
            method: 'get',
        })
        .then(response => {
            if (!response.ok) {
              throw new Error('Network response was not ok');
            }
            return response.text(); // This returns a promise
          })
          .then(data => {
              data = encodeHTML(data.slice(1, -1))
              let popup = document.getElementById("popup");
              let overlay = document.getElementById("overlay")
              popup.style.display = 'block';
              overlay.style.display = 'block';
              const container = document.createElement('div');
              container.innerHTML = data;
              popup.innerHTML = '<div id=\"popup-close-btn\">✖</div>'
              popup.appendChild(container);

              container.querySelectorAll('script').forEach(script => {
                const newScript = document.createElement('script');
                newScript.textContent = script.textContent;
                container.appendChild(newScript);
                script.parentNode.removeChild(script);
            });

              function updatePopupSize() {
                  // popup.style.width = popup.parentElement.offsetWidth * (85/100) + 'px'
                  popup.style.top = (link.getBoundingClientRect().bottom + window.scrollY) + 'px'
                  popup.focus();
              }
              window.addEventListener('resize', updatePopupSize)
              updatePopupSize()

              document.getElementById('popup-close-btn').addEventListener('click', function() {
                document.getElementById('overlay').style.display = 'none';
                document.getElementById('popup').style.display = 'none';
              });

              window.addEventListener('click', function (event) {
                    if (event.target == overlay) {
                        popup.style.display = 'none'
                        popup.innerHTML = ''
                        overlay.style.display = 'none'
                    }
                  })
          })
    }

function encodeHTML(html) {
    return html
        .replaceAll('&quot;', '"')
        .replaceAll('\\n', '');
}

function getCookie(name) {
    const cookies = document.cookie.split(';');

    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return null;
}
