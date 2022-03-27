const hamburger = document.getElementById('hamburger');
const navContain = document.querySelector('.nav-container');
const navDropdown = document.querySelector('.nav-dropdown');
const searchButton = document.querySelector("#search-btn");
const searchEntry = document.querySelector('#search-entry');

// Function to validate search entry
const searchValidate = () => {
    if(searchEntry.value != '') {
        let searchText = searchEntry.value.toLowerCase();  
        let baseUrl = window.location.origin;
        window.location.replace(`${baseUrl}/search/${searchText}`);
    }
}

// Adding event listener on hamburger to show navbar
hamburger.addEventListener('click', (e) => {
    e.preventDefault();
    navDropdown.append(navContain);
    navContain.classList.toggle('drop');
});

// Event listener for search
searchButton.addEventListener('click', (e)  => {
    e.preventDefault();
    searchValidate();
});