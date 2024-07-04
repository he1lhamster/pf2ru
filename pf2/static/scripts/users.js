
let googleButtons = document.querySelectorAll(".google-button");
googleButtons.forEach(googleBtn => {
    googleBtn.addEventListener('click', async function(event) {
        event.preventDefault();
        const response = await fetch('/users/auth/google/authorize');
        if (response.ok) {
            const data = await response.json();
            window.location.href = data.authorization_url;
        } else {
            alert('Авторизация через Google не удалась. Попробуйте заново.');
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const loginMenu = document.getElementById('usermenu-login');
    const logoutMenu = document.getElementById('usermenu-logout');
    const loginDropdown = document.getElementById('login-dropdown');
    const logoutDropdown = document.getElementById('logout-dropdown');
    const loginForm = document.getElementById('login-form');
    const logoutButton = document.getElementById('logout-button');

    // Toggle dropdowns on click
    if (loginMenu) {
        loginMenu.addEventListener('click', () => {
             loginDropdown.style.display = loginDropdown.style.display === 'flex' ? 'none' : 'flex';
        });

        // Login form submission
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(loginForm);
            const response = await fetch('/users/auth/jwt/login', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                window.location.reload();
            } else {
                alert('Ошибка входа. Проверьте свои данные');
            }
        });
    }

    if (logoutMenu) {
        logoutMenu.addEventListener('click', () => {
            logoutDropdown.style.display = logoutDropdown.style.display === 'flex' ? 'none' : 'flex';
        });
        // Logout button
        logoutButton.addEventListener('click', async () => {
            const response = await fetch('/users/auth/logout', {
                method: 'POST',
            });

            if (response.ok) {
                window.location.href = '/';
            } else {
                alert('Попытка выхода неуспешна. Пожалуйста, попробуйте заново');
            }
        });
    }

    // Close dropdowns when clicking outside
    document.addEventListener('click', (event) => {
        if (loginMenu && !loginMenu.contains(event.target) && !loginDropdown.contains(event.target)) {
            loginDropdown.style.display = 'none';
        }
        if (logoutMenu && !logoutMenu.contains(event.target) && !logoutDropdown.contains(event.target)) {
            logoutDropdown.style.display = 'none';
        }
    });
});

// update user
if (document.getElementById('updateUserForm')) {
    document.getElementById('updateUserForm').addEventListener('submit', async function (event) {
        event.preventDefault();

        const username = document.getElementById('update-username').value.trim();
        // const password = document.getElementById('update-password').value.trim();
        const email = document.getElementById('update-email').value;

        if (username) {

            const responseValid = await fetch('/users/is-valid-update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',

            },
            credentials: "include",
            body: JSON.stringify({
                username: username,
                // password: password,
                email: email
            })
            });

            if (responseValid.ok) {
                const result = await responseValid.json()
                const updateUsername = result.username // need to prevent null username value

                const response = await fetch('/users/api/me', {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',

                    },
                    credentials: "include",
                    body: JSON.stringify({
                        username: updateUsername,
                        // password: password,
                        email: email
                    })
                });

                if (response.ok) {
                    alert('Информация о пользователе обновлена');
                    window.location.reload()
                } else {
                    alert('Неудалось обновить информацию о пользователе. Попробуйте еще раз');
                }
                // window.location.reload()
            } else {
                const errorData = await responseValid.json();
                alert(errorData.detail);
            }
        } else {
            alert('Заполните хотя бы одно поле')
        }
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    const themesContainer = document.getElementById('archive-themes');
    const notePopup = document.getElementById('create-note-popup-archive');
    if (notePopup) {
        const closePopup = notePopup.querySelector('.popup-archive-close');
        closePopup.addEventListener('click', () => {
            notePopup.style.display = 'none';
        });
        window.addEventListener('click', (event) => {
        if (event.target === notePopup) {
            notePopup.style.display = 'none';
        }
        });
    }
    const createThemeBtn = document.getElementById('create-theme-button')
    if (createThemeBtn) {
        createThemeBtn.addEventListener('click', () => {
            createThemePopup.style.display = 'flex';
        });
    }
    const createThemePopup = document.getElementById('create-theme-popup-archive')
    if (createThemePopup) {
        const closeThemePopup = createThemePopup.querySelector('.popup-archive-close')
        closeThemePopup.addEventListener('click', () => {
            createThemePopup.style.display = 'none';
        });
    }

    let currentThemeId = null; // To store the theme ID for the note being created

    // Function to toggle expand/collapse of theme details
    function toggleExpand(element) {
        if (element.style.display === 'none') {
            element.style.display = 'flex';
        } else {
            element.style.display = 'none';
        }
    }

    function trans(value) {
        const transButtons = {
            "Edit": "Редактировать",
            "Delete": "Удалить",
            "Change Bookshelf": "Сменить полку",
            "Add Note": "Добавить заметку"
        }
        if (value in transButtons && globalLang === 'ru') {
            return transButtons[value]
        }
        return value
    }

    // Function to confirm theme deletion
    async function confirmDeleteTheme(themeId) {
        if (confirm('Are you sure you want to delete this theme?')) {
            try {
                const response = await fetch(`/api/archive/themes/${themeId}`, {
                    method: 'DELETE',
                    credentials: 'include'
                });

                if (response.ok) {
                    const themeToRemove = themesContainer.querySelector(`.theme[data-theme-id="${themeId}"]`);
                    if (themeToRemove) {
                        themeToRemove.remove();
                    }
                } else {
                    throw new Error('Failed to delete theme');
                }
            } catch (error) {
                console.error('Error deleting theme:', error);
            }
        }
    }

    // Function to create individual note element
    async function createNoteElement(note) {
        const noteDiv = document.createElement('div');
        noteDiv.classList.add('note');
        noteDiv.setAttribute('data-note-id', note.id);

        const noteDetails = document.createElement('div');
        noteDetails.classList.add('note--details');
        noteDetails.style.display = 'none';

        const noteHeader = document.createElement('div');
        noteHeader.classList.add('note--header');
        noteHeader.innerHTML = `<span class="note--status"></span>${note.title}`;
        const noteStatus = noteHeader.getElementsByClassName('note--status')[0]
        noteHeader.addEventListener('click', () => {
            toggleExpand(noteDetails)
            noteStatus.classList.toggle('note--status--active')

        });

        const noteText = document.createElement('p');

        if (note.item_type && note.item_id) {

            const response = await fetch(`/api/${note.item_type}/${note.item_id}`, {
                method: 'GET',
                credentials: "include"
            });

            if (response.ok) {
                let resultItem = await response.json()
                resultItem = JSON.parse(resultItem)
                noteText.innerHTML = `<div class="note--item-field">
                                            <span class="rhombus rhombus--with-margin" itemID=${note.item_id} itemType=${note.item_type} onclick="getItem(this)"></span>
                                            <a class="textlink" href="${resultItem.url}">${resultItem.name}</a>
                                            <span class="note--item-field--level">${resultItem.type_level}</span>
                                       </div>
                                       ${note.text}`;
            } else {
                noteText.innerHTML = `не удалось загрузить данные об объекте.<br>${note.text}`;
            }

        } else {
            noteText.textContent = note.text;
        }

        noteDetails.appendChild(noteText);

        const actionsDiv = document.createElement('div');
        actionsDiv.classList.add('note--actions');

        const editButton = document.createElement('button');
        editButton.classList.add('note--button');
        editButton.textContent = trans('Edit');
        editButton.addEventListener('click', () => toggleEditNote(note, noteDetails));

        const deleteButton = document.createElement('button');
        deleteButton.classList.add('note--button');
        deleteButton.textContent = trans('Delete');
        deleteButton.addEventListener('click', () => confirmDeleteNote(note.id, note.archive_theme_id));

        const changeThemeButton = document.createElement('button');
        changeThemeButton.classList.add('note--button');
        changeThemeButton.textContent = trans('Change Bookshelf');
        changeThemeButton.addEventListener('click', () => openChangeThemePopup(note));

        actionsDiv.appendChild(editButton);
        actionsDiv.appendChild(deleteButton);
        actionsDiv.appendChild(changeThemeButton);

        noteDetails.appendChild(actionsDiv);

        noteDiv.appendChild(noteHeader);
        noteDiv.appendChild(noteDetails);

        return noteDiv;
    }

    // Function to open note creation popup-archive
    function openCreateNotePopup(themeId) {
        currentThemeId = themeId;
        notePopup.style.display = 'flex';
    }

    // Function to create "Create Note" button for each theme
    function addCreateNoteButton(theme, themeDetails) {
        const createNoteButton = document.createElement('button');

        createNoteButton.classList.add('add-note-button')
        createNoteButton.innerHTML = `<img class="add-note-button--icon" src="/static/icons/plus-icon-color.svg" alt="Add">${trans('Add Note')}`;
        createNoteButton.addEventListener('click', () => openCreateNotePopup(theme.id));

        themeDetails.appendChild(createNoteButton);
    }

    // Function to create individual theme element
    function createThemeElement(theme) {
        const themeDiv = document.createElement('div');
        themeDiv.classList.add('theme');
        themeDiv.setAttribute('data-theme-id', theme.id);

        const themeHeader = document.createElement('div');
        themeHeader.classList.add('theme--header');
        themeHeader.innerHTML = `<span class="theme--status"></span>${theme.name}`;
        const themeStatus = themeHeader.getElementsByClassName('theme--status')[0]
        themeHeader.addEventListener('click', () => {
            toggleExpand(themeDetails)
            themeStatus.classList.toggle('theme--status--active')

        });

        const themeDetails = document.createElement('div');
        themeDetails.classList.add('theme--details');
        themeDetails.style.display = 'none';

        const descriptionParagraph = document.createElement('p');
        descriptionParagraph.classList.add('theme--description')
        descriptionParagraph.textContent = theme.description;
        themeDetails.appendChild(descriptionParagraph);

        const actionsDiv = document.createElement('div');
        actionsDiv.classList.add('theme--actions');

        const editButton = document.createElement('button');
        editButton.classList.add('theme--button')
        editButton.textContent =  trans('Edit');
        editButton.addEventListener('click', () => toggleEditTheme(theme, themeDetails));

        const deleteButton = document.createElement('button');
        deleteButton.classList.add('theme--button')
        deleteButton.textContent = trans('Delete');
        deleteButton.addEventListener('click', () => confirmDeleteTheme(theme.id));

        actionsDiv.appendChild(editButton);
        actionsDiv.appendChild(deleteButton);

        themeDetails.appendChild(actionsDiv);

        // TODO: Add search - add script to add notes from profile
        // addCreateNoteButton(theme, themeDetails);

        themeDiv.appendChild(themeHeader);
        themeDiv.appendChild(themeDetails);

        return themeDiv;
    }

    const createNoteForm = document.getElementById('create-note-form')
    if (createThemePopup) {
        createNoteForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const form = event.target;
            const note = {
                item_type: form.item_type.value,
                item_id: form.item_id.value,
                title: form.title.value,
                text: form.text.value,
                archive_theme_id: currentThemeId
            };

            try {
                const response = await fetch(`/api/archive/themes/${currentThemeId}/notes`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify(note)
                });

                if (response.ok) {
                    const createdNote = await response.json();
                    const themeDetails = document.querySelector(`.theme[data-theme-id="${currentThemeId}"] .theme--details`);
                    themeDetails.appendChild(await createNoteElement(createdNote));
                    notePopup.style.display = 'none';
                    form.reset();
                } else {
                    throw new Error('Failed to create note');
                }
            } catch (error) {
                console.error('Error creating note:', error);
            }
        });
    }

    // Function to confirm note deletion
    async function confirmDeleteNote(noteId, themeId) {
        if (confirm('Are you sure you want to delete this note?')) {
            try {
                const response = await fetch(`/api/archive/themes/${themeId}/notes/${noteId}`, {
                    method: 'DELETE',
                    credentials: 'include'
                });

                if (response.ok) {
                    const noteToRemove = document.querySelector(`.note[data-note-id="${noteId}"]`);
                    if (noteToRemove) {
                        noteToRemove.remove();
                    }
                } else {
                    throw new Error('Failed to delete note');
                }
            } catch (error) {
                console.error('Error deleting note:', error);
            }
        }
    }

    // Function to fetch themes and display them along with their notes
    async function fetchThemes() {
        try {
            const response = await fetch('/api/archive/themes', {
                method: 'GET',
                credentials: 'include'
            });

            if (response.ok) {
                const themes = await response.json();
                themesContainer.innerHTML = '';
                for (const theme of themes) {
                    const themeElement = createThemeElement(theme);
                    const notesResponse = await fetch(`/api/archive/themes/${theme.id}/notes`, {
                        method: 'GET',
                        credentials: 'include'
                    });

                    if (notesResponse.ok) {
                        const notes = await notesResponse.json();
                        const notesContainer = document.createElement('div');
                        notesContainer.classList.add('theme--notes-container');
                        for (const note of notes) {
                            const noteElement = await createNoteElement(note);
                            notesContainer.appendChild(noteElement);
                        }
                        themeElement.querySelector('.theme--details').appendChild(notesContainer);
                    } else {
                        throw new Error('Failed to fetch notes for theme');
                    }

                    themesContainer.appendChild(themeElement);
                }
            } else {
                throw new Error('Failed to fetch themes');
            }
        } catch (error) {
            console.error('Error fetching themes:', error);
        }
    }

    const themeForm = document.getElementById('themeForm')
    if (themeForm) {
        themeForm.addEventListener('submit', async function (event) {
            const archiveThemes = document.getElementById('archive-themes');
            const form = event.target
            event.preventDefault();

            const name = form.elements['name'].value;
            const description = form.elements['description'].value;

            try {
                const response = await fetch('/api/archive/themes', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: "include",
                    body: JSON.stringify({
                        archive_id: null,
                        name: name,
                        description: description
                    })
                });

                if (!response.ok) {
                    throw new Error('Failed to create theme');
                }

                const theme = await response.json();

                // Append the new theme to the UI
                const themeElement = createThemeElement(theme);
                archiveThemes.appendChild(themeElement);

                // Clear form inputs
                form.reset();
                document.getElementById('create-theme-popup-archive').style.display = 'none'
                // form.remove();

            } catch (error) {
                console.error('Error:', error);
            }
        });
    }

    // Function to toggle edit form for a theme
    async function toggleEditTheme(theme, themeDetailsElement) {
        // Get current theme details elements
        const themeHeader = themeDetailsElement.previousElementSibling;
        const descriptionParagraph = themeDetailsElement.querySelector('p');

        if (!themeHeader || !descriptionParagraph) return;


        const currentName = themeHeader.textContent.trim();
        const currentDescription = descriptionParagraph.textContent.trim();

        document.querySelectorAll('.theme-form').forEach(openForm=> {
            openForm.remove()
        })

        // Create form elements
        const form = document.createElement('form');
        form.classList.add('theme-form');

        const nameInput = document.createElement('input');
        nameInput.classList.add('theme-form--input')
        nameInput.type = 'text';
        nameInput.value = currentName;
        form.appendChild(nameInput);

        const descriptionInput = document.createElement('textarea');
        descriptionInput.classList.add('theme-form--textarea')
        descriptionInput.value = currentDescription;
        form.appendChild(descriptionInput);

        const updateButton = document.createElement('button');
        updateButton.classList.add('theme-form--button')
        updateButton.textContent = 'Update';
        updateButton.type = 'button';
        updateButton.addEventListener('click', async () => {
            try {
                const response = await fetch(`/api/archive/themes/${theme.id}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({
                        id: theme.id,
                        name: nameInput.value,
                        description: descriptionInput.value
                    })
                });

                if (response.ok) {
                    const updatedTheme = await response.json();
                    // Update theme details in the DOM
                    themeHeader.textContent = updatedTheme.name;
                    descriptionParagraph.textContent = updatedTheme.description;
                    // Remove form and revert to displaying theme details
                    form.remove();
                    themeHeader.classList.remove('hidden');
                    descriptionParagraph.classList.remove('hidden');
                } else {
                    throw new Error('Failed to update theme');
                }
            } catch (error) {
                console.error('Error updating theme:', error);
            }
        });

        form.appendChild(updateButton);

        // Hide theme details and display form
        themeHeader.classList.add('hidden');
        descriptionParagraph.classList.add('hidden');
        themeHeader.parentNode.insertBefore(form, themeHeader.nextSibling);
    }

    // Function to toggle edit form for a note
    async function toggleEditNote(note, noteDetailsElement) {
        const noteHeader = noteDetailsElement.previousElementSibling;
        if (!noteHeader) return;

        const currentTitle = noteHeader.textContent.trim();
        const currentText = noteDetailsElement.querySelector('p').textContent.trim();

        // Clear all previous opened forms
        document.querySelectorAll('.note-form').forEach(openForm=> {
            openForm.remove()
        })

        // Create form elements
        const form = document.createElement('form');
        form.classList.add('note-form');

        const titleInput = document.createElement('input');
        titleInput.classList.add('note-form--input')
        titleInput.type = 'text';
        titleInput.value = currentTitle;
        form.appendChild(titleInput);

        const textArea = document.createElement('textarea');
        textArea.classList.add('note-form--textarea')
        textArea.value = currentText;
        form.appendChild(textArea);

        const updateButton = document.createElement('button');
        updateButton.classList.add('note-form--button')
        updateButton.textContent = 'Update';
        updateButton.type = 'button';
        updateButton.addEventListener('click', async () => {
            try {
                const response = await fetch(`/api/archive/themes/${note.archive_theme_id}/notes/${note.id}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({
                        id: note.id,
                        archive_theme_id: note.archive_theme_id,
                        title: titleInput.value,
                        text: textArea.value
                    })
                });

                if (response.ok) {
                    const updatedNote = await response.json();
                    // Update note details in the DOM
                    noteHeader.textContent = updatedNote.title;
                    noteDetailsElement.querySelector('p').textContent = updatedNote.text;
                    // Remove form and revert to displaying note details
                    form.remove();
                    // Show actions div containing buttons
                    const actionsDiv = noteDetailsElement.querySelector('.actions');
                    if (actionsDiv) {
                        actionsDiv.classList.remove('hidden');
                    }
                    noteHeader.classList.remove('hidden');
                    noteDetailsElement.classList.remove('hidden');
                } else {
                    throw new Error('Failed to update note');
                }
            } catch (error) {
                console.error('Error updating note:', error);
            }
        });

        form.appendChild(updateButton);

        // Hide note details and display form
        noteHeader.classList.add('hidden');
        noteDetailsElement.classList.add('hidden');
        noteHeader.parentNode.insertBefore(form, noteHeader.nextSibling);
    }

    // Function to handle changing the theme of a note
    async function openChangeThemePopup(note) {
        const changeThemePopup = document.getElementById('change-theme-popup-archive');
        const themeList = document.getElementById('theme-list');

        // Clear any existing theme buttons
        themeList.innerHTML = '';

        try {
            const response = await fetch('/api/archive/themes', {
                method: 'GET',
                credentials: 'include'
            });

            if (response.ok) {
                const themes = await response.json();
                themes.forEach(theme => {
                    const themeButton = document.createElement('button');
                    themeButton.textContent = theme.name;
                    themeButton.addEventListener('click', async () => {
                        try {
                            const updateResponse = await fetch(`/api/archive/themes/${theme.id}/notes/${note.id}`, {
                                method: 'PATCH',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                credentials: 'include',
                                body: JSON.stringify({
                                    id: note.id,
                                    archive_theme_id: theme.id,
                                    title: note.title, // Keep the existing title
                                    text: note.text    // Keep the existing text
                                })
                            });

                            if (updateResponse.ok) {
                                // Delete note from current theme
                                const currentThemeElement = document.querySelector(`.theme[data-theme-id="${note.archive_theme_id}"]`);
                                if (currentThemeElement) {
                                    const currentNoteElement = currentThemeElement.querySelector(`.note[data-note-id="${note.id}"]`);
                                    if (currentNoteElement) {
                                        currentNoteElement.remove(); // Remove note from current theme
                                    }
                                }

                                note.archive_theme_id = theme.id;
                                const themeElement = document.querySelector(`.theme[data-theme-id="${theme.id}"]`);
                                if (themeElement) {
                                    const themeDetails = themeElement.querySelector('.theme--details');
                                    const noteElement = await createNoteElement(note); // Create updated note element
                                    themeDetails.appendChild(noteElement); // Append note to theme details
                                }

                                changeThemePopup.style.display = 'none'; // Close popup-archive
                            } else {
                                throw new Error('Failed to change theme for note');
                            }
                        } catch (error) {
                            console.error('Error updating note theme:', error);
                        }
                    });
                    themeList.appendChild(themeButton);
                });

                // Display the popup-archive
                changeThemePopup.style.display = 'flex';
            } else {
                throw new Error('Failed to fetch themes');
            }
        } catch (error) {
            console.error('Error fetching themes:', error);
        }
    }

    if (window.location.pathname.startsWith('/users/profile')) {
        await fetchThemes();
    }
});


