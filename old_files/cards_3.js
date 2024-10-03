const cardWidth = 230
const cardBackHeight = 314
const cardFrontHeight = 288


function calculateFontSize(htmlText, maxHeight, maxWidth, currentFont) {

    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = htmlText;
    tempDiv.style.display = 'block';
    tempDiv.style.position = 'absolute';

    tempDiv.style.lineHeight = '1em';

    document.body.appendChild(tempDiv);
    // tempDiv.style.width = maxWidth + 'px';
    // tempDiv.style.height = maxHeight + 'px';

    const computedStyle = window.getComputedStyle(document.getElementById('text1-1'));
      // tempDiv.style.fontFamily = computedStyle.fontFamily;
      tempDiv.style.fontFamily = 'Roboto';
      // tempDiv.style.border = computedStyle.border;
      // tempDiv.style.boxSizing = computedStyle.boxSizing;
      // tempDiv.style.lineHeight = computedStyle.lineHeight;
      tempDiv.style.letterSpacing = computedStyle.letterSpacing;
      tempDiv.style.overflow = 'hidden';
      tempDiv.style.width = cardWidth + 'px';
      tempDiv.style.height = maxHeight + 'px';
      tempDiv.style.fontSize = currentFont + 'px';

  let fontSize = currentFont;

  while (tempDiv.scrollHeight > maxHeight || tempDiv.scrollWidth > maxWidth) {
      fontSize -= 0.2;
      tempDiv.style.fontSize = fontSize + 'px';
  }
  document.body.removeChild(tempDiv);
  return fontSize;
}

// return  [optimalFont, numberCards, ];
function findMaxFontSize(text) {
  const firstTextBlock = document.getElementById("text1-1")
  let maxHeight = firstTextBlock.clientHeight + cardBackHeight - 10
  // let maxHeight = getComputedStyle(firstTextBlock).height + cardBackHeight

  const currentFont = 12.2

  let optimalFont = calculateFontSize(text, maxHeight, cardWidth, currentFont)
  let numberCards = 1

  while (optimalFont < 8) {
    numberCards +=1
    maxHeight = maxHeight + cardFrontHeight + cardBackHeight -10
    optimalFont = calculateFontSize(text, maxHeight, cardWidth, currentFont)
  }

  return  [optimalFont - 0.2, numberCards, ];
}

function splitText(htmlText) {
    const result = [];
    const selfClosingTagRegex = /<(br|hr|img|input|link|meta|source|wbr|param|area|base|col)(\s[^>]*)?\/?>/i;
    let i = 0;

    while (i < htmlText.length) {
        if (htmlText[i] === '<') {
            // Check for self-closing tag
            const selfClosingMatch = htmlText.slice(i).match(selfClosingTagRegex);
            if (selfClosingMatch && selfClosingMatch.index === 0) {
                result.push(selfClosingMatch[0]);
                i += selfClosingMatch[0].length;
                continue;
            }

            // Handle opening tag and nested tags
            let tagStart = i;
            let tagEnd = i;
            let depth = 0;

            do {
                if (htmlText[tagEnd] === '<') {
                    if (htmlText[tagEnd + 1] !== '/') {
                        depth++;
                    } else {
                        depth--;
                    }
                }
                tagEnd++;
            } while (depth > 0 && tagEnd < htmlText.length);

            // Find the closing tag that matches the last opened tag
            while (htmlText[tagEnd] !== '>') {
                tagEnd++;
            }
            tagEnd++;

            result.push(htmlText.slice(tagStart, tagEnd));
            i = tagEnd;
        } else if (htmlText[i].match(/\s/)) {
            // Handle whitespace
            let spaceEnd = i;
            while (spaceEnd < htmlText.length && htmlText[spaceEnd].match(/\s/)) {
                spaceEnd++;
            }
            result.push(htmlText.slice(i, spaceEnd));
            i = spaceEnd;
        } else {
            // Handle word
            let wordEnd = i;
            while (wordEnd < htmlText.length && !htmlText[wordEnd].match(/\s|</)) {
                wordEnd++;
            }
            result.push(htmlText.slice(i, wordEnd));
            i = wordEnd;
        }
    }

    // Filter out empty strings caused by consecutive spaces
    return result.filter(element => element.length > 0);
}

