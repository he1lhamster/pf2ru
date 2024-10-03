document.addEventListener('DOMContentLoaded', function () {
    const tables = document.querySelectorAll('table.need-filters'); // Select all tables that need filtering

    tables.forEach(table => {
      const filterInputs = table.querySelectorAll('.filter-input');
      const sortButtons = table.querySelectorAll('.sort-button');
      const checkboxes = table.querySelectorAll('.check-checkbox');
      const actionFilters = table.querySelectorAll('.action-filter');
      const filterInputsRange = table.querySelectorAll('.filter-input--range');
      const filterButtons = table.querySelectorAll('.filter-button');

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
      const filterTraits = table.querySelectorAll('.trait--filter');
      // const filtersTraits = Array.from(filterTags).map(tag => tag.textContent.trim().toLowerCase());

      rows.forEach(row => {
        let showRow = true;

        table.querySelectorAll('.filter-input').forEach(input => {
          const column = input.dataset.column;
          const filterValue = input.value.toLowerCase();
          // const cellValue = row.cells[column].textContent.toLowerCase();
          const cellValue = row.cells[column].getAttribute('data').toLowerCase();
          if (!cellValue.includes(filterValue)) {
              showRow = false;
          }
        });

        filterTraits.forEach(filterTrait => {
          const column = filterTrait.getAttribute('data-column')
          // const cell = ; // Assuming filterTrait applies to the first column
          const cellData = row.cells[column].getAttribute('data').toLowerCase();

          const cellDataList = cellData.split(',')

          // if (!cellDataList.includes(filterTrait.textContent.toLowerCase())) {
          if (!cellDataList.some(item => item.includes(filterTrait.textContent.toLowerCase()))) {
            showRow = false;
          }
        });

        table.querySelectorAll('.filter-input--range').forEach(input => {
          const column = input.dataset.column;
          let fromValue = null
          let toValue = null
          const cellValue = parseInt(row.cells[column].getAttribute('data').toLowerCase())

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

        const activeActionFilters = table.querySelectorAll('.action-filter--active');
        if (activeActionFilters.length > 0) {
          let hasActiveValue = false;
          activeActionFilters.forEach(span => {
            const column = span.dataset.column;
            const cell = row.cells[column];
            const cellValue = cell.getAttribute('data');
            if (cellValue === span.getAttribute('data')) {
              hasActiveValue = true;
            }
          });
          showRow = hasActiveValue;
        }

        row.style.display = showRow ? '' : 'none';
        //

        table.querySelectorAll('.check-checkbox').forEach((checkbox) => {
          if (checkbox.checked) {
            const column = checkbox.dataset.column;
            // const cellValue = row.cells[column].textContent.toLowerCase();
            const cellValue = row.cells[column].getAttribute('data').toLowerCase();
            if (cellValue !== 'true' && checkbox.checked) {
              showRow = false;
            }
          }
        });

        row.style.display = showRow ? '' : 'none';
      });
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
    };

  });
