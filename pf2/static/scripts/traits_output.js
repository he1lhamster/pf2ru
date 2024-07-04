 function traitsOutputHover() {
    const traitElements = document.querySelectorAll('.item-link--traits-output');
    const traitTextDiv = document.querySelector('.trait-text');
    let hoverTimeout;

    traitElements.forEach(element => {
        element.addEventListener('mouseenter', event => {
            hoverTimeout = setTimeout(() => {
                const itemId = element.getAttribute('itemid');
                // const itemLang = element.getAttribute('itemLang');

                fetch(`/api/traits/${itemId}?lang=${globalLang}`)
                    .then(response => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! status: ${response.status}`);
                            }
                            return response.json();
                        })
                    .then(data => {
                        data = JSON.parse(data)
                        text_output = encodeHTML(data.text_output)
                        traitTextDiv.innerHTML = text_output;
                        traitTextDiv.style.display = 'block';
                    })
                    .catch(error => console.error('Error fetching trait data:', error));
            }, 100);
        });

        element.addEventListener('mousemove', event => {
            traitTextDiv.style.left = `${event.pageX + 10}px`;
            traitTextDiv.style.top = `${event.pageY + 10}px`;
        });

        element.addEventListener('mouseleave', () => {
            clearTimeout(hoverTimeout);
            traitTextDiv.style.display = 'none';
            traitTextDiv.textContent = '';
        });
    });
}

 document.addEventListener('DOMContentLoaded', () => {
     setTimeout(() => {
          traitsOutputHover();
     }, 2000)
 })