document.addEventListener('DOMContentLoaded', async function() {
    const createNotePopup = document.getElementById('bookmark-create-note-popup-archive');
    const createNoteForm = document.getElementById('bookmark-create-note-form');
    const closeButton = document.querySelector('.popup-archive-close');
    const themeSelect = document.getElementById('bookmark-theme_id');

    document.querySelectorAll('.bookmark-button').forEach(button => {
        button.addEventListener('click', async function() {
            const itemType = button.getAttribute('itemType');
            const itemId = button.getAttribute('itemId');

            // Set hidden inputs
            createNoteForm.item_type.value = itemType;
            createNoteForm.item_id.value = itemId;

            // Fetch themes
            try {
                const response = await fetch('/api/archive/themes', {
                    method: 'GET',
                    credentials: 'include'
                });

                if (response.ok) {
                    const themes = await response.json();
                    themeSelect.innerHTML = ''; // Clear previous options

                    themes.forEach(theme => {
                        const option = document.createElement('option');
                        option.value = theme.id;
                        option.textContent = theme.name;
                        themeSelect.appendChild(option);
                    });
                } else {
                    throw new Error('Failed to fetch themes');
                }
            } catch (error) {
                console.error('Error fetching themes:', error);
            }

            // Show the popup
            createNotePopup.style.display = 'flex';
        });
    });

    // Handle form submission for creating a note
    if (createNotePopup) {
        createNoteForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const form = event.target;
            const themeId = form.theme_id.value;

            const note = {
                item_type: form.item_type.value,
                item_id: form.item_id.value,
                title: form.title.value,
                text: form.text.value,
                archive_theme_id: themeId
            };

            try {
                const response = await fetch(`/api/archive/themes/${themeId}/notes`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify(note)
                });

                if (response.ok) {
                    const createdNote = await response.json();

                    alert('Заметка создана');
                    createNotePopup.style.display = 'none';
                    form.reset();
                } else {
                    throw new Error('Failed to create note');
                }
            } catch (error) {
                console.error('Error creating note:', error);
            }
        });

        // Close the popup when the close button is clicked
        closeButton.addEventListener('click', () => {
            createNotePopup.style.display = 'none';
        });

        // Prevent closing the popup when clicking outside of it
        // TODO: Think if click outside should close popup window
        createNotePopup.addEventListener('click', (event) => {
            if (event.target === createNotePopup) {
                event.stopPropagation();
            }
        });
    }
});
