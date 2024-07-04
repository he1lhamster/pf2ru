document.addEventListener('DOMContentLoaded', function () {
    const tables = document.querySelectorAll('table.need-filters'); // Select all tables that need filtering

    tables.forEach(table => {
      const filterInputs = table.querySelectorAll('.filter-input');
      const sortButtons = table.querySelectorAll('.sort-button');
      const checkboxes = table.querySelectorAll('.check-checkbox');
      const actionFilters = table.querySelectorAll('.action-filter');
      const filterInputsRange = table.querySelectorAll('.filter-input--range');
      const filterButtons = table.querySelectorAll('.filter-button');
      const choicesButtons = table.querySelectorAll('.choice-button')

      filterButtons.forEach(button => {
        button.addEventListener('click', function () {
          const columnName = this.getAttribute('data-column');
          const input = this.previousElementSibling;
          const filterValue = input.value.trim();
          if (filterValue !== '') {
            addFilterTag(filterValue, columnName, table);
            input.value = '';
            applyFilters(table);
          }
        });
      });

      filterInputs.forEach(input => {
        input.addEventListener('input', function () { applyFilters(table); });
      });

      filterInputsRange.forEach(input => {
        input.addEventListener('input', function () { applyFilters(table); });
      });

      checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () { applyFilters(table); });
      });

      actionFilters.forEach(span => {
      span.addEventListener('click', function () { toggleActionFilter(this, table); });
      });
      function toggleActionFilter(span, table) {
        span.classList.toggle('action-filter--active');
        applyFilters(table);
      }

      choicesButtons.forEach(span => {
        span.addEventListener('click', function () { toggleChoiceButton(this, table); });
      });
      function toggleChoiceButton(span, table) {
        span.classList.toggle('choice-button--active');
        applyFilters(table);
      }

      sortButtons.forEach(button => {
        button.addEventListener('click', function () {
          const columnName = this.getAttribute('data-column');
          sortTable(columnName, table);
        });
      });
    });

    function addFilterTag(filterValue, columnName, table) {
      const traitsFilter = table.querySelector(`.traits-filter--${columnName}`);
      const span = document.createElement('span');
      span.classList.add('trait--filter');
      span.setAttribute('data-column', columnName)
      span.textContent = filterValue;
      const closeButton = document.createElement('button');
      closeButton.classList.add('trait-close-btn')
      closeButton.setAttribute('close-btn-txt', '✖')
      closeButton.addEventListener('click', function () {
        span.remove();
        applyFilters(table);
      });
      span.appendChild(closeButton);
      traitsFilter.appendChild(span);
    }

    let sortDirection = {};

    function applyFilters(table) {
      const rows = table.querySelectorAll('tbody tr:not(.table-breaker)');
      // const filtersTraits = Array.from(filterTags).map(tag => tag.textContent.trim().toLowerCase());

      rows.forEach(row => {
        let showRow = true;

        if (table.querySelector('.action-filter--active')) {
          showRow = false
          table.querySelectorAll('.action-filter--active').forEach(actionFilter => {
            const column = actionFilter.getAttribute('data-column');
            const cell = row.cells[column];
            const cellValue = cell.getAttribute('data');
            if (cellValue === actionFilter.getAttribute('data')) {
              showRow = true;
              return
            }
          });
        }

        table.querySelectorAll('.filter-input').forEach(input => {
          const column = input.getAttribute('data-column');
          const filterValue = input.value.toLowerCase();
          const cellValue = row.cells[column].getAttribute('data').toLowerCase();
          if (!cellValue.includes(filterValue)) {
            showRow = false;
          }
        });

        table.querySelectorAll('.trait--filter').forEach(filterTrait => {
          const column = filterTrait.getAttribute('data-column')
          const column2 = parseInt(column) + 1
          const cellData = row.cells[column].getAttribute('data').toLowerCase();
          const cellData2 = row.cells[column2].getAttribute('data').toLowerCase();
          const cellDataList2 = cellData2.split(',')
          const cellDataList = cellData.split(',')
          // if (!cellDataList.includes(filterTrait.textContent.toLowerCase())) {
          if ((!cellDataList.some(item => item.includes(filterTrait.textContent.toLowerCase())))
              &
              (!cellDataList2.some(item => item.includes(filterTrait.textContent.toLowerCase())))
          ) {
            showRow = false;
          }
        });

        table.querySelectorAll('.filter-input--range').forEach(input => {
          const column = input.getAttribute('data-column');
          let fromValue = null
          let toValue = null
          const cellValue = parseFloat(row.cells[column].getAttribute('data'))

          if (input.classList.contains('filter-input--range-from')) {
            fromValue = parseInt(input.value.trim())
            if (cellValue < fromValue) {
              showRow = false;
            }
          }
          if (input.classList.contains('filter-input--range-to')) {
            toValue = parseInt(input.value.trim())
            if (cellValue > toValue) {
              showRow = false;
            }
          }
        });

        table.querySelectorAll('.choice-button--active').forEach(choiceButton => {
          const column = choiceButton.getAttribute('data-column');
          const cell = row.cells[column];
          const cellValue = cell.getAttribute('data').toLowerCase().split(',');
          if ((!cellValue.some(item => item.includes(choiceButton.getAttribute('data').toLowerCase())))
          ) {
            showRow = false;
          }
        });

        table.querySelectorAll('.check-checkbox').forEach((checkbox) => {
          if (checkbox.checked) {
            const column = checkbox.getAttribute('data-column');
            // const cellValue = row.cells[column].textContent.toLowerCase();
            const cellValue = row.cells[column].getAttribute('data').toLowerCase();
            if (cellValue === '-' && checkbox.checked) {
              showRow = false;
            }
          }
        });

        row.style.display = showRow ? '' : 'none';

      });
      recalculateRowColors(table)
    }

    window.sortTable = function (columnName, table) {
      const tbody = table.querySelector('tbody');
      const rows = Array.from(tbody.querySelectorAll('tbody tr:not(.table-breaker)'));

      if (!sortDirection[columnName] || sortDirection[columnName] === 'desc') {
          sortDirection[columnName] = 'asc';
      } else {
          sortDirection[columnName] = 'desc';
      }

      rows.sort((a, b) => {
        // const cellA = a.cells[columnName].textContent.trim();
        const cellA = a.cells[columnName].getAttribute('data').toLowerCase().trim();
        // const cellB = b.cells[columnName].textContent.trim();
        const cellB = b.cells[columnName].getAttribute('data').toLowerCase().trim();

        const numericA = parseFloat(cellA);
        const numericB = parseFloat(cellB);

        if (!isNaN(numericA) && !isNaN(numericB)) {
          return sortDirection[columnName] === 'asc' ? numericA - numericB : numericB - numericA;
        } else {
          return sortDirection[columnName] === 'asc' ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
        }
      });

      tbody.innerHTML = '';

      rows.forEach(row => {
        tbody.appendChild(row);
      });
      recalculateRowColors(table)
    };

    function recalculateRowColors(table) {
        const tbody = table.querySelector('tbody');
        const rows = tbody.querySelectorAll('tr');

        let visibleRowIndex = 0;

        rows.forEach((row) => {

            const isVisible = row.style.display !== 'none';

            if (isVisible) {
                // Determine whether the row should be odd or even based on its position in the filtered list
                const shouldBeOdd = visibleRowIndex % 2 === 0;
                const cells = row.querySelectorAll('td');
                cells.forEach((cell) => {
                    cell.style.backgroundColor = shouldBeOdd ? 'white' : 'rgb(242 ,242 ,242)';
                });
                // Increment the visible row index
                visibleRowIndex++;
            }
        });
    }
});