function distributeText(text, elements, fontSize) {

  let _parts = []
  // Function to clone the necessary styles
  function cloneStyles(sourceElement, targetElement) {
      const computedStyle = window.getComputedStyle(sourceElement);
      targetElement.style.fontSize = fontSize + 'px';
      // targetElement.style.fontFamily = computedStyle.fontFamily;
      targetElement.style.fontFamily = 'Roboto';

      targetElement.style.width = cardWidth + 'px';
      targetElement.style.height = computedStyle.height;
      targetElement.style.padding = computedStyle.padding;
      targetElement.style.border = computedStyle.border;
      targetElement.style.boxSizing = computedStyle.boxSizing;
      targetElement.style.lineHeight = computedStyle.lineHeight;
      targetElement.style.letterSpacing = computedStyle.letterSpacing;
      // copy custom tags
      targetElement.style.tableLayout = computedStyle.tableLayout;
      targetElement.style.borderCollapse = computedStyle.borderCollapse;
      targetElement.style.verticalAlign = computedStyle.verticalAlign;

      targetElement.style.display = computedStyle.display;
      targetElement.style.flex = computedStyle.flex;
      targetElement.style.flexDirection = computedStyle.flexDirection;
      // targetElement.style.verticalAlign = computedStyle.verticalAlign;

  }

  function copyCustomTagStyles(tagName, targetElement) {
      const elementsWithTag = document.querySelectorAll(tagName);
      if (elementsWithTag.length > 0) {
          const firstElement = elementsWithTag[0];
          cloneStyles(firstElement, targetElement);
      }
  }

    const words = splitText(text)

    let currentElementIndex = 0;
    let currentText = '';

  // Clear all elements
  elements.forEach(element => element.innerHTML = '');

  while (currentElementIndex < elements.length && words.length > 0) {
      // Create a temporary container to measure text
      const container = document.createElement('div');
      container.style.display = 'block';
      container.style.position = 'absolute';
      container.style.visibility = 'hidden';
      document.body.appendChild(container);

      // Clone styles from the current element
      cloneStyles(elements[currentElementIndex], container);
      // Copy styles for custom tags from actual document to temporary container
      copyCustomTagStyles('thhead', container);
      copyCustomTagStyles('trow', container);
      copyCustomTagStyles('tdcell', container);

      currentText = '';

      while (words.length > 0) {
          let word = words[0]; // Peek at the first word
          container.innerHTML = currentText + word;

          // Check if the current text fits in the current element
          if (container.scrollWidth > elements[currentElementIndex].clientWidth || container.scrollHeight > elements[currentElementIndex].clientHeight) {

            break; // If it doesn't fit, break the loop
          } else {
              // If it fits, update the current text and remove the word from the list
              currentText += word;
              words.shift(); // Remove the first word
          }
      }

      elements[currentElementIndex].innerHTML = currentText;
      _parts.push(currentText)

      // Clean up the temporary container
      document.body.removeChild(container);

      // Move to the next element
      currentElementIndex++;
  }

  // If there are remaining words and elements are exhausted, fill the last element with remaining text
  if (words.length > 0 && currentElementIndex >= elements.length) {
      elements[elements.length - 1].innerHTML += words.join('');
  }
  return _parts
}

function extractContent(text1, typeLevel, itemName) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(text1, 'text/html');

    // Select all <h2> elements
    const headings = Array.from(doc.querySelectorAll('h2'));
    let result = '';
    let foundHeadings = [];

    // Iterate over all headings to find those with a matching <span class="item-type">
    for (let i = 0; i < headings.length; i++) {
        const heading = headings[i];
        const span = heading.querySelector(`span.item-type`);

        // Check if the span text matches typeLevel
        if (span?.textContent === typeLevel) {
            foundHeadings.push(heading);
        }
    }

    // If no matching <h2> is found, return the original text as HTML
    if (foundHeadings.length === 0) {
        return text1;
    }

    // If multiple matching <h2>s are found, compare their text with itemName
    const normalizedItemName = itemName.toLowerCase();
    let matchingHeading;

    if (foundHeadings.length === 1) {
        matchingHeading = foundHeadings[0];  // Only one match, no need to compare itemName
    } else {
        // Compare the heading text (before the <span>) with itemName
        for (let heading of foundHeadings) {
            const headingClone = heading.cloneNode(true);
            const span = headingClone.querySelector('span');
            if (span) {
                span.remove();  // Remove the <span> to compare only the <h2> text before it
            }
            const headingText = headingClone.textContent.trim().toLowerCase();

            if (headingText === normalizedItemName) {
                matchingHeading = heading;
                break;
            }
        }
    }

    // If no heading matches itemName, return the original text as HTML
    if (!matchingHeading) {
        return text1;
    }

    // Get everything before the first <h2>
    let firstH2 = doc.body.querySelector('h2');
    if (firstH2) {
        let currentNode = doc.body.firstChild;
        while (currentNode && currentNode !== firstH2) {
            result += currentNode.outerHTML || currentNode.textContent;
            currentNode = currentNode.nextSibling;
        }
    }

    // Include the matching <h2> and content after it until the next <h2>
    result += matchingHeading.outerHTML;
    let nextSibling = matchingHeading.nextSibling;
    while (nextSibling && nextSibling.nodeName !== 'H2') {
        result += nextSibling.outerHTML || nextSibling.textContent;
        nextSibling = nextSibling.nextSibling;
    }

    // Return the result as a rendered HTML string
    return result.trim();
}

window.onload = function() {
  const elements = [
    document.getElementById('text1-1'),
    document.getElementById('text2-1'),
    document.getElementById('text1-2'),
    document.getElementById('text2-2'),
    document.getElementById('text1-3'),
    document.getElementById('text2-3'),
    document.getElementById('text1-4'),
    document.getElementById('text2-4')
  ];

  const itemText = document.getElementById('text1-1').innerHTML;
  const itemLevel = document.getElementById('level-1').innerHTML
  const itemName = document.getElementById('name-1').innerHTML
  const _textCard = extractContent(itemText, itemLevel, itemName)
  document.getElementById('text1-1').innerHTML = _textCard
    const textCard = document.getElementById('text1-1').innerHTML;

  let [fontSize, numCards] = findMaxFontSize(textCard);

  if (textCard.includes('<trow>')) {
    fontSize -= 0.2
  }
  for (let element of elements) {
    element.style.fontSize= fontSize + 'px'
  }

  let parts = distributeText(textCard, elements, fontSize)

  window.opener.postMessage(JSON.stringify({
      id: document.getElementById('item-id').innerHTML,
      name: document.getElementById('name-1').innerHTML,
      type_level: document.getElementById('level-1').innerHTML,
      traits: document.getElementById('traits-1').innerHTML,
      category: document.getElementById('category-1').innerHTML,
      fontSize: fontSize,
      numberCards: numCards,
      parts: parts
  }), "*");
  window.close();

}


