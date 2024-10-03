
        const nameInput = document.getElementById('card-name');
        const cardsDropdown = document.getElementById('card-dropdown');
        const cardsForGenerate = document.getElementById('cards-for-generate');
        const generateBtn = document.getElementById('card-generate-btn');
        let typingTimer;
        const typingCardDelay = 500;
        let items = [] // resulting array with parts and font sizes
        let messagePromises = [];
        let shadowHost = document.getElementById('shadow-host');
        let shadowRoot = shadowHost.attachShadow({ mode: 'open' });

        // Search for items in MS
        nameInput.addEventListener('input', () => {
            clearTimeout(typingTimer);
            const query = nameInput.value;
            const cardItemType= document.getElementById('card-item-type').value

            if (query.length > 2) {
                typingTimer = setTimeout(async () => {
                    cardsDropdown.innerHTML = '<i>loading...</i>';

                    // const cardSearchEndpoint = 'https://pf2.ru/meilisearch/indexes/content/search';
                    // const cardApiKey = 'f573319f8d0ad54c589c1e3f75366c6756c2eea35522b8c32cffa61f2ed8114a';

                    const cardApiKey = '3b0cd156522db89b6bbcf448083ae47ef7c499958a7749abe7e0633ddf03e665';
                    const cardSearchEndpoint = 'http://127.0.0.1:7700/indexes/content/search';
                    const searchOptions = {
                        filter: [`type=${cardItemType}`],
                        attributesToSearchOn: ['name', 'rus_name']
                    };

                    const response = await fetch(cardSearchEndpoint, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${cardApiKey}`
                        },
                        body: JSON.stringify({
                            q: `${query}`,
                            ...searchOptions
                        })
                    });
                    const data = await response.json();
                    const hits = data.hits;
                    const results = [];

                    hits.forEach(hit => {
                        results.push({
                            id: hit.uid.split('_')[1],
                            name: hit.name,
                            rus_name: hit.rus_name,
                            type_level: hit.type_level,
                            rus_type_level: hit.rus_type_level,
                            type: hit.type,
                            url: hit.url,
                            variants: hit.variants,
                        });

                        if (hit.variants && hit.variants.length > 0) {
                            hit.variants.forEach(variant => {
                                results.push({
                                    id: hit.uid.split('_')[1],
                                    name: variant.name,  // Use the variant's name
                                    rus_name: variant.rus_name,  // Use the variant's rus_name
                                    type_level: `Item ${variant.level}`,  // Set type_level based on the variant's level
                                    rus_type_level: `Предмет ${variant.level}`,  // Set rus_type_level based on the variant's level
                                    type: hit.type,
                                    url: hit.url,
                                    variants: [],
                                });
                            });
                        }
                    });
                    // hits.map(hit => ({
                    //     id: hit.uid.split('_')[1],
                    //     name: hit.name,
                    //     rus_name: hit.rus_name,
                    //     type_level: hit.type_level,
                    //     rus_type_level: hit.rus_type_level,
                    //     type: hit.type,
                    //     url: hit.url,
                    //     variants: hit.variants,
                    // }));

                    cardsDropdown.innerHTML = '';
                    results.forEach(result => {
                        const resultDiv = document.createElement('div');
                        resultDiv.classList.add('cards-search-item')
                        resultDiv.innerHTML = `${result.rus_name} / ${result.name} (${result.rus_type_level})`;
                        // resultDiv.dataset.id = result.id;
                        // resultDiv.dataset.type = result.type;
                        // resultDiv.dataset.name = result.name;
                        // resultDiv.dataset.typeLevel = result.type_level;
                        // resultDiv.dataset.traits_output = result.traits_output ;
                        // resultDiv.dataset.text_output = result.text_output ;
                        // resultDiv.dataset.rus_traits_output = result.rus_traits_output ;
                        // resultDiv.dataset.rus_text_output = result.rus_text_output ;

                        resultDiv.addEventListener('click', () => {
                            const itemDiv = document.createElement('div');
                            itemDiv.classList.add('selected-item');
                            itemDiv.dataset.cardItemType = cardItemType;
                            itemDiv.dataset.itemId = result.id;
                            itemDiv.dataset.itemName = result.name
                            itemDiv.dataset.itemTypeLevel = result.type_level
                            itemDiv.dataset.itemRusName = result.rus_name
                            itemDiv.dataset.itemRusTypeLevel = result.rus_type_level

                            itemDiv.innerHTML = `
                                <span><a class="item-link" href="${result.url}">${result.rus_name} / ${result.name} (${result.rus_type_level})</a></span>
                                <span class="remove-btn">&times;</span>
                            `;
                            itemDiv.querySelector('.remove-btn').addEventListener('click', () => {
                                itemDiv.remove();
                                if (cardsForGenerate.children.length === 0) {
                                    cardsForGenerate.style.display = 'none';
                                    generateBtn.style.display = 'none';
                                }
                            });
                            cardsForGenerate.appendChild(itemDiv);
                            cardsForGenerate.style.display = 'block';
                            generateBtn.style.display = 'block';
                        });
                        cardsDropdown.appendChild(resultDiv);
                    });
                    cardsDropdown.style.display = 'block';
                }, typingCardDelay);
            } else {
                cardsDropdown.style.display = 'none';
            }
        });

        window.addEventListener("message", function(event) {
            const receivedDict = JSON.parse(event.data);
            let item = {
                id: parseInt(receivedDict.id),
                name: receivedDict.name,
                type_level: receivedDict.type_level,
                traits: receivedDict.traits,
                category: receivedDict.category,
                font_size: parseFloat(receivedDict.fontSize),
                cards_number: parseInt(receivedDict.numberCards),
                parts: receivedDict.parts
            };
            items.push(item)
            console.log(item.parts, item.cards_number, item.font_size)

            if (messagePromises.length > 0) {
                let promise = messagePromises.pop();
                promise.resolve();
            }
        } , false);

        generateBtn.addEventListener('click', async () => {
            items= []

            let response = await fetch('/users/cards/blank', {
                method: 'GET',
                credentials: "include"
            });
            const htmlContent = await response.text()
            const isRotated = document.getElementById('is_rotated').checked;
            const isEnglish = document.getElementById('is_english').checked;
            let newTab = window.open("", "_blank");

            let cardLang = 'ru'
            if (isEnglish) {
                cardLang = 'en'
            }

            for (let card of cardsForGenerate.children) {

                let cardBody =  JSON.stringify({
                        item_type: card.dataset.cardItemType,
                        id: parseInt(card.dataset.itemId),
                        lang: cardLang
                    })

                let response = await fetch('/users/cards/compose-card', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: cardBody,
                    credentials: "include",
                });
                if (response.ok) {
                    try {
                        let resultItem = await response.json()
                        // cardsDB.push({
                        //     itemId: card.dataset.itemId,
                        //     traits: resultItem.traits,
                        //     text: resultItem.text.replace(/<!--.*?-->/gs, ''),
                        //     name: resultItem.name,
                        //     type_level: resultItem.type_level,
                        //     category: resultItem.category,
                        // })
                        const itemName = card.dataset.itemName.replace(/<span[^>]*>.*?<\/span>/gi, '');
                        const itemRusName = card.dataset.itemRusName.replace(/<span[^>]*>.*?<\/span>/gi, '');

                        shadowRoot.innerHTML = htmlContent
                        shadowRoot.getElementById('item-id').innerHTML = card.dataset.itemId
                        shadowRoot.getElementById('traits-1').innerHTML = resultItem.traits
                        shadowRoot.getElementById('text1-1').innerHTML = resultItem.text.replace(/<!--.*?-->/gs, '');

                        if (cardLang === 'ru') {
                            shadowRoot.getElementById('name-1').innerHTML = itemRusName
                            shadowRoot.getElementById('name-2').innerHTML = itemRusName
                            shadowRoot.getElementById('name-3').innerHTML = itemRusName
                            shadowRoot.getElementById('name-4').innerHTML = itemRusName
                            shadowRoot.getElementById('level-1').innerHTML = card.dataset.itemRusTypeLevel
                        } else {
                            shadowRoot.getElementById('name-1').innerHTML = itemName
                            shadowRoot.getElementById('name-2').innerHTML = itemName
                            shadowRoot.getElementById('name-3').innerHTML = itemName
                            shadowRoot.getElementById('name-4').innerHTML = itemName
                            shadowRoot.getElementById('level-1').innerHTML = card.dataset.itemTypeLevel
                        }
                        // shadowRoot.getElementById('name-1').innerHTML = resultItem.name
                        // shadowRoot.getElementById('name-2').innerHTML = resultItem.name
                        // shadowRoot.getElementById('name-3').innerHTML = resultItem.name
                        // shadowRoot.getElementById('name-4').innerHTML = resultItem.name
                        // shadowRoot.getElementById('level-1').innerHTML = resultItem.type_level

                        if (card.dataset.cardItemType === 'equipment') {
                            shadowRoot.getElementById('category-1').innerHTML = resultItem.category
                        }
                        newTab = window.open("", "_blank");
                        newTab.document.write(shadowRoot.innerHTML);
                        newTab.document.close();
                        let messagePromise = new Promise((resolve) => {
                            messagePromises.push({ resolve }); // Store the promise resolver
                        });
                        await messagePromise;

                    } catch(error) {
                        console.error('Error parsing', error)
                        }
                } else {
                    window.alert('Что-то пошло не так...')
                }
            }

            // Send Request to App to form cards
            await Promise.all(messagePromises);
            const cardItemType= document.getElementById('card-item-type').value

            let ready_file = await fetch('/users/cards/cards-generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        item_type: cardItemType,
                        is_rotated: isRotated,
                        is_english: isEnglish,
                        cards: items
                    }),
                    credentials: "include",
                })
                .then(response => {
                    if (!response) {
                        throw new Error('Response is not ok')
                    }
                    return response.blob()
                })
                .then(blob => {
                    const downloadUrl = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = downloadUrl;
                    a.download = 'cards.zip';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(downloadUrl);
                  })
                .catch(error => {
                    console.error('There was a problem with the fetch operation:', error);
                });
        });

    document.addEventListener('click', (event) => {
        if (!cardsDropdown.contains(event.target) && !nameInput.contains(event.target)) {
            cardsDropdown.style.display = 'none';
        }
    });
    document.getElementById('card-item-type').addEventListener('change', () => {
        nameInput.value = '';
        cardsDropdown.innerHTML = '';
        cardsDropdown.style.display = 'none';
        cardsForGenerate.innerHTML = '';
        cardsForGenerate.style.display = 'none';
        generateBtn.style.display = 'none';
        document.getElementById('is_rotated').checked = true;
        document.getElementById('is_english').checked = false;
    });
