const cardWidth = 230
const cardBackHeight = 314
const cardFrontHeight = 288


function calculateFontSize(htmlText, maxHeight, maxWidth, currentFont) {
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = htmlText;
  // tempDiv.style.lineHeight = '1em';

  document.body.appendChild(tempDiv);
  tempDiv.style.width = maxWidth + 'px';
  tempDiv.style.height = maxHeight + 'px';
  tempDiv.style.fontSize = currentFont + 'px';
  tempDiv.style.overflow = 'hidden';

  let fontSize = currentFont;

  while (tempDiv.scrollHeight > maxHeight || tempDiv.scrollWidth > maxWidth) {
      fontSize -= 0.2;
      tempDiv.style.fontSize = fontSize + 'px';
  }
  console.log(maxHeight, maxWidth, fontSize)
  document.body.removeChild(tempDiv);
  return fontSize;
}

// return  [optimalFont, numberCards];
function findMaxFontSize(text, firstTextBlock) {
  let maxHeight = firstTextBlock.clientHeight + cardBackHeight
    console.log('---'+maxHeight)
  const currentFont = 12

  let optimalFont = calculateFontSize(text, maxHeight, cardWidth, currentFont)
  let numberCards = 1

  while (optimalFont < 8) {
    numberCards +=1
    maxHeight = maxHeight + cardFrontHeight + cardBackHeight
    optimalFont = calculateFontSize(text, maxHeight, cardWidth, currentFont)
  }
  console.log(optimalFont)

  return  [optimalFont - 0.2, numberCards ];
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

  let parts = []
  function cloneStyles(sourceElement, targetElement) {
      const computedStyle = window.getComputedStyle(sourceElement);
      targetElement.style.fontSize = fontSize + 'px';
      targetElement.style.fontFamily = computedStyle.fontFamily;;
      targetElement.style.width = cardWidth + 'px';
      targetElement.style.height = computedStyle.height;;
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
      targetElement.style.border = computedStyle.border;
      targetElement.style.backgroundColor = computedStyle.verticalAlign;

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
      container.style.position = 'absolute';
      // container.style.visibility = 'hidden';
      document.body.appendChild(container);

      // Clone styles from the current element
      cloneStyles(elements[currentElementIndex], container);
      copyCustomTagStyles('thhead', container);
      copyCustomTagStyles('trow', container);
      copyCustomTagStyles('tdcell', container);

      currentText = '';

      while (words.length > 0) {
          const word = words[0];
          container.innerHTML = currentText + word.replace(/\n{3,}/g, '\n\n');
          // Check if the current text fits in the current element
          if (container.scrollWidth > elements[currentElementIndex].clientWidth || container.scrollHeight > elements[currentElementIndex].clientHeight) {

              break;
          } else {
              currentText += word.replace(/\n{3,}/g, '\n\n');
              words.shift();
          }
      }
            console.log(container.scrollHeight, elements[currentElementIndex].clientHeight)

        console.log(container.innerHTML)

      elements[currentElementIndex].innerHTML = currentText;
      parts.push(currentText)
      //console.log(currentText)

      document.body.removeChild(container);

      currentElementIndex++;
  }
  return parts
}

function setHeaderBgColor() {
      const mainElement = document.getElementById('main-frame')
      if (mainElement) {
        const cardType = mainElement.getAttribute('card-type')
        const cardTypeColors = {
          'equipment': 'rgb(226 210 162)',
          // 'spell': 'rgb(204 224 233)',
          'spell': 'rgb(237 236 211)',
          'ritual': 'rgb(212 190 213)',
        }
        if (cardType && cardTypeColors[cardType]){
          const headerDivs = document.querySelectorAll('.header')
          headerDivs.forEach(span => {
            span.style.backgroundColor = cardTypeColors[cardType]
          })
        // mainElement.style.backgroundColor = cardTypeColors[cardType]
      }
    }
  }

// window.addEventListener('load', setHeaderBgColor);

