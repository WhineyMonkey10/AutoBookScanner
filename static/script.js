var initialBooks = []; // Store the initial database in a JavaScript variable

// Function to filter and display cards based on the search query
function filterCards(searchQuery) {
  var cardContainer = document.querySelector('.card-container');
  var cards = cardContainer.querySelectorAll('.card');

  cards.forEach(function (card) {
    var title = card.querySelector('h3').textContent.toLowerCase();
    var author = card.querySelector('.author').textContent.toLowerCase();

    if (title.includes(searchQuery.toLowerCase()) || author.includes(searchQuery.toLowerCase())) {
      card.style.display = 'flex'; // Show the card if it matches the search query,
    } else {
      card.style.display = 'none'; // Hide the card if it doesn't match the search query
    }
  });
}

// Event listener for the search input field
var searchInput = document.querySelector('input[name="search_query"]');
searchInput.addEventListener('input', function () {
  var searchQuery = searchInput.value.trim();
  filterCards(searchQuery);
});

// Function to handle page load and initial setup
function handlePageLoad() {
  // Fetch the initial books data and store it in the 'initialBooks' variable
  fetch('/load_initial_books')
  .then(response => response.json())
  .then(data => {
    initialBooks = data;
    console.log('Initial books loaded:', initialBooks);
    filterCards(''); // Initially, show all books
  })
  .catch(error => console.error('Error loading initial books:', error));

  // Add event listener to the search input field
  searchInput.addEventListener('input', function () {
    var searchQuery = searchInput.value.trim();
    filterCards(searchQuery);
  });

  console.log('All scripts loaded!');
}

// Call the handlePageLoad function when the window has finished loading the page
window.onload = handlePageLoad;

// Add an event listener for clicking on a card
var cardContainer = document.querySelector('.card-container');
cardContainer.addEventListener('click', function (event) {
  var card = event.target.closest('.card'); // Find the closest parent with the 'card' class

  if (card) {
    var cardISBN = card.getAttribute('data-book-id');
    console.log(cardISBN);
    if (cardISBN) {
      window.location.href = '/book/' + cardISBN;
    }
    console.log('Clicked on a card!');
  }
});
